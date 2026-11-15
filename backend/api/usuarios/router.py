from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.dependencias import servicio_usuarios
from esquemas.datos import UsuarioEdicion, UsuarioSalida
from modelos.usuario import Usuario
from seguridad.autenticacion import usuario_actual
from servicios.usuarios import ServicioUsuarios
from utilidades.archivos import guardar_archivo, ruta_segura

router = APIRouter(prefix='/api/usuarios', tags=['Usuarios'])

@router.get('/me', response_model=UsuarioSalida)
def mi_perfil(u: Usuario = Depends(usuario_actual)):
    return u

@router.patch('/me', response_model=UsuarioSalida)
def editar_perfil(
    datos: UsuarioEdicion,
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioUsuarios = Depends(servicio_usuarios),
):
    return servicio.modificar_perfil(u, datos)

@router.post('/me/foto', response_model=UsuarioSalida)
async def subir_foto(
    archivo: UploadFile = File(...),
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioUsuarios = Depends(servicio_usuarios),
):
    """Sube (o reemplaza) la foto de perfil del usuario autenticado."""
    ruta = await guardar_archivo(archivo, f'publicos/perfiles/{u.usuario_id}')
    try:
        anterior = servicio.cambiar_foto(u, ruta)
    except Exception:
        # No dejar archivos huérfanos si la transacción no puede completarse.
        ruta_segura(ruta).unlink(missing_ok=True)
        raise
    if anterior:
        ruta_segura(anterior).unlink(missing_ok=True)
    return u

@router.delete('/me/foto', response_model=UsuarioSalida)
def borrar_foto(
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioUsuarios = Depends(servicio_usuarios),
):
    anterior = servicio.quitar_foto(u)
    if anterior:
        ruta_segura(anterior).unlink(missing_ok=True)
    return u

@router.get('/{uid}/foto')
def ver_foto(
    uid: int,
    servicio: ServicioUsuarios = Depends(servicio_usuarios),
):
    """Foto pública del perfil; las imágenes no contienen datos de contacto."""
    destino = ruta_segura(servicio.ruta_foto(uid))
    if not destino.is_file():
        raise HTTPException(status_code=404, detail='Foto de perfil no disponible')
    return FileResponse(
        destino,
        headers={
            'Cache-Control': 'no-cache',
            'X-Content-Type-Options': 'nosniff',
        },
    )

@router.get('/me/accesos')
def mis_accesos(
    u: Usuario = Depends(usuario_actual),
    servicio: ServicioUsuarios = Depends(servicio_usuarios),
):
    return [
        {'accion': a.accion, 'fecha_hora': a.fecha_hora, 'ip': a.ip, 'dispositivo': a.dispositivo}
        for a in servicio.accesos_de(u.usuario_id)
    ]
