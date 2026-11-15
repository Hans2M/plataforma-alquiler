from dominio.errores import NoEncontrado
from dominio.puertos import RepositorioAccesos, RepositorioUsuarios
from esquemas.datos import UsuarioEdicion
from modelos.registro_acceso import RegistroAcceso
from modelos.usuario import Usuario


class ServicioUsuarios:
    """Casos de uso del perfil propio y su historial de acceso."""

    def __init__(
        self,
        accesos: RepositorioAccesos,
        usuarios: RepositorioUsuarios,
    ) -> None:
        self.accesos = accesos
        self.usuarios = usuarios

    def modificar_perfil(self, usuario: Usuario, cambios: UsuarioEdicion) -> Usuario:
        for campo, valor in cambios.model_dump(exclude_unset=True).items():
            setattr(usuario, campo, valor)
        return usuario

    def cambiar_foto(self, usuario: Usuario, ruta: str) -> str | None:
        """Asigna la nueva foto y devuelve la ruta anterior para eliminarla."""
        anterior = usuario.foto_perfil
        usuario.foto_perfil = ruta
        return anterior

    def quitar_foto(self, usuario: Usuario) -> str | None:
        anterior = usuario.foto_perfil
        usuario.foto_perfil = None
        return anterior

    def ruta_foto(self, uid: int) -> str:
        usuario = self.usuarios.por_id(uid)
        if usuario is None or not usuario.foto_perfil:
            raise NoEncontrado("Foto de perfil no disponible")
        return usuario.foto_perfil

    def accesos_de(self, uid: int) -> list[RegistroAcceso]:
        return self.accesos.de_usuario(uid)
