from decimal import Decimal
from sqlalchemy import BigInteger, ForeignKey, Identity, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from configuracion.base_datos import Base

class PerfilCompanero(Base):
    __tablename__ = "perfiles_companero"
    __table_args__ = {"schema": "alquiler"}
    perfil_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    buscador_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.buscadores.usuario_id"), nullable=False, unique=True)
    presupuesto_min: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)
    presupuesto_max: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)
    habitos: Mapped[str | None] = mapped_column(Text)
    preferencias: Mapped[str | None] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(15), nullable=False, server_default="activo")
