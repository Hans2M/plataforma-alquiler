"""UBIGEO: departamentos, provincias y distritos del Perú.

Los datos oficiales se cargan con ``sql/05_ubigeo_y_catalogos.sql``. El
alojamiento guarda una FK al distrito y conserva el nombre en texto como
respaldo histórico para clientes anteriores.
"""

from sqlalchemy import CHAR, ForeignKey, Identity, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configuracion.base_datos import Base


class Departamento(Base):
    __tablename__ = "ubigeo_departamentos"
    __table_args__ = {"schema": "alquiler"}

    departamento_id: Mapped[int] = mapped_column(
        SmallInteger, Identity(always=True), primary_key=True
    )
    codigo: Mapped[str] = mapped_column(CHAR(2), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    provincias: Mapped[list["Provincia"]] = relationship(
        back_populates="departamento",
        order_by="Provincia.nombre",
        lazy="selectin",
    )


class Provincia(Base):
    __tablename__ = "ubigeo_provincias"
    __table_args__ = {"schema": "alquiler"}

    provincia_id: Mapped[int] = mapped_column(
        SmallInteger, Identity(always=True), primary_key=True
    )
    departamento_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("alquiler.ubigeo_departamentos.departamento_id"),
        nullable=False,
    )
    codigo: Mapped[str] = mapped_column(CHAR(4), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)

    departamento: Mapped[Departamento] = relationship(
        back_populates="provincias", lazy="joined"
    )
    distritos: Mapped[list["Distrito"]] = relationship(
        back_populates="provincia",
        order_by="Distrito.nombre",
        lazy="selectin",
    )


class Distrito(Base):
    __tablename__ = "ubigeo_distritos"
    __table_args__ = {"schema": "alquiler"}

    distrito_id: Mapped[int] = mapped_column(
        Integer, Identity(always=True), primary_key=True
    )
    provincia_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("alquiler.ubigeo_provincias.provincia_id"),
        nullable=False,
    )
    codigo: Mapped[str] = mapped_column(CHAR(6), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    provincia: Mapped[Provincia] = relationship(
        back_populates="distritos", lazy="joined"
    )

    @property
    def provincia_nombre(self) -> str:
        return self.provincia.nombre

    @property
    def departamento_nombre(self) -> str:
        return self.provincia.departamento.nombre

    @property
    def distrito_completo(self) -> str:
        """Texto legible para la interfaz: distrito, provincia, departamento."""
        return f"{self.nombre}, {self.provincia_nombre}, {self.departamento_nombre}"
