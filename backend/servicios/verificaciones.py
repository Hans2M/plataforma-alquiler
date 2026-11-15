from datetime import datetime, timezone

from dominio.errores import Conflicto, NoEncontrado, ValidacionInvalida
from dominio.puertos import RepositorioUsuarios, RepositorioVerificaciones
from modelos.usuario import Usuario
from modelos.verificacion_identidad import VerificacionIdentidad


class ServicioVerificaciones:
    """Solicitud y revisión de verificaciones de identidad."""

    def __init__(
        self,
        verificaciones: RepositorioVerificaciones,
        usuarios: RepositorioUsuarios,
    ) -> None:
        self.verificaciones = verificaciones
        self.usuarios = usuarios

    def estado(self, uid: int) -> VerificacionIdentidad | None:
        return self.verificaciones.ultima_por_usuario(uid)

    def validar_nueva_solicitud(self, uid: int) -> None:
        """Regla única para impedir solicitudes duplicadas.

        La API la invoca antes de guardar el archivo y crear_solicitud la
        vuelve a aplicar para no depender del orden de las llamadas.
        """
        ultima = self.verificaciones.ultima_por_usuario(uid)
        if ultima and ultima.estado in ("pendiente", "aprobada"):
            raise Conflicto("Ya existe una solicitud pendiente o aprobada")

    def crear_solicitud(self, uid: int, ruta: str) -> VerificacionIdentidad:
        self.validar_nueva_solicitud(uid)
        solicitud = VerificacionIdentidad(
            usuario_id=uid, ruta_documento=ruta, estado="pendiente"
        )
        self.verificaciones.agregar(solicitud)
        return solicitud

    def pendientes(self) -> list[VerificacionIdentidad]:
        return self.verificaciones.pendientes()

    def documento(self, verificacion_id: int) -> str:
        solicitud = self.verificaciones.por_id(verificacion_id)
        if solicitud is None:
            raise NoEncontrado("Solicitud inexistente")
        return solicitud.ruta_documento

    def revisar(
        self,
        verificacion_id: int,
        admin: Usuario,
        decision: str,
        observacion: str | None,
    ) -> VerificacionIdentidad:
        solicitud = self.verificaciones.por_id(verificacion_id, bloquear=True)
        if solicitud is None:
            raise NoEncontrado("Solicitud no encontrada")
        if solicitud.estado != "pendiente":
            raise Conflicto("Esta solicitud ya fue revisada")
        if decision == "rechazada" and not (observacion or "").strip():
            raise ValidacionInvalida("Debes registrar el motivo del rechazo")

        solicitud.estado = decision
        solicitud.revisor_id = admin.usuario_id
        solicitud.fecha_revision = datetime.now(timezone.utc)
        solicitud.observacion = observacion

        if decision == "aprobada":
            usuario = self.usuarios.por_id(solicitud.usuario_id)
            if usuario and usuario.estado_cuenta != "suspendida":
                usuario.estado_cuenta = "verificada"
        return solicitud
