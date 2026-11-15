-- ================================================================
-- CAPITULO IV - 4.6 | MODELO FISICO POSTGRESQL
-- PLATAFORMA WEB DE ALQUILER DE ALOJAMIENTOS
-- Version academica 1.0 | 10 tablas, 55 columnas
-- EJECUTAR UNICAMENTE EN UNA BASE DE DATOS DE PRUEBA INDEPENDIENTE.
-- No contiene DROP ni modifica las bases de datos preexistentes.
-- No vuelve a ejecutarse sobre el mismo esquema ya creado.
-- ================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS alquiler;

-- 1. Cuentas generales: buscador, arrendador, administrador.
CREATE TABLE alquiler.usuarios (
    usuario_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_completo  VARCHAR(150) NOT NULL,
    correo           VARCHAR(180) NOT NULL UNIQUE,
    clave_hash       VARCHAR(255) NOT NULL,
    rol              VARCHAR(20)  NOT NULL,
    estado_cuenta    VARCHAR(20)  NOT NULL DEFAULT 'pendiente',
    telefono         VARCHAR(25),
    tipo_documento   VARCHAR(20),
    numero_documento VARCHAR(25) UNIQUE,
    foto_perfil      VARCHAR(255),
    fecha_registro   TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_usuarios_nombre_no_vacio
        CHECK (LENGTH(BTRIM(nombre_completo)) > 0),
    CONSTRAINT ck_usuarios_correo_no_vacio
        CHECK (LENGTH(BTRIM(correo)) > 0),
    CONSTRAINT ck_usuarios_rol
        CHECK (rol IN ('buscador', 'arrendador', 'administrador')),
    CONSTRAINT ck_usuarios_estado_cuenta
        CHECK (estado_cuenta IN ('pendiente', 'verificada', 'suspendida'))
);

-- 2. Datos especificos del rol buscador (PK compartida con usuarios).
CREATE TABLE alquiler.buscadores (
    usuario_id BIGINT PRIMARY KEY,
    CONSTRAINT fk_buscadores_usuario FOREIGN KEY (usuario_id)
        REFERENCES alquiler.usuarios(usuario_id) ON DELETE RESTRICT
);

-- 3. Datos especificos del rol arrendador (PK compartida con usuarios).
CREATE TABLE alquiler.arrendadores (
    usuario_id BIGINT PRIMARY KEY,
    ruc        VARCHAR(11) UNIQUE,
    CONSTRAINT fk_arrendadores_usuario FOREIGN KEY (usuario_id)
        REFERENCES alquiler.usuarios(usuario_id) ON DELETE RESTRICT,
    CONSTRAINT ck_arrendadores_ruc_formato
        CHECK (ruc IS NULL OR ruc ~ '^[0-9]{11}$')
);

-- 4. Publicaciones de alquiler.
CREATE TABLE alquiler.alojamientos (
    alojamiento_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arrendador_id     BIGINT        NOT NULL,
    titulo            VARCHAR(150)  NOT NULL,
    descripcion       TEXT          NOT NULL,
    precio            NUMERIC(12,2) NOT NULL,
    direccion         VARCHAR(250)  NOT NULL,
    distrito          VARCHAR(100)  NOT NULL,
    tipo              VARCHAR(40)   NOT NULL,
    estado            VARCHAR(20)   NOT NULL DEFAULT 'activo',
    destacado         BOOLEAN       NOT NULL DEFAULT FALSE,
    fecha_publicacion TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alojamientos_arrendador FOREIGN KEY (arrendador_id)
        REFERENCES alquiler.arrendadores(usuario_id) ON DELETE RESTRICT,
    CONSTRAINT ck_alojamientos_precio CHECK (precio > 0),
    CONSTRAINT ck_alojamientos_estado
        CHECK (estado IN ('activo', 'inactivo', 'alquilado'))
);

-- 5. Catalogo de comodidades sin listas multivaluadas.
CREATE TABLE alquiler.comodidades (
    comodidad_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT ck_comodidades_nombre_no_vacio
        CHECK (LENGTH(BTRIM(nombre)) > 0)
);

-- 6. Resolucion de la relacion muchos a muchos.
CREATE TABLE alquiler.alojamiento_comodidades (
    alojamiento_id BIGINT NOT NULL,
    comodidad_id   BIGINT NOT NULL,
    CONSTRAINT pk_alojamiento_comodidades
        PRIMARY KEY (alojamiento_id, comodidad_id),
    CONSTRAINT fk_ac_alojamiento FOREIGN KEY (alojamiento_id)
        REFERENCES alquiler.alojamientos(alojamiento_id) ON DELETE CASCADE,
    CONSTRAINT fk_ac_comodidad FOREIGN KEY (comodidad_id)
        REFERENCES alquiler.comodidades(comodidad_id) ON DELETE RESTRICT
);

-- 7. Solo referencias a archivos, no imagenes binarias.
CREATE TABLE alquiler.imagenes_alojamiento (
    imagen_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alojamiento_id BIGINT  NOT NULL,
    ruta_archivo   TEXT    NOT NULL,
    orden          INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT fk_imagenes_alojamiento FOREIGN KEY (alojamiento_id)
        REFERENCES alquiler.alojamientos(alojamiento_id) ON DELETE CASCADE,
    CONSTRAINT ck_imagenes_orden CHECK (orden >= 0),
    CONSTRAINT ck_imagenes_ruta_no_vacia
        CHECK (LENGTH(BTRIM(ruta_archivo)) > 0)
);

-- 8. Maximo un perfil de convivencia por buscador.
CREATE TABLE alquiler.perfiles_companero (
    perfil_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    buscador_id     BIGINT        NOT NULL UNIQUE,
    presupuesto_min NUMERIC(12,2) NOT NULL,
    presupuesto_max NUMERIC(12,2) NOT NULL,
    habitos         TEXT,
    preferencias    TEXT,
    descripcion     TEXT,
    estado          VARCHAR(15)  NOT NULL DEFAULT 'activo',
    CONSTRAINT fk_perfiles_buscador FOREIGN KEY (buscador_id)
        REFERENCES alquiler.buscadores(usuario_id) ON DELETE RESTRICT,
    CONSTRAINT ck_perfiles_presupuesto
        CHECK (presupuesto_min >= 0 AND presupuesto_max >= presupuesto_min),
    CONSTRAINT ck_perfiles_estado
        CHECK (estado IN ('activo', 'inactivo'))
);

-- 9. Solicitudes de verificacion: el revisor tambien es un usuario.
CREATE TABLE alquiler.verificaciones_identidad (
    verificacion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      BIGINT      NOT NULL,
    ruta_documento  TEXT        NOT NULL,
    estado          VARCHAR(15) NOT NULL DEFAULT 'pendiente',
    fecha_solicitud TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revisor_id      BIGINT,
    fecha_revision  TIMESTAMPTZ,
    observacion     TEXT,
    CONSTRAINT fk_verificaciones_solicitante FOREIGN KEY (usuario_id)
        REFERENCES alquiler.usuarios(usuario_id) ON DELETE RESTRICT,
    CONSTRAINT fk_verificaciones_revisor FOREIGN KEY (revisor_id)
        REFERENCES alquiler.usuarios(usuario_id) ON DELETE RESTRICT,
    CONSTRAINT ck_verificaciones_estado
        CHECK (estado IN ('pendiente', 'aprobada', 'rechazada')),
    CONSTRAINT ck_verificaciones_ruta_no_vacia
        CHECK (LENGTH(BTRIM(ruta_documento)) > 0),
    CONSTRAINT ck_verificaciones_revision
        CHECK (
            (estado = 'pendiente' AND revisor_id IS NULL AND fecha_revision IS NULL)
            OR
            (estado IN ('aprobada', 'rechazada')
             AND revisor_id IS NOT NULL AND fecha_revision IS NOT NULL
             AND fecha_revision >= fecha_solicitud)
        )
);

-- 10. Historial de acceso; no debe editarse desde la UI ordinaria.
CREATE TABLE alquiler.registros_acceso (
    registro_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id  BIGINT      NOT NULL,
    accion      VARCHAR(40) NOT NULL,
    fecha_hora  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip          VARCHAR(45),
    dispositivo TEXT,
    CONSTRAINT fk_registros_usuario FOREIGN KEY (usuario_id)
        REFERENCES alquiler.usuarios(usuario_id) ON DELETE RESTRICT,
    CONSTRAINT ck_registros_accion
        CHECK (accion IN ('registro', 'inicio_sesion',
                         'cierre_sesion', 'eliminacion_cuenta'))
);

-- Indices adicionales para consultas y JOIN frecuentes.
-- PK y UNIQUE ya generan indices automaticamente.
CREATE INDEX idx_alojamientos_busqueda
    ON alquiler.alojamientos (estado, distrito, precio);
CREATE INDEX idx_alojamientos_arrendador
    ON alquiler.alojamientos (arrendador_id);
CREATE INDEX idx_imagenes_alojamiento_orden
    ON alquiler.imagenes_alojamiento (alojamiento_id, orden);
CREATE INDEX idx_ac_comodidad
    ON alquiler.alojamiento_comodidades (comodidad_id);
CREATE INDEX idx_verificaciones_estado_fecha
    ON alquiler.verificaciones_identidad (estado, fecha_solicitud);
CREATE INDEX idx_verificaciones_usuario
    ON alquiler.verificaciones_identidad (usuario_id);
CREATE INDEX idx_verificaciones_revisor
    ON alquiler.verificaciones_identidad (revisor_id);
CREATE INDEX idx_registros_usuario_fecha
    ON alquiler.registros_acceso (usuario_id, fecha_hora DESC);

COMMIT;

-- NOTAS DE ALCANCE:
-- 1. Solo deben existir filas en buscadores para usuarios con rol 'buscador'
--    y en arrendadores para usuarios con rol 'arrendador'. Esta regla
--    NO queda garantizada por la FK, se valida desde FastAPI.
-- 2. revisor_id debe pertenecer a un usuario administrador: se valida
--    en la logica de servicios, no por la FK a usuarios.
-- 3. El DDL no impide editar verificaciones finalizadas: FastAPI debe
--    bloquear la segunda revision, idealmente con transaccion y bloqueo.
-- 4. UNIQUE de correo y documentos es sensible a mayusculas/cadena exacta;
--    normalizar correo en API antes de almacenar y consultar.
-- 5. ON DELETE CASCADE elimina registros de IMAGENES_ALOJAMIENTO y AC,
--    pero NO borra los archivos fisicos u objetos externos.
-- 6. DELETE de usuarios con historial/verificaciones puede quedar
--    bloqueado por FK RESTRICT: definir un flujo de eliminacion/retencion.
-- 7. El DDL usa exactamente los 54 atributos del diccionario de 4.5.
