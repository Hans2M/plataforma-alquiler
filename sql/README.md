# Modelo físico PostgreSQL

Se incluye el DDL **íntegro** del Capítulo IV 4.6: esquema `alquiler`, 10 tablas, 54 atributos, PK/FK, CHECK, UNIQUE, DEFAULT y 8 índices auxiliares. La mejora `04` añade 4 tablas (2 catálogos y 2 asociaciones M:N) y 9 columnas al perfil de convivencia, sin alterar las 10 tablas originales ni sus columnas existentes. Las mejoras `05` y `06` añaden UBIGEO, catálogos administrables y la migración de textos heredados, también de forma aditiva.

`01_esquema_alquiler.sql` se aplica **automáticamente y una única vez**, cuando Docker inicializa un volumen de datos vacío. No se debe ejecutar nuevamente sobre una base donde ya existan las tablas.

Las pruebas `02_pruebas_integridad.sql` validan 7 restricciones y hacen `ROLLBACK`. Opcionalmente puedes cargar `03_catalogo_comodidades_opcional.sql` para disponer de comodidades de ejemplo.

`04_mejoras_perfil_convivencia.sql` es una **mejora aditiva e idempotente** del perfil de convivencia: agrega los catálogos `catalogo_habitos` y `catalogo_preferencias`, las tablas puente `perfil_habitos` y `perfil_preferencias`, campos tipados (`fuma`, `tiene_mascotas`, `horario`, `nivel_orden`, `ocupacion`, `genero`, `genero_preferido`, `edad`) y sus `CHECK`. Conserva las columnas de texto `habitos` y `preferencias` para no romper datos ni clientes previos.

`05_ubigeo_y_catalogos.sql` normaliza la ubicación y convierte los valores fijos en catálogos editables:

- `ubigeo_departamentos` → `ubigeo_provincias` → `ubigeo_distritos` con los datos oficiales del INEI 2026 (25 departamentos, 196 provincias y 1892 distritos).
- `alojamientos.distrito_id` y `perfiles_companero.distrito_id` como FK al distrito; las columnas de texto se conservan como respaldo.
- `tipos_alojamiento` y `catalogo_estados` con nombre, descripción, orden y visibilidad editables desde la administración.
- Columnas de dominio generadas y FK compuestas para reforzar los estados; índices para búsquedas por distrito y departamento.
- Relleno de `tipo_id` y `distrito_id` en datos existentes cuando el texto coincide de forma única.

`06_migracion_textos_convivencia.sql` completa los catálogos estructurados a partir de los textos heredados `habitos` y `preferencias`. Es idempotente y **no modifica el texto original**: solo agrega coincidencias reconocidas en las tablas puente. Los textos no reconocidos permanecen intactos como respaldo.

Ejecuta las mejoras manualmente sobre una base existente con:

```bash
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/02_pruebas_integridad.sql
# Catálogo opcional:
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/03_catalogo_comodidades_opcional.sql
# Perfil de convivencia (repetible):
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/04_mejoras_perfil_convivencia.sql
# UBIGEO y catálogos administrables (repetible):
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/05_ubigeo_y_catalogos.sql
# Migración de textos heredados (repetible):
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/06_migracion_textos_convivencia.sql
```

Con un volumen nuevo, `01`, `04`, `05` y `06` se aplican automáticamente al inicializar PostgreSQL (están montados en `docker-entrypoint-initdb.d`).

**No ejecutes `DROP`, `down -v` ni estos scripts en otras bases de datos.** Las reglas de roles administrativos y propiedad se validan también en servicios FastAPI; las FK por sí solas no verifican roles.
