from fastapi import APIRouter, Depends, File, UploadFile

from api.dependencias import servicio_verificaciones
from esquemas.datos import VerificacionSalida
from modelos.usuario import Usuario
from seguridad.autenticacion import usuario_actual
from servicios.verificaciones import ServicioVerificaciones
from utilidades.archivos import guardar_archivo, ruta_segura

router = APIRouter(prefix='/api/verificaciones', tags=['Verificaciones'])

@router.get('/mi-estado', response_model=VerificacionSalida | None)
def estado(
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioVerificaciones = Depends(servicio_verificaciones),
):
    return servicio.estado(u.usuario_id)

@router.post('/solicitar', response_model=VerificacionSalida, status_code=201)
async def solicitar(
    archivo: UploadFile = File(...),
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioVerificaciones = Depends(servicio_verificaciones),
):
    # Se valida antes de escribir el archivo para no dejar huérfanos.
    servicio.validar_nueva_solicitud(u.usuario_id)
    ruta = await guardar_archivo(archivo, 'privados/dni', admite_pdf=True)
    try:
        return servicio.crear_solicitud(u.usuario_id, ruta)
    except Exception:
        ruta_segura(ruta).unlink(missing_ok=True)
        raise
