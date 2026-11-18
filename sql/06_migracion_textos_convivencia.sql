-- ================================================================
-- MEJORA 6 | MIGRACION DE TEXTOS HISTORICOS A CATALOGOS
-- Plataforma Web de Alquiler de Alojamientos
--
-- Objetivo: completar los catalogos estructurados a partir de los
-- campos de texto libre que ya existian en perfiles_companero
-- (habitos y preferencias). No borra ni modifica el texto original:
-- lo conserva como respaldo y solo agrega filas en perfil_habitos y
-- perfil_preferencias cuando reconoce una frase conocida.
--
-- Idempotente: puede ejecutarse varias veces sin duplicar filas.
-- Aplicar despues de 04 y 05:
--   docker compose exec -T db psql -v ON_ERROR_STOP=1 \
--     -U alquiler_app -d alquiler_db < sql/06_migracion_textos_convivencia.sql
-- ================================================================

BEGIN;

-- ----------------------------------------------------------------
-- 1. Habitos y pasatiempos reconocidos en el texto libre
-- ----------------------------------------------------------------
WITH mapa(patron, habito, exclusion) AS (
    VALUES
        ('%no fum%',                'No fumo',                    NULL),
        ('%fum%',                   'Fumo ocasionalmente',        '%no fum%'),
        ('%no tengo mascota%',      'No tengo mascotas',          NULL),
        ('%mascota%',               'Tengo mascotas',             '%no tengo mascota%'),
        ('%ordenad%',               'Soy ordenado/a',             NULL),
        ('%silencio%',              'Prefiero el silencio',       NULL),
        ('%sociable%',              'Soy sociable',               NULL),
        ('%madrug%',                'Madrugo',                    NULL),
        ('%trabajo de d%',          'Trabajo de día',             NULL),
        ('%estudio de noche%',      'Estudio de noche',           NULL),
        ('%deport%',                'Hago deporte',               NULL),
        ('%cocin%',                 'Cocino',                     NULL),
        ('%serie%',                 'Veo series o películas',     NULL),
        ('%pelicul%',               'Veo series o películas',     NULL),
        ('%música%',                'Escucho música',             NULL),
        ('%musica%',                'Escucho música',             NULL),
        ('%videojuego%',            'Juego videojuegos',          NULL),
        ('%salgo con amigos%',      'Salgo con amigos',           NULL),
        ('%flexible%',              'Soy flexible con horarios',  NULL)
)
INSERT INTO alquiler.perfil_habitos (perfil_id, habito_id)
SELECT DISTINCT p.perfil_id, h.habito_id
FROM alquiler.perfiles_companero p
JOIN mapa m ON p.habitos ILIKE m.patron
           AND (m.exclusion IS NULL OR p.habitos NOT ILIKE m.exclusion)
JOIN alquiler.catalogo_habitos h ON h.nombre = m.habito
ON CONFLICT DO NOTHING;

-- Casos con palabra completa: evita falsos positivos como "lejos".
INSERT INTO alquiler.perfil_habitos (perfil_id, habito_id)
SELECT DISTINCT p.perfil_id, h.habito_id
FROM alquiler.perfiles_companero p
JOIN alquiler.catalogo_habitos h ON h.nombre = 'Leo'
WHERE p.habitos ~* '\m(leo|leer|leemos|lectura|lecturas|libros?)\M'
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------
-- 2. Preferencias de convivencia reconocidas en el texto libre
-- ----------------------------------------------------------------
WITH mapa(patron, preferencia, exclusion) AS (
    VALUES
        ('%tranquil%',              'Ambiente tranquilo',         NULL),
        ('%sociable%',              'Ambiente sociable',          NULL),
        ('%descanso%',              'Respeto por el descanso',    NULL),
        ('%comunicaci%',            'Buena comunicación',         NULL),
        ('%limp%',                  'Limpieza compartida',        NULL),
        ('%no fumar%',              'No fumar en casa',           NULL),
        ('%no aceptar mascota%',    'No aceptar mascotas',        NULL),
        ('%mascota%',               'Aceptar mascotas',           '%no aceptar mascota%'),
        ('%estudiante%',            'Compañero estudiante',       NULL),
        ('%trabajador%',            'Compañero trabajador',       NULL)
)
INSERT INTO alquiler.perfil_preferencias (perfil_id, preferencia_id)
SELECT DISTINCT p.perfil_id, c.preferencia_id
FROM alquiler.perfiles_companero p
JOIN mapa m ON p.preferencias ILIKE m.patron
           AND (m.exclusion IS NULL OR p.preferencias NOT ILIKE m.exclusion)
JOIN alquiler.catalogo_preferencias c ON c.nombre = m.preferencia
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------
-- 3. Resumen de la migracion
-- ----------------------------------------------------------------
DO $resumen$
DECLARE
    v_perfiles        INTEGER;
    v_con_habitos     INTEGER;
    v_con_preferencias INTEGER;
    v_alojamientos    INTEGER;
    v_sin_distrito    INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_perfiles FROM alquiler.perfiles_companero;
    SELECT COUNT(DISTINCT perfil_id) INTO v_con_habitos
        FROM alquiler.perfil_habitos;
    SELECT COUNT(DISTINCT perfil_id) INTO v_con_preferencias
        FROM alquiler.perfil_preferencias;
    SELECT COUNT(*) INTO v_alojamientos FROM alquiler.alojamientos;
    SELECT COUNT(*) INTO v_sin_distrito
        FROM alquiler.alojamientos WHERE distrito_id IS NULL;

    RAISE NOTICE 'Perfiles: %, con habitos estructurados: %, con preferencias: %',
        v_perfiles, v_con_habitos, v_con_preferencias;
    RAISE NOTICE 'Alojamientos: %, sin distrito_id (texto no reconocido): %',
        v_alojamientos, v_sin_distrito;
END
$resumen$;

COMMIT;
