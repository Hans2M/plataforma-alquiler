from dominio.consultas import CoincidenciaCompanero
from dominio.errores import NoEncontrado, SolicitudInvalida
from dominio.puertos import RepositorioCompaneros
from esquemas.datos import PerfilEntrada
from modelos.perfil_companero import CatalogoHabito, CatalogoPreferencia, PerfilCompanero


class ServicioCompaneros:
    """Casos de uso del perfil de convivencia y sus coincidencias."""

    def __init__(self, companeros: RepositorioCompaneros) -> None:
        self.companeros = companeros

    def mi_perfil(self, uid: int) -> PerfilCompanero:
        perfil = self.companeros.por_buscador(uid)
        if perfil is None:
            raise NoEncontrado("Todavía no tienes perfil")
        return perfil

    def guardar_perfil(self, uid: int, datos: PerfilEntrada) -> PerfilCompanero:
        valores = datos.model_dump(exclude={"habito_ids", "preferencia_ids"})
        perfil = self.companeros.por_buscador(uid)
        if perfil is None:
            perfil = PerfilCompanero(buscador_id=uid, **valores)
            self.companeros.agregar(perfil)
        else:
            for clave, valor in valores.items():
                setattr(perfil, clave, valor)

        if datos.habito_ids is not None:
            if not self.companeros.habitos_validos(datos.habito_ids):
                raise SolicitudInvalida(
                    "Uno o más hábitos no existen o están inactivos"
                )
            self.companeros.asignar_habitos(perfil, datos.habito_ids)

        if datos.preferencia_ids is not None:
            if not self.companeros.preferencias_validas(datos.preferencia_ids):
                raise SolicitudInvalida(
                    "Una o más preferencias no existen o están inactivas"
                )
            self.companeros.asignar_preferencias(perfil, datos.preferencia_ids)

        return perfil

    def coincidencias(self, uid: int) -> list[CoincidenciaCompanero]:
        perfil = self.companeros.por_buscador(uid)
        if perfil is None or perfil.estado != "activo":
            raise SolicitudInvalida("Debes tener un perfil activo")
        return self.companeros.coincidencias(uid, perfil)

    def catalogos(self) -> tuple[list[CatalogoHabito], list[CatalogoPreferencia]]:
        return self.companeros.catalogos()
