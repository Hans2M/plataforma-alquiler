"""Objetos de lectura que cruzan la frontera entre repositorios y servicios.

No son entidades persistidas: representan consultas de solo lectura con los
datos justos para la interfaz (por ejemplo, una coincidencia con el perfil
público y el teléfono de la otra persona).
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CoincidenciaCompanero:
    """Perfil de convivencia de otra persona con la que hay compatibilidad.

    ``foto_perfil`` solo indica si existe una imagen; la ruta interna nunca
    se publica. La interfaz arma la URL pública a partir de ``buscador_id``.
    """

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
    foto_perfil: bool = False


@dataclass(frozen=True)
class ContactoArrendador:
    arrendador_id: int
    nombre_completo: str
    telefono: str | None
    correo: str
