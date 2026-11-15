from fastapi import APIRouter, Depends

from api.dependencias import servicio_companeros
from esquemas.datos import CoincidenciaSalida, PerfilEntrada, PerfilSalida
from modelos.usuario import Usuario
from seguridad.autenticacion import rol_requerido
from servicios.companeros import ServicioCompaneros

router = APIRouter(prefix='/api/companeros', tags=['Compañeros'])

@router.get('/mi-perfil', response_model=PerfilSalida)
def mi_perfil(
    u: Usuario = Depends(rol_requerido('buscador')),
    servicio: ServicioCompaneros = Depends(servicio_companeros),
):
    return servicio.mi_perfil(u.usuario_id)

@router.put('/mi-perfil', response_model=PerfilSalida)
def editar(
    datos: PerfilEntrada,
    u: Usuario = Depends(rol_requerido('buscador')),
    servicio: ServicioCompaneros = Depends(servicio_companeros),
):
    return servicio.guardar_perfil(u.usuario_id, datos)

@router.get('/coincidencias', response_model=list[CoincidenciaSalida])
def buscar(
    u: Usuario = Depends(rol_requerido('buscador')),
    servicio: ServicioCompaneros = Depends(servicio_companeros),
):
    return servicio.coincidencias(u.usuario_id)
