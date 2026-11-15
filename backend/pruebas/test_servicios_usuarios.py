import pytest

from dominio.errores import NoEncontrado
from modelos.usuario import Usuario
from pruebas.falsos import RepositorioAccesosFalso, RepositorioUsuariosFalso
from servicios.usuarios import ServicioUsuarios


@pytest.fixture
def entorno():
    usuarios = RepositorioUsuariosFalso()
    accesos = RepositorioAccesosFalso()
    servicio = ServicioUsuarios(accesos, usuarios)
    usuario = Usuario(
        usuario_id=1,
        nombre_completo="Lucía Ramos",
        correo="lucia@example.com",
        clave_hash="hash",
        rol="buscador",
        estado_cuenta="verificada",
    )
    usuarios.agregar(usuario)
    return servicio, usuarios, usuario


def test_cambiar_foto_guarda_la_ruta_y_devuelve_la_anterior(entorno):
    servicio, _, usuario = entorno

    primera = servicio.cambiar_foto(usuario, "publicos/perfiles/1/uno.png")
    segunda = servicio.cambiar_foto(usuario, "publicos/perfiles/1/dos.png")

    assert primera is None
    assert segunda == "publicos/perfiles/1/uno.png"
    assert usuario.foto_perfil == "publicos/perfiles/1/dos.png"


def test_quitar_foto_devuelve_la_ruta_eliminada(entorno):
    servicio, _, usuario = entorno
    servicio.cambiar_foto(usuario, "publicos/perfiles/1/uno.png")

    anterior = servicio.quitar_foto(usuario)

    assert anterior == "publicos/perfiles/1/uno.png"
    assert usuario.foto_perfil is None


def test_ruta_foto_de_usuario_sin_imagen_no_existe(entorno):
    servicio, _, _ = entorno

    with pytest.raises(NoEncontrado, match="Foto"):
        servicio.ruta_foto(1)


def test_ruta_foto_de_usuario_inexistente_no_existe(entorno):
    servicio, _, _ = entorno

    with pytest.raises(NoEncontrado):
        servicio.ruta_foto(99)
