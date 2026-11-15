from sqlalchemy import select
from sqlalchemy.orm import Session

from dominio.consultas import CoincidenciaCompanero
from modelos.perfil_companero import PerfilCompanero
from modelos.usuario import Usuario


class RepositorioCompanerosSQLAlchemy:
    """Implementación del puerto RepositorioCompaneros."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def por_buscador(self, uid: int) -> PerfilCompanero | None:
        return self.db.scalar(
            select(PerfilCompanero).where(PerfilCompanero.buscador_id == uid)
        )

    def coincidencias(
        self, uid: int, perfil: PerfilCompanero
    ) -> list[CoincidenciaCompanero]:
        stmt = (
            select(PerfilCompanero, Usuario)
            .join(Usuario, Usuario.usuario_id == PerfilCompanero.buscador_id)
            .where(
                PerfilCompanero.buscador_id != uid,
                PerfilCompanero.estado == "activo",
                PerfilCompanero.presupuesto_min <= perfil.presupuesto_max,
                PerfilCompanero.presupuesto_max >= perfil.presupuesto_min,
            )
            .order_by(PerfilCompanero.perfil_id)
            .limit(50)
        )
        return [
            CoincidenciaCompanero(
                perfil_id=otro.perfil_id,
                buscador_id=otro.buscador_id,
                nombre_completo=usuario.nombre_completo,
                telefono=usuario.telefono,
                presupuesto_min=otro.presupuesto_min,
                presupuesto_max=otro.presupuesto_max,
                habitos=otro.habitos,
                preferencias=otro.preferencias,
                descripcion=otro.descripcion,
                estado=otro.estado,
                foto_perfil=bool(usuario.foto_perfil),
            )
            for otro, usuario in self.db.execute(stmt)
        ]

    def agregar(self, perfil: PerfilCompanero) -> None:
        self.db.add(perfil)
        self.db.flush()
