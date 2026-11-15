from fastapi import APIRouter, Depends, Request

from api.dependencias import servicio_autenticacion
from esquemas.datos import (
    Credenciales,
    RegistroArrendador,
    RegistroBuscador,
    Token,
    UsuarioSalida,
)
from modelos.usuario import Usuario
from seguridad.autenticacion import usuario_actual
from servicios.autenticacion import ServicioAutenticacion

router = APIRouter(prefix='/api/autenticacion', tags=['Autenticación'])

def metadatos(req: Request):
    return (req.client.host if req.client else None), req.headers.get('user-agent','')[:500]

@router.post('/registro/buscador', response_model=UsuarioSalida, status_code=201)
def registrar_buscador(
    datos: RegistroBuscador,
    req: Request,
    servicio: ServicioAutenticacion = Depends(servicio_autenticacion),
):
    return servicio.registrar(datos, 'buscador', *metadatos(req))

@router.post('/registro/arrendador', response_model=UsuarioSalida, status_code=201)
def registrar_arrendador(
    datos: RegistroArrendador,
    req: Request,
    servicio: ServicioAutenticacion = Depends(servicio_autenticacion),
):
    return servicio.registrar(datos, 'arrendador', *metadatos(req))

@router.post('/login', response_model=Token)
def login(
    datos: Credenciales,
    req: Request,
    servicio: ServicioAutenticacion = Depends(servicio_autenticacion),
):
    return servicio.ingresar(datos, *metadatos(req))

@router.post('/logout')
def logout(
    req: Request,
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioAutenticacion = Depends(servicio_autenticacion),
):
    servicio.cerrar_sesion(u.usuario_id, *metadatos(req))
    return {'mensaje': 'Cierra la sesión eliminando el token del navegador. En esta base JWT no se revoca anticipadamente.'}
