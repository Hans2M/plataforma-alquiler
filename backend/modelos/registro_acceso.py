from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from configuracion.base_datos import Base

class RegistroAcceso(Base):
    __tablename__ = "registros_acceso"
    __table_args__ = {"schema": "alquiler"}
    registro_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.usuarios.usuario_id"), nullable=False)
    accion: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ip: Mapped[str | None] = mapped_column(String(45))
    dispositivo: Mapped[str | None] = mapped_column(Text)
