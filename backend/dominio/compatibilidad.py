"""Cálculo puro de compatibilidad entre perfiles de convivencia.

No depende de FastAPI, SQLAlchemy ni de la base de datos: recibe datos ya
resueltos y devuelve un porcentaje de 0 a 100. El presupuesto se valida
antes (debe existir solapamiento); este cálculo solo pondera afinidad por
hábitos, preferencias y campos tipados.
"""

from collections.abc import Sequence


def calcular_compatibilidad(
    *,
    habito_ids_a: Sequence[int],
    habito_ids_b: Sequence[int],
    preferencia_ids_a: Sequence[int],
    preferencia_ids_b: Sequence[int],
    fuma_a: bool | None = None,
    fuma_b: bool | None = None,
    tiene_mascotas_a: bool | None = None,
    tiene_mascotas_b: bool | None = None,
    horario_a: str | None = None,
    horario_b: str | None = None,
    nivel_orden_a: int | None = None,
    nivel_orden_b: int | None = None,
    ocupacion_a: str | None = None,
    ocupacion_b: str | None = None,
) -> int:
    """Devuelve 50 por el solo hecho de tener presupuestos compatibles.

    Suma hasta 20 puntos por hábitos en común y 20 por preferencias en
    común; los campos tipados aportan 5 puntos cada uno cuando ambos
    perfiles los declararon y coinciden.
    """

    puntos = 50
    puntos += min(20, 5 * len(set(habito_ids_a) & set(habito_ids_b)))
    puntos += min(20, 5 * len(set(preferencia_ids_a) & set(preferencia_ids_b)))

    if fuma_a is not None and fuma_a == fuma_b:
        puntos += 5
    if tiene_mascotas_a is not None and tiene_mascotas_a == tiene_mascotas_b:
        puntos += 5
    if horario_a is not None and horario_a == horario_b:
        puntos += 5
    if ocupacion_a is not None and ocupacion_a == ocupacion_b:
        puntos += 5
    if (
        nivel_orden_a is not None
        and nivel_orden_b is not None
        and abs(nivel_orden_a - nivel_orden_b) <= 1
    ):
        puntos += 5

    return min(100, puntos)
