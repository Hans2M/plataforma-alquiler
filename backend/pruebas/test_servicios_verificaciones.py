import pytest

from dominio.errores import Conflicto, NoEncontrado, ValidacionInvalida
from modelos.usuario import Usuario
from pruebas.falsos import RepositorioUsuariosFalso, RepositorioVerificacionesFalso
from servicios.verificaciones import ServicioVerificaciones


def usuario(uid: int | None = None, estado: str = "pendiente") -> Usuario:
    return Usuario(
        usuario_id=uid,
        nombre_completo="Ana Torres",
        correo="ana@example.com",
        clave_hash="hash",
        rol="buscador",
        estado_cuenta=estado,
    )


def admin() -> Usuario:
    return Usuario(
        usuario_id=99,
        nombre_completo="Admin",
        correo="admin@example.com",
        clave_hash="hash",
        rol="administrador",
        estado_cuenta="verificada",
    )


@pytest.fixture
def entorno():
    verificaciones = RepositorioVerificacionesFalso()
    usuarios = RepositorioUsuariosFalso()
    usuarios.agregar(usuario())
    return ServicioVerificaciones(verificaciones, usuarios), verificaciones, usuarios


def test_crear_solicitud_y_bloquear_duplicados(entorno):
    servicio, repositorio, _ = entorno

    solicitud = servicio.crear_solicitud(1, "privados/dni/a.jpg")

    assert solicitud.verificacion_id == 1
    assert solicitud.estado == "pendiente"
    assert solicitud.ruta_documento == "privados/dni/a.jpg"

    with pytest.raises(Conflicto, match="pendiente o aprobada"):
        servicio.validar_nueva_solicitud(1)
    with pytest.raises(Conflicto, match="pendiente o aprobada"):
        servicio.crear_solicitud(1, "privados/dni/b.jpg")
    assert len(repositorio.items) == 1


def test_solicitud_aprobada_tambien_bloquea_una_nueva(entorno):
    servicio, _, _ = entorno
    servicio.crear_solicitud(1, "privados/dni/a.jpg")
    servicio.revisar(1, admin(), "aprobada", None)

    with pytest.raises(Conflicto):
        servicio.validar_nueva_solicitud(1)


def test_rechazo_exige_motivo_y_no_cambia_estado(entorno):
    servicio, repositorio, _ = entorno
    servicio.crear_solicitud(1, "privados/dni/a.jpg")

    with pytest.raises(ValidacionInvalida, match="motivo"):
        servicio.revisar(1, admin(), "rechazada", "   ")

    assert repositorio.items[1].estado == "pendiente"


def test_aprobacion_marca_cuenta_como_verificada(entorno):
    servicio, repositorio, usuarios = entorno
    servicio.crear_solicitud(1, "privados/dni/a.jpg")

    solicitud = servicio.revisar(1, admin(), "aprobada", "Documento legible")

    assert solicitud.estado == "aprobada"
    assert solicitud.revisor_id == 99
    assert solicitud.fecha_revision is not None
    assert solicitud.observacion == "Documento legible"
    assert usuarios.usuarios[1].estado_cuenta == "verificada"
    assert repositorio.items[1] is solicitud


def test_no_verifica_una_cuenta_suspendida(entorno):
    servicio, _, usuarios = entorno
    usuarios.usuarios[1].estado_cuenta = "suspendida"
    servicio.crear_solicitud(1, "privados/dni/a.jpg")

    servicio.revisar(1, admin(), "aprobada", None)

    assert usuarios.usuarios[1].estado_cuenta == "suspendida"


def test_no_se_puede_revisar_dos_veces(entorno):
    servicio, _, _ = entorno
    servicio.crear_solicitud(1, "privados/dni/a.jpg")
    servicio.revisar(1, admin(), "aprobada", None)

    with pytest.raises(Conflicto, match="ya fue revisada"):
        servicio.revisar(1, admin(), "rechazada", "Tarde")


def test_revisar_solicitud_inexistente(entorno):
    servicio, _, _ = entorno

    with pytest.raises(NoEncontrado):
        servicio.revisar(404, admin(), "aprobada", None)


def test_documento_de_solicitud_inexistente(entorno):
    servicio, _, _ = entorno

    with pytest.raises(NoEncontrado):
        servicio.documento(404)
