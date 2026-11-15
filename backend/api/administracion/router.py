from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.dependencias import servicio_administracion, servicio_verificaciones
from esquemas.datos import (
    EstadoCuentaEntrada,
    RevisionEntrada,
    UsuarioSalida,
    VerificacionSalida,
)
from modelos.usuario import Usuario
from seguridad.autenticacion import rol_requerido
from servicios.administracion import ServicioAdministracion
from servicios.verificaciones import ServicioVerificaciones
from utilidades.archivos import ruta_segura

router = APIRouter(prefix='/api/administracion', tags=['Administración'])

@router.get('/usuarios', response_model=list[UsuarioSalida])
def usuarios(
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioAdministracion = Depends(servicio_administracion),
):
    return servicio.listar_usuarios()

@router.patch('/usuarios/{uid}/estado', response_model=UsuarioSalida)
def estado_cuenta(
    uid: int,
    entrada: EstadoCuentaEntrada,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioAdministracion = Depends(servicio_administracion),
):
    return servicio.cambiar_estado(u, uid, entrada.estado_cuenta)

@router.get('/verificaciones', response_model=list[VerificacionSalida])
def verificaciones(
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioVerificaciones = Depends(servicio_verificaciones),
):
    return servicio.pendientes()

@router.get('/verificaciones/{vid}/documento')
def documento(
    vid: int,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioVerificaciones = Depends(servicio_verificaciones),
):
    ruta = ruta_segura(servicio.documento(vid))
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail='Archivo no encontrado')
    return FileResponse(
        ruta,
        headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'},
    )

@router.post('/verificaciones/{vid}/revision', response_model=VerificacionSalida)
def revision(
    vid: int,
    entrada: RevisionEntrada,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioVerificaciones = Depends(servicio_verificaciones),
):
    return servicio.revisar(vid, u, entrada.decision, entrada.observacion)
