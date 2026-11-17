# Plataforma Web de Gestión y Búsqueda de Alojamientos

**Proyecto académico: Diseño Detallado de Software — 2026-II**  
**Tecnologías:** React + JavaScript (Vite), Python + FastAPI, SQLAlchemy, PostgreSQL 17, Docker Compose.  
**Arquitectura:** monolito modular en capas: presentación → API → servicios → repositorios → modelos → PostgreSQL.

> **Estado: código base funcional de demostración, NO producto listo para producción.** Se entrega un andamiaje ejecutable con endpoints y pantallas básicas. Algunas funciones de los 30 RF / 30 RNF están solo parcialmente implementadas o pendientes. El propósito es facilitar la implementación del informe sin afirmar capacidades no construidas.

## 1. Propósito y personas usuarias

El sistema está dirigido al **público general**. Un **visitante** puede buscar y consultar alojamientos activos sin registrarse. Un **buscador** puede registrarse, gestionar su perfil, consultar coincidencias de convivencia y solicitar verificación de identidad. Un **arrendador** puede publicar y administrar sus inmuebles; además puede explorar el catálogo público para comparar el mercado, sin acceder a los datos de contacto de otras publicaciones. El **administrador** gestiona cuentas y decide sobre solicitudes de identidad. No hay pagos, reservas ni contratos digitales.

## 2. Antes de comenzar

- Docker Desktop con Docker Compose habilitado (Windows 11 o Linux/WSL2).
- No necesitas instalar Python, Node ni PostgreSQL en el equipo para la ejecución con Docker.
- Utiliza una **carpeta de proyecto independiente**: este Compose crea sus propios contenedores y volúmenes; **no modifica `postgres_db`, `prueba_1` ni otras bases**.

### Levantar en Docker

1. Copia `.env.example` a `.env`. En PowerShell: `Copy-Item .env.example .env`; en Linux/WSL: `cp .env.example .env`.
2. Edita `.env` y cambia `POSTGRES_PASSWORD` y `SECRET_KEY` por valores aleatorios fuertes; no los subas a Git.
3. Desde la raíz ejecuta:

   ```bash
   docker compose up --build -d
   docker compose ps
   ```

4. Abre **http://localhost:5173** (frontend) y **http://localhost:8000/docs** (Swagger API). La comprobación de salud: **http://localhost:8000/api/salud**.
5. El DDL PostgreSQL se aplica automáticamente cuando arranca **por primera vez** un volumen vacío. El esquema es `alquiler`.
6. Para el rol administrador, ejecuta el asistente interactivo:

   ```bash
   docker compose exec backend python -m scripts.crear_admin
   ```

7. Registra un buscador y un arrendador desde la web; entra con cada cuenta para probar sus paneles.
8. Opcionalmente, carga los datos de demostración (arrendador con fotos y buscadores con coincidencias compatibles):

   ```bash
   docker compose exec backend python -m scripts.crear_demo
   ```

   | Cuenta | Correo | Contraseña |
   |---|---|---|
   | Arrendador | `arrendador.demo@example.com` | `DemoSegura123` |
   | Buscador principal | `buscador.demo@example.com` | `DemoSegura123` |
   | Compañero compatible 1 | `companero1.demo@example.com` | `DemoSegura123` |
   | Compañero compatible 2 | `companero2.demo@example.com` | `DemoSegura123` |

   Ingresa como **buscador principal** y abre **Compartir vivienda** para ver el resumen del perfil, las coincidencias y los botones de WhatsApp. El script es idempotente: restaura los perfiles canónicos y regenera las fotos de demostración sin duplicar cuentas ni publicaciones.

### Ver la demo desde otro dispositivo con ngrok

Con los tres servicios levantados, configura tu token personal de ngrok **una sola vez** (no lo guardes en el repositorio) y abre un túnel al frontend:

```bash
ngrok config add-authtoken TU_TOKEN_PERSONAL
ngrok http 5173
```

ngrok mostrará una URL pública `https://...ngrok-free.app`. Ábrela desde el otro dispositivo y pulsa **Visit Site** la primera vez; es el aviso antiabuso de la cuenta gratuita. El frontend reenvía `/api` al backend dentro de la red Docker, así que no hace falta abrir el puerto 8000.

> La URL gratuita cambia cada vez que reinicias ngrok. Cualquier persona con el enlace puede acceder mientras el túnel esté activo: úsalo solo con datos de demostración y cierra el proceso al terminar.

### Detener sin perder datos

```bash
docker compose down
```

**NO uses `docker compose down -v`**, ya que elimina los volúmenes de PostgreSQL y archivos. No se publica el puerto de PostgreSQL en el anfitrión; solo es accesible desde los servicios de la red interna. Esto evita colisiones con instalaciones existentes en `5432` o `5433`.

### Ver logs y acceso SQL

```bash
docker compose logs -f backend
docker compose exec db psql -U alquiler_app -d alquiler_db
# Dentro de psql:
\dt alquiler.*
SELECT COUNT(*) FROM alquiler.usuarios;
\q
```

Para verificar las restricciones de integridad (ROLLBACK sin persistencia de datos):

```bash
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/02_pruebas_integridad.sql
```

## 3. Estructura del proyecto

```text
PLATAFORMA_ALQUILER/
├── README.md                        # Instalación, requerimientos, pruebas y pendientes
├── .env.example                     # Ejemplo de variables de entorno
├── .gitignore / .dockerignore       # Exclusiones del repositorio y las imágenes
├── compose.yaml                     # Servicios frontend, backend, db; volúmenes y red
├── sql/
│   ├── 01_esquema_alquiler.sql       # DDL íntegro, 10 tablas, 54 campos y 8 índices
│   ├── 02_pruebas_integridad.sql     # 7 verificaciones de reglas SQL
│   └── 03_catalogo_comodidades_opcional.sql  # Referencias de demostración
├── frontend/
│   ├── Dockerfile, package.json, vite.config.js, index.html
│   ├── App.jsx, main.jsx            # Punto de entrada y estado básico de sesión
│   ├── componentes/
│   │   ├── autenticacion/           # Componentes de formulario reutilizables (por ampliar)
│   │   ├── alojamientos/            # Tarjetas y listas
│   │   ├── companeros/              # Por ampliar
│   │   ├── administracion/          # Por ampliar
│   │   └── comunes/                 # Encabezado y mensajes
│   ├── paginas/
│   │   ├── autenticacion/           # Login y registro
│   │   ├── buscador/                # Búsqueda, panel, convivencia, verificación
│   │   ├── arrendador/              # Publicar y administrar alojamiento
│   │   └── administrador/           # Cuentas y revisión de DNI
│   ├── servicios/                   # Cliente fetch con token Bearer
│   ├── rutas/                       # Protección básica de rutas React
│   └── recursos/                    # CSS y logo
├── backend/
│   ├── Dockerfile, requirements.txt, main.py
│   ├── dominio/                     # Errores de negocio y puertos (Protocol) del dominio
│   ├── api/                         # Rutas REST por módulo
│   │   └── dependencias.py          # Composición de repositorios y servicios (inyección)
│   ├── servicios/                   # Reglas de negocio (sin FastAPI ni commit)
│   ├── repositorios/                # Adaptadores SQLAlchemy de los puertos
│   ├── modelos/                     # Mapeos de las diez tablas del MER
│   ├── esquemas/                    # Validaciones Pydantic
│   ├── seguridad/                   # Hash Argon2, JWT, permisos de roles
│   ├── utilidades/                  # Archivos públicos y privados
│   ├── configuracion/               # Entorno y unidad de trabajo PostgreSQL
│   ├── scripts/                     # Creación interactiva del administrador
│   └── pruebas/                     # Pruebas de servicios con dobles y de API
├── pruebas/                         # Criterios de prueba y evidencias
└── documentacion/                   # Decisiones, requisitos y diagramas
```

La estructura **conserva los módulos y capas del Capítulo III**. Se añaden archivos técnicos imprescindibles (`main.py`, `package.json`, `esquemas/`, `seguridad/`, etc.) para que funcione la versión inicial. Los modelos de comodidades e imágenes se agregan para corresponder con las diez tablas del Capítulo IV. El administrador sigue siendo un **rol de `usuarios`**, no una tabla separada.

### Capas y dependencias

- `api/` solo traduce HTTP ↔ servicios; no ejecuta reglas de negocio ni consultas.
- `servicios/` contiene los casos de uso, lanza errores de `dominio/errores.py` y **no importa FastAPI ni hace `commit`**.
- `dominio/puertos.py` define `Protocol` de repositorios; `repositorios/` los implementa con SQLAlchemy.
- `api/dependencias.py` compone las implementaciones y permite sustituirlas en las pruebas.
- La unidad de trabajo en `configuracion/base_datos.obtener_db` confirma o revierte la transacción al final de cada petición.

Con esto se refuerzan SRP y DIP en el backend. Quedan decisiones no SOLID heredadas: herencia de esquemas de registro, roles resueltos con condicionales y páginas React monolíticas (ver sección 9).

## 4. Base de datos: 10 tablas del diseño académico

| Tabla | Propósito |
|---|---|
| `alquiler.usuarios` | Identidad, correo, hash, rol y estado |
| `alquiler.buscadores` | Extensión uno-a-uno del buscador |
| `alquiler.arrendadores` | Extensión uno-a-uno del arrendador, RUC obligatorio (11 dígitos) |
| `alquiler.alojamientos` | Anuncios, precio, distrito y disponibilidad |
| `alquiler.comodidades` | Catálogo único de comodidades |
| `alquiler.alojamiento_comodidades` | Asociación M:N, clave compuesta |
| `alquiler.imagenes_alojamiento` | Rutas de imágenes de inmuebles |
| `alquiler.perfiles_companero` | Presupuesto, estilo de vida tipado y descripción; máximo uno por buscador |
| `alquiler.catalogo_habitos` | Catálogo de hábitos, rutinas y pasatiempos seleccionables |
| `alquiler.catalogo_preferencias` | Catálogo de preferencias de convivencia |
| `alquiler.perfil_habitos` | Asociación M:N perfil–hábito, clave compuesta |
| `alquiler.perfil_preferencias` | Asociación M:N perfil–preferencia, clave compuesta |
| `alquiler.verificaciones_identidad` | Solicitud, estado, revisor y observación |
| `alquiler.registros_acceso` | Acciones de autenticación y acceso |

**Integridad:** PK/FK, UNIQUE, NOT NULL, CHECK, defaults e índices. Las autorizaciones de propietario y rol se refuerzan en FastAPI; una FK por sí sola no garantiza que un revisor sea administrador.

`sql/01_esquema_alquiler.sql` es el **mismo DDL de la sección 4.6**; no realiza `DROP`, no cambia otras bases y se importa automáticamente con PostgreSQL solo cuando el volumen está vacío. En futuros cambios de esquema se recomienda añadir Alembic y migraciones versionadas, en vez de editar el SQL inicial de una base ya utilizada.

### 4.1 Perfil de convivencia con datos tipados

`sql/04_mejoras_perfil_convivencia.sql` amplía el perfil de convivencia **de forma aditiva e idempotente** (no borra ni renombra nada):

- Catálogos reutilizables `catalogo_habitos` y `catalogo_preferencias`, con categoría, orden y estado.
- Tablas puente `perfil_habitos` y `perfil_preferencias` (M:N) que sustituyen el texto libre para el matching.
- Columnas tipadas en `perfiles_companero`: `fuma`, `tiene_mascotas`, `horario`, `nivel_orden` (1–5), `ocupacion`, `genero`, `genero_preferido`, `edad` y `actualizado_en`.
- Restricciones `CHECK` para cada dominio y para la descripción (10–500 caracteres en escrituras nuevas).
- Semillas de hábitos y preferencias con `ON CONFLICT DO NOTHING`.

Los campos de texto `habitos` y `preferencias` se conservan como respaldo de compatibilidad: se siguen devolviendo en la API, pero la interfaz ya trabaja con los catálogos.

Aplica la mejora sobre una base ya creada con:

```bash
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/04_mejoras_perfil_convivencia.sql
```

En un volumen nuevo se ejecuta automáticamente después de `01_esquema_alquiler.sql`.

La compatibilidad entre perfiles se calcula en `backend/dominio/compatibilidad.py`: 50 puntos por presupuestos solapados, hasta 20 por hábitos en común, hasta 20 por preferencias en común y 5 por cada campo tipado coincidente (máximo 100).

## 5. Endpoints principales (Swagger: /docs)

| Método / ruta | Acceso | Estado inicial |
|---|---|---|
| `POST /api/autenticacion/registro/buscador` | Público | Implementado; DNI/CE/pasaporte obligatorio y validado por formato |
| `POST /api/autenticacion/registro/arrendador` | Público | Implementado; exige teléfono de 9 dígitos (WhatsApp) y RUC de 11 dígitos |
| `POST /api/autenticacion/login` | Público | Implementado |
| `POST /api/autenticacion/logout` | Autenticado | Registro del cierre; revocación anticipada de JWT pendiente |
| `GET/PATCH /api/usuarios/me` | Autenticado | Implementado |
| `POST/DELETE /api/usuarios/me/foto` | Autenticado | Foto de perfil con validación de JPG, PNG o WebP (máx. 5 MB) |
| `GET /api/usuarios/{id}/foto` | Público | Sirve la foto de perfil; no expone datos de contacto |
| `GET /api/usuarios/me/accesos` | Titular | Implementado |
| `GET /api/alojamientos` y `GET /api/alojamientos/{id}` | Público | Implementado con filtros y paginación |
| `GET /api/alojamientos/comodidades` | Público | Implementado; catálogo se carga por SQL |
| `POST /api/alojamientos` | Arrendador | Implementado |
| `PATCH/DELETE /api/alojamientos/{id}` | Arrendador dueño | Implementado; DELETE desactiva |
| `POST /api/alojamientos/{id}/imagenes` | Arrendador dueño | Implementado; la primera imagen es la portada del catálogo |
| `GET /api/alojamientos/{id}/imagenes` | Público para activos | Implementado; galería del detalle |
| `GET /api/alojamientos/{id}/contacto` | Buscador | Nombre y teléfono del arrendador para contacto por WhatsApp; el catálogo sigue siendo público |
| `GET/PUT /api/companeros/mi-perfil` | Buscador | Perfil con catálogos de hábitos/preferencias y campos tipados |
| `GET /api/companeros/catalogos` | Público | Catálogos y opciones para construir el perfil |
| `GET /api/companeros/coincidencias` | Buscador | Coincidencia por presupuestos solapados, ordenada por compatibilidad, con nombre y teléfono para WhatsApp |
| `POST /api/verificaciones/solicitar` | Autenticado | Implementado, documentos privados |
| `GET /api/verificaciones/mi-estado` | Solicitante | Implementado |
| `GET /api/administracion/usuarios` | Administrador | Listado de hasta 100 |
| `PATCH /api/administracion/usuarios/{uid}/estado` | Administrador | Implementado |
| `GET /api/administracion/verificaciones` | Administrador | Pendientes |
| `GET /api/administracion/verificaciones/{id}/documento` | Administrador | Archivo privado autorizado |
| `POST /api/administracion/verificaciones/{id}/revision` | Administrador | Implementado con bloqueo transaccional |

### Ejemplo de datos de una publicación

```json
{
  "titulo": "Habitación cercana al centro",
  "descripcion": "Habitación amoblada, con baño compartido y escritorio",
  "precio": 450.00,
  "direccion": "Av. de ejemplo 123",
  "distrito": "Tingo María",
  "tipo": "habitacion",
  "estado": "activo",
  "comodidad_ids": []
}
```

## 6. Correspondencia con los 30 RF y 30 RNF

El documento del curso plantea **30 RF / 30 RNF**, pero este repositorio es una **base para implementarlos progresivamente**:

- **Implementado en la base:** registros, ingreso, roles en API, consulta y edición limitada del perfil, foto de perfil con carga y retiro, historial, CRUD inicial de inmuebles (retiro lógico), consulta pública, paginación, subida de imágenes con portada y galería, detalle público, contacto autenticado con el arrendador por WhatsApp, único perfil de convivencia con resumen editable y catálogos tipados, coincidencias ordenadas por compatibilidad con datos de contacto, solicitud/revisión de identidad y gestión inicial de cuentas.
- **Parcialmente implementado:** cierre de sesión (borra el token del navegador, pero el JWT emitido sigue siendo válido hasta expirar), filtros de precio (solo máximo), selección de comodidades en el frontend, coincidencia basada únicamente en presupuesto, destacados (ordenamiento sin panel para asignarlos), paneles con métricas y filtros administrativos.
- **Pendiente:** eliminación formal de cuenta conforme a política de conservación, revocación de tokens, paginación completa de todas las listas, funcionalidades avanzadas de coincidencias, historial/auditoría de cambios, migraciones Alembic, suite completa de pruebas, gestión de imágenes (orden/retiro), respaldo/recuperación automatizada y cumplimiento verificado de RNF-08/09, RNF-15, RNF-19/20.

**Los objetivos de RPO=24 h y RTO=8 h son metas del informe, no capacidades ya demostradas.** Tampoco se ha realizado carga de 50 usuarios concurrentes, ni auditoría de accesibilidad o seguridad.

## 7. Seguridad: aspectos que debes atender

- Para el entorno local se utiliza HTTP en `localhost`; para **producción es obligatorio HTTPS/TLS**, un proxy seguro y configuración cuidadosa de CORS/headers.
- Los secretos solo se pasan por `.env`/variables de entorno; nunca subir `.env` al repositorio.
- Los hashes Argon2 protegen contraseñas y el backend verifica roles y propiedad de publicaciones.
- El teléfono es obligatorio para el arrendador (9 dígitos, celular) y solo se entrega a cuentas de **buscador** mediante `GET /api/alojamientos/{id}/contacto`; visitantes, arrendadores y administradores no reciben esos datos personales. El enlace de WhatsApp se construye con un mensaje de presentación precargado.
- El JWT se guarda en `sessionStorage` en este prototipo; producción requiere mejor estrategia de sesión/revocación, mitigación XSS y cookies seguras donde corresponda.
- Los DNI se guardan en una carpeta privada, no montada como recursos públicos; solo los descarga un administrador autenticado. Antes de usar datos reales, definir consentimiento, retención, permisos de almacenamiento, límites de carga, políticas de eliminación y análisis de riesgos.
- La validación de tipo de archivo incluida es básica (encabezados de archivo), **no reemplaza** antivirus ni análisis de contenido.
- Los volúmenes Docker **NO equivalen a respaldos**. Programa copias de PostgreSQL y archivos en soportes separados y comprueba la restauración.
- No reutilices usuarios o bases de otros proyectos. La configuración Docker de esta plantilla usa volúmenes propios.

## 8. Pruebas rápidas

```bash
# Backend: servicios con dobles en memoria, API y validaciones
# Si el contenedor está levantado:
docker compose exec backend pytest -q pruebas/

# Integridad SQL (devuelve ROLLBACK):
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U alquiler_app -d alquiler_db < sql/02_pruebas_integridad.sql

# Estado de los tres servicios:
docker compose ps
```

### Flujo de validación manual

1. Abrir la web sin sesión y buscar un alojamiento.
2. Registrar un arrendador e iniciar sesión.
3. Publicar alojamiento con precio positivo y verificar que aparece en la búsqueda pública.
4. Intentar consultar/modificar alojamientos ajenos desde otra cuenta de arrendador; el servidor debe rechazarlo.
5. Registrar un buscador, guardar un perfil y consultar coincidencias.
6. Solicitar revisión de identidad con un documento ficticio; iniciar sesión como administrador y aprobar/rechazar.
7. Comprobar la base de datos con `SELECT` en el esquema `alquiler`.

## 9. Próximos entregables

- Completar diagramas, DTOs, contratos y cobertura total de RF/RNF.
- Añadir Alembic, pruebas de integración, pruebas de carga, control de errores consistente, monitoreo y métricas.
- Refinar el matching con filtros por distrito, edad y género preferido, y migrar los textos heredados a los catálogos.
- Modelar UBIGEO (departamento/provincia/distrito) y catálogos administrables de estados y tipos.
- Implementar solicitud de eliminación de cuenta y política de retención.
- Crear despliegue de producción (Vite `build`, servidor estático y proxy HTTPS, procesos backend, respaldos restaurables).

## 10. Correspondencia con el informe

- Capítulo I: 30 RF / 30 RNF — **diseño objetivo**.
- Capítulo II: Visitante, Buscador, Arrendador, Administrador y 13 casos de uso.
- Capítulo III: monolito modular en capas, despliegue Docker en 3 servicios.
- Capítulo IV: 10 tablas, 3FN, diccionario de datos y DDL incluido sin modificaciones.
- Capítulo V: interfaz UI (primer prototipo React).
- Capítulo VI: pruebas y evidencias de ejecución tras instalar Docker (aún no verificadas en esta generación).
