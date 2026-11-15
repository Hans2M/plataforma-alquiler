"""Errores de negocio.

La capa de servicios lanza estas excepciones; la capa API las traduce a HTTP.
Así el dominio no depende de FastAPI.
"""


class ErrorDominio(Exception):
    """Error de regla de negocio con un mensaje apto para el cliente."""

    codigo = 400

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class SolicitudInvalida(ErrorDominio):
    codigo = 400


class NoAutorizado(ErrorDominio):
    codigo = 401


class Prohibido(ErrorDominio):
    codigo = 403


class NoEncontrado(ErrorDominio):
    codigo = 404


class Conflicto(ErrorDominio):
    codigo = 409


class ValidacionInvalida(ErrorDominio):
    codigo = 422
