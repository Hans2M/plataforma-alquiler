from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from configuracion.base_datos import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "alquiler"}
    usuario_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    correo: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    clave_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    estado_cuenta: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pendiente")
    telefono: Mapped[str | None] = mapped_column(String(25))
    tipo_documento: Mapped[str | None] = mapped_column(String(20))
    numero_documento: Mapped[str | None] = mapped_column(String(25), unique=True)
    # Ruta relativa dentro del almacén de archivos; NULL si no subió foto.
    foto_perfil: Mapped[str | None] = mapped_column(String(255))
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class Buscador(Base):
    __tablename__ = "buscadores"
    __table_args__ = {"schema": "alquiler"}
    usuario_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.usuarios.usuario_id"), primary_key=True)

class Arrendador(Base):
    __tablename__ = "arrendadores"
    __table_args__ = {"schema": "alquiler"}
    usuario_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alquiler.usuarios.usuario_id"), primary_key=True)
    ruc: Mapped[str | None] = mapped_column(String(11), unique=True)
