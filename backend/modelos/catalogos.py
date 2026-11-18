"""Catálogos administrables: tipos de alojamiento y estados por dominio.

Los códigos los fija la aplicación (la lógica compara contra ellos); el
administrador puede editar la etiqueta, la descripción, el orden y la
visibilidad sin tocar el código.
"""

from sqlalchemy import Boolean, Identity, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from configuracion.base_datos import Base


class TipoAlojamiento(Base):
    __tablename__ = "tipos_alojamiento"
    __table_args__ = {"schema": "alquiler"}

    tipo_id: Mapped[int] = mapped_column(
        SmallInteger, Identity(always=True), primary_key=True
    )
    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(200))
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )


class CatalogoEstado(Base):
    """Etiqueta editable de un estado; el dominio separa los contextos."""

    __tablename__ = "catalogo_estados"
    __table_args__ = {"schema": "alquiler"}

    dominio: Mapped[str] = mapped_column(String(30), primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(200))
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
