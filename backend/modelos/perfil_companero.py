from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configuracion.base_datos import Base


class CatalogoHabito(Base):
    """Pasatiempo, rutina o hábito de convivencia seleccionable."""

    __tablename__ = "catalogo_habitos"
    __table_args__ = {"schema": "alquiler"}

    habito_id: Mapped[int] = mapped_column(
        SmallInteger, Identity(always=True), primary_key=True
    )
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    categoria: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="convivencia"
    )
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )


class CatalogoPreferencia(Base):
    """Preferencia de convivencia seleccionable por el buscador."""

    __tablename__ = "catalogo_preferencias"
    __table_args__ = {"schema": "alquiler"}

    preferencia_id: Mapped[int] = mapped_column(
        SmallInteger, Identity(always=True), primary_key=True
    )
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    categoria: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="convivencia"
    )
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )


class PerfilHabito(Base):
    __tablename__ = "perfil_habitos"
    __table_args__ = {"schema": "alquiler"}

    perfil_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("alquiler.perfiles_companero.perfil_id", ondelete="CASCADE"),
        primary_key=True,
    )
    habito_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("alquiler.catalogo_habitos.habito_id"),
        primary_key=True,
    )


class PerfilPreferencia(Base):
    __tablename__ = "perfil_preferencias"
    __table_args__ = {"schema": "alquiler"}

    perfil_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("alquiler.perfiles_companero.perfil_id", ondelete="CASCADE"),
        primary_key=True,
    )
    preferencia_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("alquiler.catalogo_preferencias.preferencia_id"),
        primary_key=True,
    )


class PerfilCompanero(Base):
    __tablename__ = "perfiles_companero"
    __table_args__ = {"schema": "alquiler"}

    perfil_id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True
    )
    buscador_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("alquiler.buscadores.usuario_id"),
        nullable=False,
        unique=True,
    )
    presupuesto_min: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    presupuesto_max: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # Columnas heredadas de texto libre. Se conservan por compatibilidad;
    # la información estructurada vive en los catálogos M:N.
    habitos: Mapped[str | None] = mapped_column(Text)
    preferencias: Mapped[str | None] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(
        String(15), nullable=False, server_default="activo"
    )

    # Campos tipados: permiten filtrar y calcular compatibilidad.
    fuma: Mapped[bool | None] = mapped_column(Boolean)
    tiene_mascotas: Mapped[bool | None] = mapped_column(Boolean)
    horario: Mapped[str | None] = mapped_column(String(15))
    nivel_orden: Mapped[int | None] = mapped_column(SmallInteger)
    ocupacion: Mapped[str | None] = mapped_column(String(15))
    genero: Mapped[str | None] = mapped_column(String(20))
    genero_preferido: Mapped[str | None] = mapped_column(String(20))
    edad: Mapped[int | None] = mapped_column(SmallInteger)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    habitos_catalogo: Mapped[list["CatalogoHabito"]] = relationship(
        secondary=PerfilHabito.__table__,
        lazy="selectin",
        order_by="CatalogoHabito.orden",
    )
    preferencias_catalogo: Mapped[list["CatalogoPreferencia"]] = relationship(
        secondary=PerfilPreferencia.__table__,
        lazy="selectin",
        order_by="CatalogoPreferencia.orden",
    )

    @property
    def _habitos_ordenados(self) -> list["CatalogoHabito"]:
        return sorted(self.habitos_catalogo, key=lambda h: (h.orden, h.nombre))

    @property
    def _preferencias_ordenadas(self) -> list["CatalogoPreferencia"]:
        return sorted(self.preferencias_catalogo, key=lambda p: (p.orden, p.nombre))

    @property
    def habito_ids(self) -> list[int]:
        return [habito.habito_id for habito in self._habitos_ordenados]

    @property
    def habito_nombres(self) -> list[str]:
        return [habito.nombre for habito in self._habitos_ordenados]

    @property
    def preferencia_ids(self) -> list[int]:
        return [preferencia.preferencia_id for preferencia in self._preferencias_ordenadas]

    @property
    def preferencia_nombres(self) -> list[str]:
        return [preferencia.nombre for preferencia in self._preferencias_ordenadas]
