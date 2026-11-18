"""Persistencia de catálogos: UBIGEO, tipos y estados administrables."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.catalogos import CatalogoEstado, TipoAlojamiento
from modelos.perfil_companero import CatalogoHabito, CatalogoPreferencia
from modelos.ubigeo import Departamento, Distrito


class RepositorioCatalogosSQLAlchemy:
    """Implementación del puerto RepositorioCatalogos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Tipos de alojamiento ---------------------------------------------
    def tipos(self, incluir_inactivos: bool = False) -> list[TipoAlojamiento]:
        st = select(TipoAlojamiento).order_by(
            TipoAlojamiento.orden, TipoAlojamiento.nombre
        )
        if not incluir_inactivos:
            st = st.where(TipoAlojamiento.activo.is_(True))
        return list(self.db.scalars(st))

    def tipo(self, tipo_id: int) -> TipoAlojamiento | None:
        return self.db.get(TipoAlojamiento, tipo_id)

    def tipo_por_codigo(self, codigo: str) -> TipoAlojamiento | None:
        return self.db.scalar(
            select(TipoAlojamiento).where(TipoAlojamiento.codigo == codigo)
        )

    def tipo_por_nombre(self, nombre: str) -> TipoAlojamiento | None:
        return self.db.scalar(
            select(TipoAlojamiento).where(
                TipoAlojamiento.nombre.ilike(nombre.strip())
            )
        )

    def agregar_tipo(self, tipo: TipoAlojamiento) -> None:
        self.db.add(tipo)
        self.db.flush()

    # --- Estados ------------------------------------------------------------
    def estados(
        self, dominio: str | None = None, incluir_inactivos: bool = False
    ) -> list[CatalogoEstado]:
        st = select(CatalogoEstado).order_by(
            CatalogoEstado.dominio, CatalogoEstado.orden, CatalogoEstado.codigo
        )
        if dominio:
            st = st.where(CatalogoEstado.dominio == dominio)
        if not incluir_inactivos:
            st = st.where(CatalogoEstado.activo.is_(True))
        return list(self.db.scalars(st))

    def estado(self, dominio: str, codigo: str) -> CatalogoEstado | None:
        return self.db.get(CatalogoEstado, (dominio, codigo))

    # --- Hábitos ------------------------------------------------------------
    def habitos(self, incluir_inactivos: bool = False) -> list[CatalogoHabito]:
        st = select(CatalogoHabito).order_by(
            CatalogoHabito.orden, CatalogoHabito.nombre
        )
        if not incluir_inactivos:
            st = st.where(CatalogoHabito.activo.is_(True))
        return list(self.db.scalars(st))

    def habito(self, habito_id: int) -> CatalogoHabito | None:
        return self.db.get(CatalogoHabito, habito_id)

    def habito_por_nombre(self, nombre: str) -> CatalogoHabito | None:
        return self.db.scalar(
            select(CatalogoHabito).where(CatalogoHabito.nombre.ilike(nombre.strip()))
        )

    def agregar_habito(self, habito: CatalogoHabito) -> None:
        self.db.add(habito)
        self.db.flush()

    # --- Preferencias -------------------------------------------------------
    def preferencias(
        self, incluir_inactivos: bool = False
    ) -> list[CatalogoPreferencia]:
        st = select(CatalogoPreferencia).order_by(
            CatalogoPreferencia.orden, CatalogoPreferencia.nombre
        )
        if not incluir_inactivos:
            st = st.where(CatalogoPreferencia.activo.is_(True))
        return list(self.db.scalars(st))

    def preferencia(self, preferencia_id: int) -> CatalogoPreferencia | None:
        return self.db.get(CatalogoPreferencia, preferencia_id)

    def preferencia_por_nombre(self, nombre: str) -> CatalogoPreferencia | None:
        return self.db.scalar(
            select(CatalogoPreferencia).where(
                CatalogoPreferencia.nombre.ilike(nombre.strip())
            )
        )

    def agregar_preferencia(self, preferencia: CatalogoPreferencia) -> None:
        self.db.add(preferencia)
        self.db.flush()

    # --- UBIGEO -------------------------------------------------------------
    def departamentos(self) -> list[Departamento]:
        # provincias y distritos usan lazy="selectin": 3 consultas, sin N+1.
        return list(
            self.db.scalars(
                select(Departamento).order_by(Departamento.nombre)
            )
        )

    def distrito(self, distrito_id: int) -> Distrito | None:
        return self.db.get(Distrito, distrito_id)
