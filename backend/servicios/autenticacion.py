from collections.abc import Callable

from sqlalchemy.exc import IntegrityError

from dominio.errores import Conflicto, NoAutorizado, Prohibido
from dominio.puertos import RepositorioAccesos, RepositorioUsuarios
from esquemas.datos import Credenciales, RegistroArrendador, RegistroBuscador
from modelos.usuario import Usuario
from seguridad.autenticacion import crear_token, hash_clave, verificar_clave


class ServicioAutenticacion:
    """Casos de uso de registro, ingreso y cierre de sesión.

    No gestiona transacciones ni conoce FastAPI: recibe repositorios por
    constructor y lanza errores de dominio.
    """

    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        accesos: RepositorioAccesos,
        hasher: Callable[[str], str] = hash_clave,
        verificador: Callable[[str, str], bool] = verificar_clave,
        emisor_token: Callable[[int], str] = crear_token,
    ) -> None:
        self.usuarios = usuarios
        self.accesos = accesos
        self.hasher = hasher
        self.verificador = verificador
        self.emisor_token = emisor_token

    def registrar(
        self,
        datos: RegistroBuscador | RegistroArrendador,
        rol: str,
        ip: str | None = None,
        agente: str | None = None,
    ) -> Usuario:
        correo = str(datos.correo).strip().lower()
        if self.usuarios.por_correo(correo):
            raise Conflicto("Este correo ya está registrado")
        if datos.numero_documento and self.usuarios.por_documento(datos.numero_documento):
            raise Conflicto("Documento ya registrado")

        usuario = Usuario(
            nombre_completo=datos.nombre_completo.strip(),
            correo=correo,
            clave_hash=self.hasher(datos.contrasena),
            rol=rol,
            estado_cuenta="pendiente",
            telefono=datos.telefono,
            tipo_documento=datos.tipo_documento,
            numero_documento=datos.numero_documento,
        )
        try:
            self.usuarios.agregar(usuario)
            if rol == "buscador":
                self.usuarios.agregar_buscador(usuario.usuario_id)
            else:
                ruc = datos.ruc if isinstance(datos, RegistroArrendador) else None
                self.usuarios.agregar_arrendador(usuario.usuario_id, ruc)
            self.accesos.registrar(usuario.usuario_id, "registro", ip, agente)
        except IntegrityError as exc:
            raise Conflicto("Ya existe una cuenta con estos datos") from exc
        return usuario

    def ingresar(
        self,
        datos: Credenciales,
        ip: str | None = None,
        agente: str | None = None,
    ) -> dict[str, str]:
        usuario = self.usuarios.por_correo(str(datos.correo))
        if usuario is None or not self.verificador(
            datos.contrasena, usuario.clave_hash
        ):
            raise NoAutorizado("Correo o contraseña incorrectos")
        if usuario.estado_cuenta == "suspendida":
            raise Prohibido("Cuenta suspendida")
        self.accesos.registrar(usuario.usuario_id, "inicio_sesion", ip, agente)
        return {
            "access_token": self.emisor_token(usuario.usuario_id),
            "token_type": "bearer",
        }

    def cerrar_sesion(
        self, uid: int, ip: str | None = None, agente: str | None = None
    ) -> None:
        self.accesos.registrar(uid, "cierre_sesion", ip, agente)
