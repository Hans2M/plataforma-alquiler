-- ================================================================
-- MEJORA 4.7 | PERFIL DE CONVIVENCIA CON DATOS TIPADOS
-- Plataforma Web de Alquiler de Alojamientos
--
-- Objetivo: dejar de guardar "habitos" y "preferencias" como texto
-- libre y modelarlos con catalogos reutilizables, ademas de agregar
-- campos tipados (fuma, mascotas, horario, orden, ocupacion, genero,
-- edad) que permitan filtrar y calcular compatibilidad.
--
-- Compatibilidad: las columnas de texto heredadas (habitos,
-- preferencias) se conservan para no romper datos ni clientes previos.
--
-- Idempotente: puede ejecutarse sobre una base ya creada.
-- Aplicar despues de 01_esquema_alquiler.sql:
--   docker compose exec -T db psql -v ON_ERROR_STOP=1 \
--     -U alquiler_app -d alquiler_db < sql/04_mejoras_perfil_convivencia.sql
-- ================================================================

BEGIN;

-- 1. Catalogos de habitos (pasatiempos y rutinas) y preferencias.
CREATE TABLE IF NOT EXISTS alquiler.catalogo_habitos (
    habito_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre    VARCHAR(80) NOT NULL UNIQUE,
    categoria VARCHAR(30) NOT NULL DEFAULT 'convivencia',
    orden     SMALLINT    NOT NULL DEFAULT 0,
    activo    BOOLEAN     NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_catalogo_habitos_nombre
        CHECK (LENGTH(BTRIM(nombre)) > 0),
    CONSTRAINT ck_catalogo_habitos_categoria
        CHECK (categoria IN ('convivencia', 'rutina', 'ocio'))
);

CREATE TABLE IF NOT EXISTS alquiler.catalogo_preferencias (
    preferencia_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL UNIQUE,
    categoria      VARCHAR(30)  NOT NULL DEFAULT 'convivencia',
    orden          SMALLINT     NOT NULL DEFAULT 0,
    activo         BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_catalogo_preferencias_nombre
        CHECK (LENGTH(BTRIM(nombre)) > 0),
    CONSTRAINT ck_catalogo_preferencias_categoria
        CHECK (categoria IN ('convivencia', 'perfil'))
);

-- 2. Relaciones M:N entre perfiles y catalogos.
CREATE TABLE IF NOT EXISTS alquiler.perfil_habitos (
    perfil_id BIGINT   NOT NULL,
    habito_id SMALLINT NOT NULL,
    CONSTRAINT pk_perfil_habitos PRIMARY KEY (perfil_id, habito_id),
    CONSTRAINT fk_perfil_habitos_perfil FOREIGN KEY (perfil_id)
        REFERENCES alquiler.perfiles_companero(perfil_id) ON DELETE CASCADE,
    CONSTRAINT fk_perfil_habitos_habito FOREIGN KEY (habito_id)
        REFERENCES alquiler.catalogo_habitos(habito_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS alquiler.perfil_preferencias (
    perfil_id      BIGINT   NOT NULL,
    preferencia_id SMALLINT NOT NULL,
    CONSTRAINT pk_perfil_preferencias PRIMARY KEY (perfil_id, preferencia_id),
    CONSTRAINT fk_perfil_preferencias_perfil FOREIGN KEY (perfil_id)
        REFERENCES alquiler.perfiles_companero(perfil_id) ON DELETE CASCADE,
    CONSTRAINT fk_perfil_preferencias_preferencia FOREIGN KEY (preferencia_id)
        REFERENCES alquiler.catalogo_preferencias(preferencia_id) ON DELETE RESTRICT
);

-- 3. Campos tipados del perfil (todos opcionales para no romper datos previos).
ALTER TABLE alquiler.perfiles_companero
    ADD COLUMN IF NOT EXISTS fuma             BOOLEAN,
    ADD COLUMN IF NOT EXISTS tiene_mascotas   BOOLEAN,
    ADD COLUMN IF NOT EXISTS horario          VARCHAR(15),
    ADD COLUMN IF NOT EXISTS nivel_orden      SMALLINT,
    ADD COLUMN IF NOT EXISTS ocupacion        VARCHAR(15),
    ADD COLUMN IF NOT EXISTS genero           VARCHAR(20),
    ADD COLUMN IF NOT EXISTS genero_preferido VARCHAR(20),
    ADD COLUMN IF NOT EXISTS edad             SMALLINT,
    ADD COLUMN IF NOT EXISTS actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- 4. Restricciones de dominio (idempotentes).
DO $restricciones$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_horario'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_horario
            CHECK (horario IS NULL OR horario IN ('temprano', 'tarde', 'nocturno', 'flexible'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_nivel_orden'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_nivel_orden
            CHECK (nivel_orden IS NULL OR nivel_orden BETWEEN 1 AND 5);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_ocupacion'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_ocupacion
            CHECK (ocupacion IS NULL OR ocupacion IN ('estudiante', 'trabajador', 'ambos', 'otro'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_genero'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_genero
            CHECK (genero IS NULL OR genero IN ('femenino', 'masculino', 'otro', 'prefiero_no_decir'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_genero_preferido'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_genero_preferido
            CHECK (genero_preferido IS NULL OR genero_preferido IN ('femenino', 'masculino', 'mixto', 'indiferente'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_edad'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_edad
            CHECK (edad IS NULL OR edad BETWEEN 18 AND 99);
    END IF;

    -- NOT VALID: protege escrituras nuevas sin fallar si hubiera filas
    -- antiguas con descripciones fuera del rango.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_perfiles_descripcion'
    ) THEN
        ALTER TABLE alquiler.perfiles_companero
            ADD CONSTRAINT ck_perfiles_descripcion
            CHECK (
                descripcion IS NULL
                OR LENGTH(BTRIM(descripcion)) BETWEEN 10 AND 500
            ) NOT VALID;
    END IF;
END
$restricciones$;

-- 5. Indices para consultas por catalogo.
CREATE INDEX IF NOT EXISTS idx_perfil_habitos_habito
    ON alquiler.perfil_habitos (habito_id);
CREATE INDEX IF NOT EXISTS idx_perfil_preferencias_preferencia
    ON alquiler.perfil_preferencias (preferencia_id);

-- 6. Datos de referencia (repetible, no duplica por nombre).
INSERT INTO alquiler.catalogo_habitos (nombre, categoria, orden) VALUES
    ('No fumo',                  'convivencia', 10),
    ('Fumo ocasionalmente',      'convivencia', 20),
    ('Tengo mascotas',           'convivencia', 30),
    ('No tengo mascotas',        'convivencia', 40),
    ('Soy ordenado/a',           'convivencia', 50),
    ('Prefiero el silencio',     'convivencia', 60),
    ('Soy sociable',             'convivencia', 70),
    ('Madrugo',                  'rutina',      10),
    ('Trabajo de día',           'rutina',      20),
    ('Estudio de noche',         'rutina',      30),
    ('Duermo temprano',          'rutina',      40),
    ('Soy flexible con horarios','rutina',      50),
    ('Hago deporte',             'ocio',        10),
    ('Leo',                      'ocio',        20),
    ('Veo series o películas',   'ocio',        30),
    ('Escucho música',           'ocio',        40),
    ('Cocino',                   'ocio',        50),
    ('Juego videojuegos',        'ocio',        60),
    ('Salgo con amigos',         'ocio',        70)
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO alquiler.catalogo_preferencias (nombre, categoria, orden) VALUES
    ('Ambiente tranquilo',       'convivencia', 10),
    ('Ambiente sociable',        'convivencia', 20),
    ('Respeto por el descanso',  'convivencia', 30),
    ('Buena comunicación',       'convivencia', 40),
    ('Limpieza compartida',      'convivencia', 50),
    ('No fumar en casa',         'convivencia', 60),
    ('Aceptar mascotas',         'convivencia', 70),
    ('No aceptar mascotas',      'convivencia', 80),
    ('Compañero estudiante',     'perfil',      10),
    ('Compañero trabajador',     'perfil',      20)
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
