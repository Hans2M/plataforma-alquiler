from dominio.consultas import CoincidenciaCompanero
from dominio.errores import NoEncontrado, SolicitudInvalida
from dominio.puertos import RepositorioCompaneros
from esquemas.datos import PerfilEntrada
from modelos.perfil_companero import CatalogoHabito, CatalogoPreferencia, PerfilCompanero

# Valores aceptados por el perfil; la base los refuerza con CHECK.
GENEROS = {"femenino", "masculino", "otro", "prefiero_no_decir"}
GENEROS_PREFERIDOS = {"femenino", "masculino", "mixto", "indiferente"}


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
        if valores.get("distrito_id") is not None:
            if self.companeros.distrito(valores["distrito_id"]) is None:
                raise SolicitudInvalida("El distrito indicado no existe")
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

    def coincidencias(
        self,
        uid: int,
        edad_min: int | None = None,
        edad_max: int | None = None,
        genero: str | None = None,
        genero_preferido: str | None = None,
        mismo_distrito: bool = False,
    ) -> list[CoincidenciaCompanero]:
        perfil = self.companeros.por_buscador(uid)
        if perfil is None or perfil.estado != "activo":
            raise SolicitudInvalida("Debes tener un perfil activo")

        if (
            edad_min is not None
            and edad_max is not None
            and edad_min > edad_max
        ):
            raise SolicitudInvalida(
                "La edad mínima no puede superar a la edad máxima"
            )
        if genero is not None and genero not in GENEROS:
            raise SolicitudInvalida("El género indicado no es válido")
        if (
            genero_preferido is not None
            and genero_preferido not in GENEROS_PREFERIDOS
        ):
            raise SolicitudInvalida(
                "La preferencia de género indicada no es válida"
            )

        filtros = {
            "edad_min": edad_min,
            "edad_max": edad_max,
            "genero": genero,
            "genero_preferido": genero_preferido,
            "mismo_distrito": mismo_distrito,
        }
        return self.companeros.coincidencias(uid, perfil, filtros)

    def catalogos(self) -> tuple[list[CatalogoHabito], list[CatalogoPreferencia]]:
        return self.companeros.catalogos()
