from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.registro_acceso import RegistroAcceso


class RepositorioAccesosSQLAlchemy:
    """Implementación del puerto RepositorioAccesos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def registrar(
        self,
        usuario_id: int,
        accion: str,
        ip: str | None = None,
        dispositivo: str | None = None,
    ) -> None:
        self.db.add(
            RegistroAcceso(
                usuario_id=usuario_id,
                accion=accion,
                ip=ip,
                dispositivo=dispositivo,
            )
        )

    def de_usuario(self, uid: int) -> list[RegistroAcceso]:
        return list(
            self.db.scalars(
                select(RegistroAcceso)
                .where(RegistroAcceso.usuario_id == uid)
                .order_by(RegistroAcceso.fecha_hora.desc())
                .limit(100)
            )
        )
