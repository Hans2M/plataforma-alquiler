from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.alojamiento import (
    Alojamiento,
    AlojamientoComodidad,
    Comodidad,
    ImagenAlojamiento,
)
from modelos.catalogos import TipoAlojamiento
from modelos.ubigeo import Departamento, Distrito, Provincia
from modelos.usuario import Usuario


class RepositorioAlojamientosSQLAlchemy:
    """Implementación del puerto RepositorioAlojamientos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar(
        self,
        distrito: str | None,
        tipo: str | None,
        precio_max: float | None,
        texto: str | None,
        pagina: int,
        limite: int,
        precio_min: float | None = None,
        dias: int | None = None,
        orden: str = "recientes",
        distrito_id: int | None = None,
        provincia_id: int | None = None,
        departamento_id: int | None = None,
    ) -> list[Alojamiento]:
        st = select(Alojamiento).where(Alojamiento.estado == "activo")
        if distrito:
            st = st.where(Alojamiento.distrito.ilike(f"%{distrito.strip()}%"))
        if tipo:
            st = st.where(Alojamiento.tipo.ilike(f"%{tipo.strip()}%"))
        if distrito_id is not None:
            st = st.where(Alojamiento.distrito_id == distrito_id)
        if provincia_id is not None or departamento_id is not None:
            st = st.join(
                Distrito, Distrito.distrito_id == Alojamiento.distrito_id
            )
            if provincia_id is not None:
                st = st.where(Distrito.provincia_id == provincia_id)
            if departamento_id is not None:
                st = st.join(
                    Provincia, Provincia.provincia_id == Distrito.provincia_id
                ).where(Provincia.departamento_id == departamento_id)
        if precio_min is not None:
            st = st.where(Alojamiento.precio >= precio_min)
        if precio_max is not None:
            st = st.where(Alojamiento.precio <= precio_max)
        if texto:
            st = st.where(Alojamiento.titulo.ilike(f"%{texto.strip()}%"))
        if dias is not None:
            desde = datetime.now(timezone.utc) - timedelta(days=dias)
            st = st.where(Alojamiento.fecha_publicacion >= desde)

        criterios = {
            "precio_asc": (
                Alojamiento.precio.asc(),
                Alojamiento.fecha_publicacion.desc(),
            ),
            "precio_desc": (
                Alojamiento.precio.desc(),
                Alojamiento.fecha_publicacion.desc(),
            ),
        }.get(
            orden,
            # Por defecto: destacados y luego los más recientes.
            (Alojamiento.destacado.desc(), Alojamiento.fecha_publicacion.desc()),
        )
        return list(
            self.db.scalars(
                st.order_by(*criterios)
                .offset((pagina - 1) * limite)
                .limit(limite)
            )
        )

    def de_arrendador(self, uid: int) -> list[Alojamiento]:
        return list(
            self.db.scalars(
                select(Alojamiento)
                .where(Alojamiento.arrendador_id == uid)
                .order_by(Alojamiento.fecha_publicacion.desc())
            )
        )

    def por_id(self, alojamiento_id: int) -> Alojamiento | None:
        return self.db.get(Alojamiento, alojamiento_id)

    def agregar(self, alojamiento: Alojamiento) -> None:
        self.db.add(alojamiento)
        self.db.flush()

    def comodidades(self) -> list[Comodidad]:
        return list(self.db.scalars(select(Comodidad).order_by(Comodidad.nombre)))

    def comodidades_validas(self, ids: list[int]) -> bool:
        if not ids:
            return True
        encontrados = set(
            self.db.scalars(
                select(Comodidad.comodidad_id).where(Comodidad.comodidad_id.in_(set(ids)))
            )
        )
        return encontrados == set(ids)

    def asignar_comodidades(self, alojamiento_id: int, ids: list[int]) -> None:
        for item in list(
            self.db.scalars(
                select(AlojamientoComodidad).where(
                    AlojamientoComodidad.alojamiento_id == alojamiento_id
                )
            )
        ):
            self.db.delete(item)
        self.db.flush()
        for comodidad_id in set(ids):
            self.db.add(
                AlojamientoComodidad(
                    alojamiento_id=alojamiento_id,
                    comodidad_id=comodidad_id,
                )
            )

    def imagenes_de(self, alojamiento_id: int) -> list[ImagenAlojamiento]:
        return list(
            self.db.scalars(
                select(ImagenAlojamiento)
                .where(ImagenAlojamiento.alojamiento_id == alojamiento_id)
                .order_by(ImagenAlojamiento.orden)
            )
        )

    def imagen_por_id(self, imagen_id: int) -> ImagenAlojamiento | None:
        return self.db.get(ImagenAlojamiento, imagen_id)

    def agregar_imagen(self, imagen: ImagenAlojamiento) -> None:
        self.db.add(imagen)
        self.db.flush()

    def propietario_de(self, alojamiento_id: int) -> Usuario | None:
        alojamiento = self.db.get(Alojamiento, alojamiento_id)
        if alojamiento is None:
            return None
        return self.db.get(Usuario, alojamiento.arrendador_id)

    def distrito(self, distrito_id: int) -> Distrito | None:
        return self.db.get(Distrito, distrito_id)

    def tipo(self, tipo_id: int) -> TipoAlojamiento | None:
        return self.db.get(TipoAlojamiento, tipo_id)
