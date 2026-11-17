from fastapi import APIRouter, Depends

from api.dependencias import servicio_companeros
from esquemas.datos import CatalogosSalida, CoincidenciaSalida, PerfilEntrada, PerfilSalida
from modelos.usuario import Usuario
from seguridad.autenticacion import rol_requerido
from servicios.companeros import ServicioCompaneros

router = APIRouter(prefix='/api/companeros', tags=['Compañeros'])

OPCIONES = {
    "horarios": [
        {"valor": "temprano", "etiqueta": "Madrugo"},
        {"valor": "tarde", "etiqueta": "Activo por la tarde"},
        {"valor": "nocturno", "etiqueta": "Nocturno"},
        {"valor": "flexible", "etiqueta": "Horario flexible"},
    ],
    "ocupaciones": [
        {"valor": "estudiante", "etiqueta": "Estudiante"},
        {"valor": "trabajador", "etiqueta": "Trabajador/a"},
        {"valor": "ambos", "etiqueta": "Estudio y trabajo"},
        {"valor": "otro", "etiqueta": "Otro"},
    ],
    "generos": [
        {"valor": "femenino", "etiqueta": "Femenino"},
        {"valor": "masculino", "etiqueta": "Masculino"},
        {"valor": "otro", "etiqueta": "Otro"},
        {"valor": "prefiero_no_decir", "etiqueta": "Prefiero no decirlo"},
    ],
    "generos_preferidos": [
        {"valor": "femenino", "etiqueta": "Con mujeres"},
        {"valor": "masculino", "etiqueta": "Con hombres"},
        {"valor": "mixto", "etiqueta": "Mixto"},
        {"valor": "indiferente", "etiqueta": "Indiferente"},
    ],
}


@router.get('/catalogos', response_model=CatalogosSalida)
def catalogos(servicio: ServicioCompaneros = Depends(servicio_companeros)):
    habitos, preferencias = servicio.catalogos()
    return {
        "habitos": habitos,
        "preferencias": preferencias,
        "opciones": OPCIONES,
    }


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
