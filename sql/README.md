# Modelo físico PostgreSQL

Se incluye el DDL **íntegro** del Capítulo IV 4.6: esquema `alquiler`, 10 tablas, 54 atributos, PK/FK, CHECK, UNIQUE, DEFAULT y 8 índices auxiliares.

`01_esquema_alquiler.sql` se aplica **automáticamente y una única vez**, cuando Docker inicializa un volumen de datos vacío. No se debe ejecutar nuevamente sobre una base donde ya existan las tablas.

Las pruebas `02_pruebas_integridad.sql` validan 7 restricciones y hacen `ROLLBACK`. Opcionalmente puedes cargar `03_catalogo_comodidades_opcional.sql` para disponer de comodidades de ejemplo. Ejecútalas manualmente con:

```bash
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/02_pruebas_integridad.sql
# Catálogo opcional:
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/03_catalogo_comodidades_opcional.sql
```

**No ejecutes `DROP`, `down -v` ni estos scripts en otras bases de datos.** Las reglas de roles administrativos y propiedad se validan también en servicios FastAPI; las FK por sí solas no verifican roles.
