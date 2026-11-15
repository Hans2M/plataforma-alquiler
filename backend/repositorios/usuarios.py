from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.usuario import Arrendador, Buscador, Usuario


class RepositorioUsuariosSQLAlchemy:
    """Implementación PostgreSQL/SQLAlchemy del puerto RepositorioUsuarios."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def por_correo(self, correo: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.correo == correo.strip().lower()))

    def por_documento(self, documento: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.numero_documento == documento))

    def por_id(self, uid: int) -> Usuario | None:
        return self.db.get(Usuario, uid)

    def agregar(self, usuario: Usuario) -> None:
        self.db.add(usuario)
        # flush (no commit): asigna el ID y expone ya las violaciones UNIQUE
        # para que el servicio pueda traducirlas a un error de negocio.
        self.db.flush()

    def agregar_buscador(self, uid: int) -> None:
        self.db.add(Buscador(usuario_id=uid))
        self.db.flush()

    def agregar_arrendador(self, uid: int, ruc: str | None) -> None:
        self.db.add(Arrendador(usuario_id=uid, ruc=ruc))
        self.db.flush()

    def listar(self, limite: int = 100) -> list[Usuario]:
        return list(
            self.db.scalars(
                select(Usuario).order_by(Usuario.fecha_registro.desc()).limit(limite)
            )
        )
