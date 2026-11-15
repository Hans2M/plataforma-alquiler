from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from configuracion.base_datos import Base

class VerificacionIdentidad(Base):
    __tablename__ = "verificaciones_identidad"
    __table_args__ = {"schema": "alquiler"}
    verificacion_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.usuarios.usuario_id"), nullable=False)
    ruta_documento: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(15), nullable=False, server_default="pendiente")
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revisor_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("alquiler.usuarios.usuario_id"))
    fecha_revision: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observacion: Mapped[str | None] = mapped_column(Text)
