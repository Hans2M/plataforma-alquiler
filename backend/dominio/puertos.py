"""Puertos (interfaces) que los servicios usan para acceder a persistencia.

Los servicios dependen de estos Protocol, no de las clases concretas de
repositorios, de modo que puedan probarse con dobles en memoria.

Nota de alcance: las entidades siguen siendo los modelos SQLAlchemy. Separar
entidades de dominio puras es un siguiente paso; aquí ya se invierte la
dependencia respecto a los repositorios concretos.
"""

from typing import Protocol

from dominio.consultas import CoincidenciaCompanero
from modelos.alojamiento import Alojamiento, Comodidad, ImagenAlojamiento
from modelos.perfil_companero import PerfilCompanero
from modelos.registro_acceso import RegistroAcceso
from modelos.usuario import Usuario
from modelos.verificacion_identidad import VerificacionIdentidad


class RepositorioUsuarios(Protocol):
    def por_correo(self, correo: str) -> Usuario | None: ...

    def por_documento(self, documento: str) -> Usuario | None: ...

    def por_id(self, uid: int) -> Usuario | None: ...

    def agregar(self, usuario: Usuario) -> None: ...

    def agregar_buscador(self, uid: int) -> None: ...

    def agregar_arrendador(self, uid: int, ruc: str | None) -> None: ...

    def listar(self, limite: int = 100) -> list[Usuario]: ...


class RepositorioAccesos(Protocol):
    def registrar(
        self,
        usuario_id: int,
        accion: str,
        ip: str | None = None,
        dispositivo: str | None = None,
    ) -> None: ...

    def de_usuario(self, uid: int) -> list[RegistroAcceso]: ...


class RepositorioAlojamientos(Protocol):
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
    ) -> list[Alojamiento]: ...

    def de_arrendador(self, uid: int) -> list[Alojamiento]: ...

    def por_id(self, alojamiento_id: int) -> Alojamiento | None: ...

    def agregar(self, alojamiento: Alojamiento) -> None: ...

    def comodidades(self) -> list[Comodidad]: ...

    def comodidades_validas(self, ids: list[int]) -> bool: ...

    def asignar_comodidades(self, alojamiento_id: int, ids: list[int]) -> None: ...

    def imagenes_de(self, alojamiento_id: int) -> list[ImagenAlojamiento]: ...

    def imagen_por_id(self, imagen_id: int) -> ImagenAlojamiento | None: ...

    def agregar_imagen(self, imagen: ImagenAlojamiento) -> None: ...

    def propietario_de(self, alojamiento_id: int) -> Usuario | None: ...


class RepositorioCompaneros(Protocol):
    def por_buscador(self, uid: int) -> PerfilCompanero | None: ...

    def coincidencias(
        self, uid: int, perfil: PerfilCompanero
    ) -> list[CoincidenciaCompanero]: ...

    def agregar(self, perfil: PerfilCompanero) -> None: ...

    def catalogos(self) -> tuple[list, list]: ...

    def habitos_validos(self, ids: list[int]) -> bool: ...

    def preferencias_validas(self, ids: list[int]) -> bool: ...

    def asignar_habitos(self, perfil: PerfilCompanero, ids: list[int]) -> None: ...

    def asignar_preferencias(
        self, perfil: PerfilCompanero, ids: list[int]
    ) -> None: ...


class RepositorioVerificaciones(Protocol):
    def ultima_por_usuario(self, uid: int) -> VerificacionIdentidad | None: ...

    def pendientes(self) -> list[VerificacionIdentidad]: ...

    def por_id(self, verificacion_id: int, bloquear: bool = False) -> VerificacionIdentidad | None: ...

    def agregar(self, verificacion: VerificacionIdentidad) -> None: ...
