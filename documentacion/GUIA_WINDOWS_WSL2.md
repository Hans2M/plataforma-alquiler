# Ejecutar en Windows 11 y WSL2

En Visual Studio Code puedes abrir la carpeta desde WSL2 para trabajar con el proyecto y usar una terminal Bash.

```bash
cp .env.example .env
# Editar .env y establecer claves fuertes
code .
docker compose up --build -d
docker compose ps
docker compose logs -f backend
```

Si usas **PowerShell**, copia variables con `Copy-Item .env.example .env` y ejecuta desde esa misma carpeta `docker compose up --build -d`.

En **PowerShell**, para aplicar un SQL desde stdin utiliza:

```powershell
Get-Content -Raw .\sql\02_pruebas_integridad.sql | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db
```

Los comandos con `< sql/archivo.sql` de README están destinados a Bash/WSL2. Los nombres `alquiler_app` / `alquiler_db` deben cambiarse si editas esas variables en `.env`.

El servicio PostgreSQL de este Compose no expone 5432/5433 al host y no debe conectarse a `postgres_db` ni a una base `prueba_1` de otros trabajos.
