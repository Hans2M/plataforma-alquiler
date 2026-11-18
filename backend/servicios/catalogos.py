"""Casos de uso de catálogos administrables e UBIGEO."""

from dominio.errores import Conflicto, NoEncontrado
from dominio.puertos import RepositorioCatalogos
from esquemas.datos import (
    EstadoCatalogoEditar,
    HabitoCatalogoEditar,
    HabitoCatalogoEntrada,
    PreferenciaCatalogoEditar,
    PreferenciaCatalogoEntrada,
    TipoAlojamientoEditar,
    TipoAlojamientoEntrada,
)
from modelos.catalogos import CatalogoEstado, TipoAlojamiento
from modelos.perfil_companero import CatalogoHabito, CatalogoPreferencia
from modelos.ubigeo import Departamento


class ServicioCatalogos:
    """Lectura pública y edición administrativa de catálogos.

    Los códigos de estado no se crean ni renombran desde la API: la lógica
    de la aplicación los compara. Solo se editan etiqueta, descripción,
    orden y visibilidad.
    """

    def __init__(self, catalogos: RepositorioCatalogos) -> None:
        self.catalogos = catalogos

    # --- Lectura ------------------------------------------------------------
    def tipos(self, incluir_inactivos: bool = False) -> list[TipoAlojamiento]:
        return self.catalogos.tipos(incluir_inactivos)

    def ubigeo(self) -> list[Departamento]:
        return self.catalogos.departamentos()

    def estados(
        self, dominio: str | None = None, incluir_inactivos: bool = False
    ) -> list[CatalogoEstado]:
        return self.catalogos.estados(dominio, incluir_inactivos)

    def habitos(self, incluir_inactivos: bool = False) -> list[CatalogoHabito]:
        return self.catalogos.habitos(incluir_inactivos)

    def preferencias(
        self, incluir_inactivos: bool = False
    ) -> list[CatalogoPreferencia]:
        return self.catalogos.preferencias(incluir_inactivos)

    # --- Tipos de alojamiento ----------------------------------------------
    def crear_tipo(self, datos: TipoAlojamientoEntrada) -> TipoAlojamiento:
        if self.catalogos.tipo_por_codigo(datos.codigo) is not None:
            raise Conflicto("Ya existe un tipo con ese código")
        if self.catalogos.tipo_por_nombre(datos.nombre) is not None:
            raise Conflicto("Ya existe un tipo con ese nombre")
        tipo = TipoAlojamiento(**datos.model_dump())
        self.catalogos.agregar_tipo(tipo)
        return tipo

    def editar_tipo(
        self, tipo_id: int, datos: TipoAlojamientoEditar
    ) -> TipoAlojamiento:
        tipo = self.catalogos.tipo(tipo_id)
        if tipo is None:
            raise NoEncontrado("Tipo de alojamiento no encontrado")
        cambios = datos.model_dump(exclude_unset=True)
        nombre = cambios.get("nombre")
        if nombre:
            existente = self.catalogos.tipo_por_nombre(nombre)
            if existente is not None and existente.tipo_id != tipo.tipo_id:
                raise Conflicto("Ya existe un tipo con ese nombre")
        for clave, valor in cambios.items():
            setattr(tipo, clave, valor)
        return tipo

    # --- Estados ------------------------------------------------------------
    def editar_estado(
        self, dominio: str, codigo: str, datos: EstadoCatalogoEditar
    ) -> CatalogoEstado:
        estado = self.catalogos.estado(dominio, codigo)
        if estado is None:
            raise NoEncontrado("Estado no encontrado")
        for clave, valor in datos.model_dump(exclude_unset=True).items():
            setattr(estado, clave, valor)
        return estado

    # --- Hábitos ------------------------------------------------------------
    def crear_habito(self, datos: HabitoCatalogoEntrada) -> CatalogoHabito:
        if self.catalogos.habito_por_nombre(datos.nombre) is not None:
            raise Conflicto("Ya existe un hábito con ese nombre")
        habito = CatalogoHabito(**datos.model_dump())
        self.catalogos.agregar_habito(habito)
        return habito

    def editar_habito(
        self, habito_id: int, datos: HabitoCatalogoEditar
    ) -> CatalogoHabito:
        habito = self.catalogos.habito(habito_id)
        if habito is None:
            raise NoEncontrado("Hábito no encontrado")
        cambios = datos.model_dump(exclude_unset=True)
        nombre = cambios.get("nombre")
        if nombre:
            existente = self.catalogos.habito_por_nombre(nombre)
            if existente is not None and existente.habito_id != habito.habito_id:
                raise Conflicto("Ya existe un hábito con ese nombre")
        for clave, valor in cambios.items():
            setattr(habito, clave, valor)
        return habito

    # --- Preferencias -------------------------------------------------------
    def crear_preferencia(
        self, datos: PreferenciaCatalogoEntrada
    ) -> CatalogoPreferencia:
        if self.catalogos.preferencia_por_nombre(datos.nombre) is not None:
            raise Conflicto("Ya existe una preferencia con ese nombre")
        preferencia = CatalogoPreferencia(**datos.model_dump())
        self.catalogos.agregar_preferencia(preferencia)
        return preferencia

    def editar_preferencia(
        self, preferencia_id: int, datos: PreferenciaCatalogoEditar
    ) -> CatalogoPreferencia:
        preferencia = self.catalogos.preferencia(preferencia_id)
        if preferencia is None:
            raise NoEncontrado("Preferencia no encontrada")
        cambios = datos.model_dump(exclude_unset=True)
        nombre = cambios.get("nombre")
        if nombre:
            existente = self.catalogos.preferencia_por_nombre(nombre)
            if (
                existente is not None
                and existente.preferencia_id != preferencia.preferencia_id
            ):
                raise Conflicto("Ya existe una preferencia con ese nombre")
        for clave, valor in cambios.items():
            setattr(preferencia, clave, valor)
        return preferencia
