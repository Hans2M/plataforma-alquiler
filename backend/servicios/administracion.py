from dominio.errores import Conflicto, NoEncontrado
from dominio.puertos import RepositorioUsuarios
from modelos.usuario import Usuario


class ServicioAdministracion:
    """Casos de uso de supervisión de cuentas."""

    def __init__(self, usuarios: RepositorioUsuarios) -> None:
        self.usuarios = usuarios

    def listar_usuarios(self, limite: int = 100) -> list[Usuario]:
        return self.usuarios.listar(limite)

    def cambiar_estado(self, admin: Usuario, uid: int, estado: str) -> Usuario:
        objetivo = self.usuarios.por_id(uid)
        if objetivo is None:
            raise NoEncontrado("Usuario no encontrado")
        if objetivo.usuario_id == admin.usuario_id and estado == "suspendida":
            raise Conflicto("No puedes suspender tu propia cuenta")
        objetivo.estado_cuenta = estado
        return objetivo
