from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.dependencias import (
    servicio_administracion,
    servicio_catalogos,
    servicio_verificaciones,
)
from esquemas.datos import (
    CatalogosAdminSalida,
    EstadoCatalogoEditar,
    EstadoCatalogoSalida,
    EstadoCuentaEntrada,
    HabitoCatalogoEditar,
    HabitoCatalogoEntrada,
    HabitoCatalogoSalida,
    PreferenciaCatalogoEditar,
    PreferenciaCatalogoEntrada,
    PreferenciaCatalogoSalida,
    RevisionEntrada,
    TipoAlojamientoEditar,
    TipoAlojamientoEntrada,
    TipoAlojamientoSalida,
    UsuarioSalida,
    VerificacionSalida,
)
from modelos.usuario import Usuario
from seguridad.autenticacion import rol_requerido
from servicios.administracion import ServicioAdministracion
from servicios.catalogos import ServicioCatalogos
from servicios.verificaciones import ServicioVerificaciones
from utilidades.archivos import ruta_segura

router = APIRouter(prefix='/api/administracion', tags=['Administración'])


@router.get('/catalogos', response_model=CatalogosAdminSalida)
def catalogos(
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    """Todos los catálogos, incluidos los inactivos, para su gestión."""
    return {
        'tipos': servicio.tipos(incluir_inactivos=True),
        'estados': servicio.estados(incluir_inactivos=True),
        'habitos': servicio.habitos(incluir_inactivos=True),
        'preferencias': servicio.preferencias(incluir_inactivos=True),
    }


@router.post('/catalogos/tipos', response_model=TipoAlojamientoSalida, status_code=201)
def crear_tipo(
    entrada: TipoAlojamientoEntrada,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.crear_tipo(entrada)


@router.patch('/catalogos/tipos/{tipo_id}', response_model=TipoAlojamientoSalida)
def editar_tipo(
    tipo_id: int,
    entrada: TipoAlojamientoEditar,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.editar_tipo(tipo_id, entrada)


@router.patch(
    '/catalogos/estados/{dominio}/{codigo}', response_model=EstadoCatalogoSalida
)
def editar_estado(
    dominio: str,
    codigo: str,
    entrada: EstadoCatalogoEditar,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.editar_estado(dominio, codigo, entrada)


@router.post(
    '/catalogos/habitos', response_model=HabitoCatalogoSalida, status_code=201
)
def crear_habito(
    entrada: HabitoCatalogoEntrada,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.crear_habito(entrada)


@router.patch(
    '/catalogos/habitos/{habito_id}', response_model=HabitoCatalogoSalida
)
def editar_habito(
    habito_id: int,
    entrada: HabitoCatalogoEditar,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.editar_habito(habito_id, entrada)


@router.post(
    '/catalogos/preferencias',
    response_model=PreferenciaCatalogoSalida,
    status_code=201,
)
def crear_preferencia(
    entrada: PreferenciaCatalogoEntrada,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.crear_preferencia(entrada)


@router.patch(
    '/catalogos/preferencias/{preferencia_id}',
    response_model=PreferenciaCatalogoSalida,
)
def editar_preferencia(
    preferencia_id: int,
    entrada: PreferenciaCatalogoEditar,
    u: Usuario = Depends(rol_requerido('administrador')),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.editar_preferencia(preferencia_id, entrada)


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
