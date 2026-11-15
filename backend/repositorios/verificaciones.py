from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.verificacion_identidad import VerificacionIdentidad


class RepositorioVerificacionesSQLAlchemy:
    """Implementación del puerto RepositorioVerificaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def ultima_por_usuario(self, uid: int) -> VerificacionIdentidad | None:
        return self.db.scalar(
            select(VerificacionIdentidad)
            .where(VerificacionIdentidad.usuario_id == uid)
            .order_by(VerificacionIdentidad.fecha_solicitud.desc())
            .limit(1)
        )

    def pendientes(self) -> list[VerificacionIdentidad]:
        return list(
            self.db.scalars(
                select(VerificacionIdentidad)
                .where(VerificacionIdentidad.estado == "pendiente")
                .order_by(VerificacionIdentidad.fecha_solicitud)
                .limit(100)
            )
        )

    def por_id(
        self, verificacion_id: int, bloquear: bool = False
    ) -> VerificacionIdentidad | None:
        stmt = select(VerificacionIdentidad).where(
            VerificacionIdentidad.verificacion_id == verificacion_id
        )
        if bloquear:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def agregar(self, verificacion: VerificacionIdentidad) -> None:
        self.db.add(verificacion)
        self.db.flush()
