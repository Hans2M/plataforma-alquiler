from dominio.consultas import CoincidenciaCompanero
from dominio.errores import NoEncontrado, SolicitudInvalida
from dominio.puertos import RepositorioCompaneros
from esquemas.datos import PerfilEntrada
from modelos.perfil_companero import PerfilCompanero


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
        perfil = self.companeros.por_buscador(uid)
        if perfil is None:
            perfil = PerfilCompanero(buscador_id=uid, **datos.model_dump())
            self.companeros.agregar(perfil)
        else:
            for clave, valor in datos.model_dump().items():
                setattr(perfil, clave, valor)
        return perfil

    def coincidencias(self, uid: int) -> list[CoincidenciaCompanero]:
        perfil = self.companeros.por_buscador(uid)
        if perfil is None or perfil.estado != "activo":
            raise SolicitudInvalida("Debes tener un perfil activo")
        return self.companeros.coincidencias(uid, perfil)
