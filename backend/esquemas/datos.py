import re
from decimal import Decimal
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, field_validator, model_validator

class LecturaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

TiposDocumento = Literal["DNI", "CE", "PASAPORTE"]

_PATRONES_DOCUMENTO = {
    "DNI": (r"\d{8}", "El DNI debe tener exactamente 8 dígitos"),
    "CE": (r"\d{9}", "El carné de extranjería debe tener exactamente 9 dígitos"),
    "PASAPORTE": (
        r"[A-Za-z0-9]{8,12}",
        "El pasaporte debe tener entre 8 y 12 letras o números",
    ),
}

class RegistroBuscador(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=150)
    correo: EmailStr
    contrasena: str = Field(min_length=10, max_length=128)
    telefono: str | None = None
    tipo_documento: TiposDocumento = "DNI"
    numero_documento: str

    @field_validator("nombre_completo", mode="before")
    @classmethod
    def limpiar_nombre(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("telefono", "numero_documento", mode="before")
    @classmethod
    def limpiar_codigos(cls, valor):
        if isinstance(valor, str):
            return re.sub(r"[\s-]", "", valor)
        return valor

    @model_validator(mode="after")
    def validar_documento_y_telefono(self):
        patron, mensaje = _PATRONES_DOCUMENTO[self.tipo_documento]
        if not re.fullmatch(patron, self.numero_documento):
            raise ValueError(mensaje)
        if self.tipo_documento == "PASAPORTE":
            self.numero_documento = self.numero_documento.upper()
        if self.telefono and not re.fullmatch(r"\d{7,9}", self.telefono):
            raise ValueError("El teléfono debe tener entre 7 y 9 dígitos")
        return self

class RegistroArrendador(RegistroBuscador):
    # El teléfono es obligatorio: es el canal de contacto con el buscador.
    telefono: str
    ruc: str

    @field_validator("telefono")
    @classmethod
    def validar_telefono_arrendador(cls, valor: str) -> str:
        if not re.fullmatch(r"\d{9}", valor):
            raise ValueError(
                "El teléfono del arrendador debe tener 9 dígitos "
                "(celular para WhatsApp)"
            )
        return valor

    @field_validator("ruc", mode="before")
    @classmethod
    def limpiar_ruc(cls, valor):
        if isinstance(valor, str):
            return re.sub(r"[\s-]", "", valor)
        return valor

    @field_validator("ruc")
    @classmethod
    def validar_ruc(cls, valor: str) -> str:
        if not re.fullmatch(r"\d{11}", valor):
            raise ValueError("El RUC debe tener exactamente 11 dígitos")
        return valor

class Credenciales(BaseModel):
    correo: EmailStr
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UsuarioSalida(LecturaBase):
    usuario_id: int
    nombre_completo: str
    correo: str
    rol: str
    estado_cuenta: str
    telefono: str | None
    # La ruta interna no se publica; la interfaz solo necesita la URL.
    foto_perfil: str | None = Field(default=None, exclude=True)
    fecha_registro: datetime

    @computed_field
    @property
    def foto_url(self) -> str | None:
        return (
            f'/api/usuarios/{self.usuario_id}/foto' if self.foto_perfil else None
        )

class UsuarioEdicion(BaseModel):
    nombre_completo: str | None = Field(default=None, min_length=2, max_length=150)
    telefono: str | None = Field(default=None, max_length=25)

class AlojamientoEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    descripcion: str = Field(min_length=5)
    precio: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    direccion: str = Field(min_length=5, max_length=250)
    distrito: str = Field(min_length=2, max_length=100)
    tipo: str = Field(min_length=2, max_length=40)
    estado: Literal['activo','inactivo','alquilado'] = 'activo'
    comodidad_ids: list[int] = Field(default_factory=list)

class AlojamientoEditar(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=150)
    descripcion: str | None = Field(default=None, min_length=5)
    precio: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    direccion: str | None = Field(default=None, min_length=5, max_length=250)
    distrito: str | None = Field(default=None, min_length=2, max_length=100)
    tipo: str | None = Field(default=None, min_length=2, max_length=40)
    estado: Literal['activo','inactivo','alquilado'] | None = None
    comodidad_ids: list[int] | None = None

class AlojamientoSalida(LecturaBase):
    alojamiento_id: int
    arrendador_id: int
    titulo: str
    descripcion: str
    precio: Decimal
    direccion: str
    distrito: str
    tipo: str
    estado: str
    destacado: bool
    fecha_publicacion: datetime
    imagen_principal_id: int | None = None

class ContactoArrendadorSalida(LecturaBase):
    arrendador_id: int
    nombre_completo: str
    telefono: str | None
    correo: str

class PerfilEntrada(BaseModel):
    presupuesto_min: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    presupuesto_max: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    habitos: str | None = None
    preferencias: str | None = None
    descripcion: str | None = None
    estado: Literal['activo','inactivo'] = 'activo'

    @model_validator(mode='after')
    def presupuesto_ordenado(self):
        if self.presupuesto_max < self.presupuesto_min:
            raise ValueError('El presupuesto máximo debe ser mayor o igual al mínimo')
        return self

class PerfilSalida(PerfilEntrada, LecturaBase):
    perfil_id: int
    buscador_id: int

class CoincidenciaSalida(LecturaBase):
    """Perfil público de una coincidencia y su canal de contacto."""

    perfil_id: int
    buscador_id: int
    nombre_completo: str
    telefono: str | None
    presupuesto_min: Decimal
    presupuesto_max: Decimal
    habitos: str | None
    preferencias: str | None
    descripcion: str | None
    estado: str
    # La ruta interna no se publica; la interfaz solo necesita la URL.
    foto_perfil: bool = Field(default=False, exclude=True)

    @computed_field
    @property
    def foto_url(self) -> str | None:
        return (
            f'/api/usuarios/{self.buscador_id}/foto' if self.foto_perfil else None
        )

class VerificacionSalida(LecturaBase):
    verificacion_id: int
    usuario_id: int
    estado: str
    fecha_solicitud: datetime
    revisor_id: int | None
    fecha_revision: datetime | None
    observacion: str | None

class RevisionEntrada(BaseModel):
    decision: Literal['aprobada','rechazada']
    observacion: str | None = Field(default=None, max_length=1000)

class EstadoCuentaEntrada(BaseModel):
    estado_cuenta: Literal['pendiente','verificada','suspendida']
