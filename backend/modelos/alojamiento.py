from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configuracion.base_datos import Base
from modelos.catalogos import TipoAlojamiento
from modelos.ubigeo import Distrito

class Alojamiento(Base):
    __tablename__ = "alojamientos"
    __table_args__ = {"schema": "alquiler"}
    alojamiento_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    arrendador_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.arrendadores.usuario_id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    direccion: Mapped[str] = mapped_column(String(250), nullable=False)
    # Texto histórico: se conserva para clientes anteriores y búsqueda libre.
    distrito: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="activo")
    destacado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    fecha_publicacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # UBIGEO y catálogo de tipos (opcionales para no romper datos previos).
    distrito_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("alquiler.ubigeo_distritos.distrito_id")
    )
    tipo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("alquiler.tipos_alojamiento.tipo_id")
    )

    distrito_ref: Mapped[Distrito | None] = relationship(lazy="joined")
    tipo_ref: Mapped[TipoAlojamiento | None] = relationship(lazy="joined")

    # selectin evita N+1 al listar publicaciones y alimenta la foto de portada.
    imagenes: Mapped[list["ImagenAlojamiento"]] = relationship(
        "ImagenAlojamiento",
        order_by="ImagenAlojamiento.orden",
        lazy="selectin",
    )

    @property
    def imagen_principal_id(self) -> int | None:
        """Primera imagen de la publicación, usada en tarjetas y catálogo."""
        return self.imagenes[0].imagen_id if self.imagenes else None

    @property
    def distrito_completo(self) -> str:
        """Distrito, provincia y departamento cuando existe UBIGEO."""
        if self.distrito_ref is not None:
            return self.distrito_ref.distrito_completo
        return self.distrito

    @property
    def provincia_nombre(self) -> str | None:
        return self.distrito_ref.provincia_nombre if self.distrito_ref else None

    @property
    def departamento_nombre(self) -> str | None:
        return self.distrito_ref.departamento_nombre if self.distrito_ref else None

    @property
    def tipo_nombre(self) -> str:
        return self.tipo_ref.nombre if self.tipo_ref is not None else self.tipo

class Comodidad(Base):
    __tablename__ = "comodidades"
    __table_args__ = {"schema": "alquiler"}
    comodidad_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

class AlojamientoComodidad(Base):
    __tablename__ = "alojamiento_comodidades"
    __table_args__ = {"schema": "alquiler"}
    alojamiento_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.alojamientos.alojamiento_id"), primary_key=True)
    comodidad_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.comodidades.comodidad_id"), primary_key=True)

class ImagenAlojamiento(Base):
    __tablename__ = "imagenes_alojamiento"
    __table_args__ = {"schema": "alquiler"}
    imagen_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    alojamiento_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.alojamientos.alojamiento_id"), nullable=False)
    ruta_archivo: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
