from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.administracion.router import router as administracion_router
from api.alojamientos.router import router as alojamientos_router
from api.autenticacion.router import router as auth_router
from api.companeros.router import router as companeros_router
from api.usuarios.router import router as usuarios_router
from api.verificaciones.router import router as verificaciones_router
from configuracion.configuracion import settings
from dominio.errores import ErrorDominio

app = FastAPI(title='Plataforma Web de Gestión y Búsqueda de Alojamientos', version='0.1.0', description='API REST de demostración académica; PostgreSQL es la fuente de verdad.')
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(',') if o.strip()], allow_credentials=False, allow_methods=['GET','POST','PUT','PATCH','DELETE'], allow_headers=['Authorization','Content-Type'])


@app.exception_handler(ErrorDominio)
async def manejar_error_dominio(_: Request, exc: ErrorDominio):
    """Traduce errores de negocio a HTTP sin que el dominio conozca FastAPI."""
    return JSONResponse(status_code=exc.codigo, content={'detail': exc.mensaje})


for router in (auth_router, usuarios_router, alojamientos_router, companeros_router, verificaciones_router, administracion_router):
    app.include_router(router)

@app.get('/api/salud', tags=['Salud'])
def salud():
    return {'estado':'ok','servicio':'backend'}
