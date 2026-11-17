from sqlalchemy import select
from sqlalchemy.orm import Session

from dominio.compatibilidad import calcular_compatibilidad
from dominio.consultas import CoincidenciaCompanero
from modelos.perfil_companero import (
    CatalogoHabito,
    CatalogoPreferencia,
    PerfilCompanero,
)
from modelos.usuario import Usuario


class RepositorioCompanerosSQLAlchemy:
    """Implementación del puerto RepositorioCompaneros."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def por_buscador(self, uid: int) -> PerfilCompanero | None:
        return self.db.scalar(
            select(PerfilCompanero).where(PerfilCompanero.buscador_id == uid)
        )

    def coincidencias(
        self, uid: int, perfil: PerfilCompanero
    ) -> list[CoincidenciaCompanero]:
        stmt = (
            select(PerfilCompanero, Usuario)
            .join(Usuario, Usuario.usuario_id == PerfilCompanero.buscador_id)
            .where(
                PerfilCompanero.buscador_id != uid,
                PerfilCompanero.estado == "activo",
                PerfilCompanero.presupuesto_min <= perfil.presupuesto_max,
                PerfilCompanero.presupuesto_max >= perfil.presupuesto_min,
            )
            .limit(50)
        )
        resultados = [
            self._a_coincidencia(perfil, otro, usuario)
            for otro, usuario in self.db.execute(stmt)
        ]
        # Mejor compatibilidad primero; el id mantiene el orden estable.
        resultados.sort(key=lambda c: (-c.compatibilidad, c.perfil_id))
        return resultados

    def _a_coincidencia(
        self, perfil: PerfilCompanero, otro: PerfilCompanero, usuario: Usuario
    ) -> CoincidenciaCompanero:
        return CoincidenciaCompanero(
            perfil_id=otro.perfil_id,
            buscador_id=otro.buscador_id,
            nombre_completo=usuario.nombre_completo,
            telefono=usuario.telefono,
            presupuesto_min=otro.presupuesto_min,
            presupuesto_max=otro.presupuesto_max,
            habitos=otro.habitos,
            preferencias=otro.preferencias,
            descripcion=otro.descripcion,
            estado=otro.estado,
            foto_perfil=bool(usuario.foto_perfil),
            habito_ids=tuple(otro.habito_ids),
            habito_nombres=tuple(otro.habito_nombres),
            preferencia_ids=tuple(otro.preferencia_ids),
            preferencia_nombres=tuple(otro.preferencia_nombres),
            fuma=otro.fuma,
            tiene_mascotas=otro.tiene_mascotas,
            horario=otro.horario,
            nivel_orden=otro.nivel_orden,
            ocupacion=otro.ocupacion,
            genero=otro.genero,
            genero_preferido=otro.genero_preferido,
            edad=otro.edad,
            compatibilidad=calcular_compatibilidad(
                habito_ids_a=perfil.habito_ids,
                habito_ids_b=otro.habito_ids,
                preferencia_ids_a=perfil.preferencia_ids,
                preferencia_ids_b=otro.preferencia_ids,
                fuma_a=perfil.fuma,
                fuma_b=otro.fuma,
                tiene_mascotas_a=perfil.tiene_mascotas,
                tiene_mascotas_b=otro.tiene_mascotas,
                horario_a=perfil.horario,
                horario_b=otro.horario,
                nivel_orden_a=perfil.nivel_orden,
                nivel_orden_b=otro.nivel_orden,
                ocupacion_a=perfil.ocupacion,
                ocupacion_b=otro.ocupacion,
            ),
        )

    def agregar(self, perfil: PerfilCompanero) -> None:
        self.db.add(perfil)
        self.db.flush()

    def catalogos(self) -> tuple[list[CatalogoHabito], list[CatalogoPreferencia]]:
        habitos = list(
            self.db.scalars(
                select(CatalogoHabito)
                .where(CatalogoHabito.activo.is_(True))
                .order_by(CatalogoHabito.categoria, CatalogoHabito.orden, CatalogoHabito.nombre)
            )
        )
        preferencias = list(
            self.db.scalars(
                select(CatalogoPreferencia)
                .where(CatalogoPreferencia.activo.is_(True))
                .order_by(
                    CatalogoPreferencia.categoria,
                    CatalogoPreferencia.orden,
                    CatalogoPreferencia.nombre,
                )
            )
        )
        return habitos, preferencias

    def habitos_validos(self, ids: list[int]) -> bool:
        if not ids:
            return True
        encontrados = set(
            self.db.scalars(
                select(CatalogoHabito.habito_id).where(
                    CatalogoHabito.habito_id.in_(set(ids)),
                    CatalogoHabito.activo.is_(True),
                )
            )
        )
        return encontrados == set(ids)

    def preferencias_validas(self, ids: list[int]) -> bool:
        if not ids:
            return True
        encontrados = set(
            self.db.scalars(
                select(CatalogoPreferencia.preferencia_id).where(
                    CatalogoPreferencia.preferencia_id.in_(set(ids)),
                    CatalogoPreferencia.activo.is_(True),
                )
            )
        )
        return encontrados == set(ids)

    def asignar_habitos(self, perfil: PerfilCompanero, ids: list[int]) -> None:
        perfil.habitos_catalogo = list(
            self.db.scalars(
                select(CatalogoHabito).where(CatalogoHabito.habito_id.in_(set(ids)))
            )
        )

    def asignar_preferencias(self, perfil: PerfilCompanero, ids: list[int]) -> None:
        perfil.preferencias_catalogo = list(
            self.db.scalars(
                select(CatalogoPreferencia).where(
                    CatalogoPreferencia.preferencia_id.in_(set(ids))
                )
            )
        )
