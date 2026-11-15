from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile
from configuracion.configuracion import settings

TIPOS = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp', 'application/pdf': '.pdf'}

def _contenido_permitido(datos: bytes, mimetype: str) -> bool:
    if mimetype == 'image/jpeg': return datos.startswith(b'\xff\xd8\xff')
    if mimetype == 'image/png': return datos.startswith(b'\x89PNG\r\n\x1a\n')
    if mimetype == 'image/webp': return len(datos) > 12 and datos[:4] == b'RIFF' and datos[8:12] == b'WEBP'
    if mimetype == 'application/pdf': return datos.startswith(b'%PDF-')
    return False

async def guardar_archivo(archivo: UploadFile, subdirectorio: str, admite_pdf: bool = False) -> str:
    tipo = archivo.content_type or ''
    if tipo not in TIPOS or (tipo == 'application/pdf' and not admite_pdf):
        raise HTTPException(status_code=415, detail='Formato no permitido (JPG, PNG, WebP o PDF si se autoriza)')
    contenido = await archivo.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(contenido) > settings.max_upload_mb * 1024 * 1024 or not contenido:
        raise HTTPException(status_code=413, detail='Archivo vacío o demasiado grande')
    if not _contenido_permitido(contenido, tipo):
        raise HTTPException(status_code=415, detail='El contenido del archivo no coincide con el formato')
    ruta = Path(subdirectorio) / f'{uuid4().hex}{TIPOS[tipo]}'
    destino = settings.archivos_dir / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    return ruta.as_posix()

def ruta_segura(relativa: str) -> Path:
    base = settings.archivos_dir.resolve()
    candidato = (base / relativa).resolve()
    if not candidato.is_relative_to(base):
        raise HTTPException(status_code=403, detail='Ruta prohibida')
    return candidato
