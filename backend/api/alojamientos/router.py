from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from api.dependencias import servicio_alojamientos
from esquemas.datos import (
    AlojamientoEditar,
    AlojamientoEntrada,
    AlojamientoSalida,
    ContactoArrendadorSalida,
)
from modelos.usuario import Usuario
from seguridad.autenticacion import rol_requerido
from servicios.alojamientos import ServicioAlojamientos
from utilidades.archivos import guardar_archivo, ruta_segura

router = APIRouter(prefix='/api/alojamientos', tags=['Alojamientos'])

@router.get('', response_model=list[AlojamientoSalida])
def buscar(
    distrito: str | None = None,
    tipo: str | None = None,
    texto: str | None = None,
    precio_min: float | None = Query(None, ge=0),
    precio_max: float | None = Query(None, gt=0),
    dias: int | None = Query(None, ge=1, le=365),
    orden: Literal['recientes', 'precio_asc', 'precio_desc'] = 'recientes',
    pagina: int = Query(1, ge=1),
    limite: int = Query(12, ge=1, le=50),
    distrito_id: int | None = Query(None, gt=0),
    provincia_id: int | None = Query(None, gt=0),
    departamento_id: int | None = Query(None, gt=0),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    return servicio.buscar(
        distrito,
        tipo,
        precio_max,
        texto,
        pagina,
        limite,
        precio_min,
        dias,
        orden,
        distrito_id,
        provincia_id,
        departamento_id,
    )

@router.get('/comodidades')
def comodidades(servicio: ServicioAlojamientos = Depends(servicio_alojamientos)):
    return [
        {'comodidad_id': c.comodidad_id, 'nombre': c.nombre}
        for c in servicio.comodidades()
    ]

@router.get('/mis-publicaciones', response_model=list[AlojamientoSalida])
def propias(
    u: Usuario = Depends(rol_requerido('arrendador')),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    return servicio.de_arrendador(u.usuario_id)

@router.post('', response_model=AlojamientoSalida, status_code=201)
def publicar(
    datos: AlojamientoEntrada,
    u: Usuario = Depends(rol_requerido('arrendador')),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    return servicio.crear(u.usuario_id, datos)

@router.get('/imagenes/{imagen_id}')
def descargar_imagen(
    imagen_id: int,
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    destino = ruta_segura(servicio.ruta_imagen(imagen_id))
    if not destino.is_file():
        raise HTTPException(status_code=404, detail='Archivo no disponible')
    return FileResponse(destino)

@router.get('/{id_alojamiento}', response_model=AlojamientoSalida)
def detalle(
    id_alojamiento: int,
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    return servicio.detalle(id_alojamiento)

@router.get('/{id_alojamiento}/contacto', response_model=ContactoArrendadorSalida)
def contacto(
    id_alojamiento: int,
    _: Usuario = Depends(rol_requerido('buscador')),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    # El catálogo es público, pero los datos personales del arrendador solo
    # se entregan a buscadores que podrían alquilar la publicación.
    return servicio.contacto(id_alojamiento)

@router.get('/{id_alojamiento}/imagenes')
def imagenes(
    id_alojamiento: int,
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    return [
        {'imagen_id': i.imagen_id, 'url': f'/api/alojamientos/imagenes/{i.imagen_id}'}
        for i in servicio.imagenes(id_alojamiento)
    ]

@router.patch('/{id_alojamiento}', response_model=AlojamientoSalida)
def actualizar(
    id_alojamiento: int,
    datos: AlojamientoEditar,
    u: Usuario = Depends(rol_requerido('arrendador')),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    return servicio.modificar(u.usuario_id, id_alojamiento, datos)

@router.delete('/{id_alojamiento}')
def desactivar(
    id_alojamiento: int,
    u: Usuario = Depends(rol_requerido('arrendador')),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    servicio.desactivar(u.usuario_id, id_alojamiento)
    return {'mensaje': 'Publicación desactivada (eliminación lógica)'}

@router.post('/{id_alojamiento}/imagenes', status_code=201)
async def subir_imagen(
    id_alojamiento: int,
    archivo: UploadFile = File(...),
    u: Usuario = Depends(rol_requerido('arrendador')),
    servicio: ServicioAlojamientos = Depends(servicio_alojamientos),
):
    ruta = await guardar_archivo(archivo, f'publicos/alojamientos/{id_alojamiento}')
    try:
        imagen = servicio.registrar_imagen(u.usuario_id, id_alojamiento, ruta)
    except Exception:
        ruta_segura(ruta).unlink(missing_ok=True)
        raise
    return {
        'imagen_id': imagen.imagen_id,
        'url': f'/api/alojamientos/imagenes/{imagen.imagen_id}',
    }
