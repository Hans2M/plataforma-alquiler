import pytest

from dominio.errores import Conflicto, NoEncontrado
from modelos.usuario import Usuario
from pruebas.falsos import RepositorioUsuariosFalso
from servicios.administracion import ServicioAdministracion


def crear_usuario(repositorio: RepositorioUsuariosFalso, correo: str, rol: str) -> Usuario:
    usuario = Usuario(
        nombre_completo="Persona de prueba",
        correo=correo,
        clave_hash="hash",
        rol=rol,
        estado_cuenta="pendiente",
    )
    repositorio.agregar(usuario)
    return usuario


@pytest.fixture
def entorno():
    usuarios = RepositorioUsuariosFalso()
    return ServicioAdministracion(usuarios), usuarios


def test_admin_no_puede_suspenderse_a_si_mismo(entorno):
    servicio, _ = entorno
    admin = crear_usuario(servicio.usuarios, "admin@example.com", "administrador")

    with pytest.raises(Conflicto, match="tu propia cuenta"):
        servicio.cambiar_estado(admin, admin.usuario_id, "suspendida")


def test_admin_cambia_estado_de_otra_cuenta(entorno):
    servicio, _ = entorno
    admin = crear_usuario(servicio.usuarios, "admin@example.com", "administrador")
    objetivo = crear_usuario(servicio.usuarios, "ana@example.com", "buscador")

    actualizado = servicio.cambiar_estado(admin, objetivo.usuario_id, "verificada")

    assert actualizado.estado_cuenta == "verificada"


def test_usuario_inexistente(entorno):
    servicio, _ = entorno
    admin = crear_usuario(servicio.usuarios, "admin@example.com", "administrador")

    with pytest.raises(NoEncontrado):
        servicio.cambiar_estado(admin, 404, "suspendida")


def test_listar_usuarios_respeta_limite(entorno):
    servicio, _ = entorno
    for indice in range(5):
        crear_usuario(servicio.usuarios, f"persona{indice}@example.com", "buscador")

    assert len(servicio.listar_usuarios(limite=3)) == 3
