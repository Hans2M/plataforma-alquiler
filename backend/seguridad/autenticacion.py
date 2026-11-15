from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from configuracion.base_datos import obtener_db
from configuracion.configuracion import settings
from modelos.usuario import Usuario
from repositorios.usuarios import RepositorioUsuariosSQLAlchemy

hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def hash_clave(valor: str) -> str:
    return hasher.hash(valor)

def verificar_clave(valor: str, clave_hash: str) -> bool:
    try:
        return hasher.verify(valor, clave_hash)
    except Exception:
        return False

def crear_token(usuario_id: int) -> str:
    ahora = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(usuario_id), "iat": ahora, "exp": ahora + timedelta(minutes=settings.access_token_minutes)}, settings.secret_key, algorithm="HS256")

def usuario_actual(token: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(obtener_db, scope="function")) -> Usuario:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Necesitas iniciar sesión")
    try:
        data = jwt.decode(token.credentials, settings.secret_key, algorithms=['HS256'])
        uid = int(data['sub'])
    except (InvalidTokenError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Sesión no válida o expirada")
    u = RepositorioUsuariosSQLAlchemy(db).por_id(uid)
    if u is None or u.estado_cuenta == 'suspendida':
        raise HTTPException(status_code=401, detail="Cuenta no disponible")
    return u

def rol_requerido(*roles: str):
    def validar(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status_code=403, detail='No autorizado para este rol')
        return usuario
    return validar
