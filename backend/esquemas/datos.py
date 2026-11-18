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
    # Compatibilidad: clientes anteriores envían texto; los nuevos envían ids.
    distrito: str | None = Field(default=None, min_length=2, max_length=100)
    distrito_id: int | None = Field(default=None, gt=0)
    tipo: str | None = Field(default=None, min_length=2, max_length=40)
    tipo_id: int | None = Field(default=None, gt=0)
    estado: Literal['activo','inactivo','alquilado'] = 'activo'
    comodidad_ids: list[int] = Field(default_factory=list)

    @model_validator(mode='after')
    def ubicacion_o_texto(self):
        if self.distrito_id is None and not self.distrito:
            raise ValueError('Indica el distrito')
        if self.tipo_id is None and not self.tipo:
            raise ValueError('Indica el tipo de alojamiento')
        return self

class AlojamientoEditar(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=150)
    descripcion: str | None = Field(default=None, min_length=5)
    precio: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    direccion: str | None = Field(default=None, min_length=5, max_length=250)
    distrito: str | None = Field(default=None, min_length=2, max_length=100)
    distrito_id: int | None = Field(default=None, gt=0)
    tipo: str | None = Field(default=None, min_length=2, max_length=40)
    tipo_id: int | None = Field(default=None, gt=0)
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
    distrito_id: int | None = None
    distrito_completo: str | None = None
    provincia_nombre: str | None = None
    departamento_nombre: str | None = None
    tipo: str
    tipo_id: int | None = None
    tipo_nombre: str | None = None
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

    # Catálogos estructurados (recomendado). None = no modificar.
    habito_ids: list[int] | None = None
    preferencia_ids: list[int] | None = None

    # Campos tipados y acotados.
    fuma: bool | None = None
    tiene_mascotas: bool | None = None
    horario: Literal['temprano', 'tarde', 'nocturno', 'flexible'] | None = None
    nivel_orden: int | None = Field(default=None, ge=1, le=5)
    ocupacion: Literal['estudiante', 'trabajador', 'ambos', 'otro'] | None = None
    genero: Literal['femenino', 'masculino', 'otro', 'prefiero_no_decir'] | None = None
    genero_preferido: Literal['femenino', 'masculino', 'mixto', 'indiferente'] | None = None
    edad: int | None = Field(default=None, ge=18, le=99)
    distrito_id: int | None = Field(default=None, gt=0)

    descripcion: str | None = Field(default=None, max_length=500)
    estado: Literal['activo','inactivo'] = 'activo'

    # Compatibilidad con clientes anteriores: texto libre opcional.
    habitos: str | None = None
    preferencias: str | None = None

    @field_validator('habito_ids', 'preferencia_ids')
    @classmethod
    def catalogos_unicos(cls, valor: list[int] | None) -> list[int] | None:
        if valor is None:
            return None
        if any(identificador <= 0 for identificador in valor):
            raise ValueError('Los identificadores del catálogo deben ser positivos')
        unicos = list(dict.fromkeys(valor))
        if len(unicos) > 15:
            raise ValueError('Selecciona como máximo 15 opciones por catálogo')
        return unicos

    @field_validator('descripcion')
    @classmethod
    def descripcion_util(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        valor = valor.strip()
        if not valor:
            return None
        if len(valor) < 10:
            raise ValueError('La descripción debe tener al menos 10 caracteres')
        return valor

    @model_validator(mode='after')
    def presupuesto_ordenado(self):
        if self.presupuesto_max < self.presupuesto_min:
            raise ValueError('El presupuesto máximo debe ser mayor o igual al mínimo')
        return self


class PerfilSalida(PerfilEntrada, LecturaBase):
    perfil_id: int
    buscador_id: int
    habito_nombres: list[str] = Field(default_factory=list)
    preferencia_nombres: list[str] = Field(default_factory=list)
    distrito_completo: str | None = None
    actualizado_en: datetime | None = None


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
    habito_ids: list[int] = Field(default_factory=list)
    habito_nombres: list[str] = Field(default_factory=list)
    preferencia_ids: list[int] = Field(default_factory=list)
    preferencia_nombres: list[str] = Field(default_factory=list)
    fuma: bool | None = None
    tiene_mascotas: bool | None = None
    horario: str | None = None
    nivel_orden: int | None = None
    ocupacion: str | None = None
    genero: str | None = None
    genero_preferido: str | None = None
    edad: int | None = None
    distrito_id: int | None = None
    distrito_completo: str | None = None
    compatibilidad: int = 0
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


class HabitoCatalogoSalida(LecturaBase):
    habito_id: int
    nombre: str
    categoria: str
    orden: int = 0
    activo: bool = True


class PreferenciaCatalogoSalida(LecturaBase):
    preferencia_id: int
    nombre: str
    categoria: str
    orden: int = 0
    activo: bool = True


class OpcionSalida(BaseModel):
    valor: str
    etiqueta: str


class OpcionesPerfilSalida(BaseModel):
    horarios: list[OpcionSalida]
    ocupaciones: list[OpcionSalida]
    generos: list[OpcionSalida]
    generos_preferidos: list[OpcionSalida]


class CatalogosSalida(BaseModel):
    habitos: list[HabitoCatalogoSalida]
    preferencias: list[PreferenciaCatalogoSalida]
    opciones: OpcionesPerfilSalida


# --- UBIGEO -----------------------------------------------------------------

class DistritoSalida(LecturaBase):
    distrito_id: int
    codigo: str
    nombre: str


class ProvinciaSalida(LecturaBase):
    provincia_id: int
    codigo: str
    nombre: str
    distritos: list[DistritoSalida] = Field(default_factory=list)


class DepartamentoSalida(LecturaBase):
    departamento_id: int
    codigo: str
    nombre: str
    provincias: list[ProvinciaSalida] = Field(default_factory=list)


# --- Catálogos administrables -------------------------------------------------

class TipoAlojamientoSalida(LecturaBase):
    tipo_id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    orden: int
    activo: bool


class TipoAlojamientoEntrada(BaseModel):
    codigo: str = Field(min_length=2, max_length=40, pattern=r'^[a-z0-9_]+$')
    nombre: str = Field(min_length=2, max_length=60)
    descripcion: str | None = Field(default=None, max_length=200)
    orden: int = Field(default=0, ge=0, le=999)


class TipoAlojamientoEditar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=60)
    descripcion: str | None = Field(default=None, max_length=200)
    orden: int | None = Field(default=None, ge=0, le=999)
    activo: bool | None = None


class EstadoCatalogoSalida(LecturaBase):
    dominio: str
    codigo: str
    nombre: str
    descripcion: str | None = None
    orden: int
    activo: bool


class EstadoCatalogoEditar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=60)
    descripcion: str | None = Field(default=None, max_length=200)
    orden: int | None = Field(default=None, ge=0, le=999)
    activo: bool | None = None


class HabitoCatalogoEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    categoria: Literal['convivencia', 'rutina', 'ocio'] = 'convivencia'
    orden: int = Field(default=0, ge=0, le=999)
    activo: bool = True


class HabitoCatalogoEditar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    categoria: Literal['convivencia', 'rutina', 'ocio'] | None = None
    orden: int | None = Field(default=None, ge=0, le=999)
    activo: bool | None = None


class PreferenciaCatalogoEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    categoria: Literal['convivencia', 'perfil'] = 'convivencia'
    orden: int = Field(default=0, ge=0, le=999)
    activo: bool = True


class PreferenciaCatalogoEditar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    categoria: Literal['convivencia', 'perfil'] | None = None
    orden: int | None = Field(default=None, ge=0, le=999)
    activo: bool | None = None


class CatalogosAlojamientoSalida(BaseModel):
    tipos: list[TipoAlojamientoSalida]
    departamentos: list[DepartamentoSalida]


class CatalogosAdminSalida(BaseModel):
    tipos: list[TipoAlojamientoSalida]
    estados: list[EstadoCatalogoSalida]
    habitos: list[HabitoCatalogoSalida]
    preferencias: list[PreferenciaCatalogoSalida]
