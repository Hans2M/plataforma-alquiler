import pytest

from dominio.errores import Conflicto, NoAutorizado, Prohibido
from esquemas.datos import Credenciales, RegistroArrendador, RegistroBuscador
from pruebas.falsos import RepositorioAccesosFalso, RepositorioUsuariosFalso
from servicios.autenticacion import ServicioAutenticacion


@pytest.fixture
def entorno():
    usuarios = RepositorioUsuariosFalso()
    accesos = RepositorioAccesosFalso()
    servicio = ServicioAutenticacion(
        usuarios,
        accesos,
        hasher=lambda clave: f"hash:{clave}",
        verificador=lambda clave, guardado: guardado == f"hash:{clave}",
        emisor_token=lambda uid: f"token-{uid}",
    )
    return servicio, usuarios, accesos


def datos_buscador(**cambios):
    base = {
        "nombre_completo": "Ana Torres",
        "correo": "ana@example.com",
        "contrasena": "unaClaveSegura1",
        "numero_documento": "12345678",
    }
    base.update(cambios)
    return RegistroBuscador(**base)


def test_registro_crea_usuario_extension_y_bitacora(entorno):
    servicio, usuarios, accesos = entorno

    usuario = servicio.registrar(datos_buscador(), "buscador", "127.0.0.1", "pytest")

    assert usuario.usuario_id == 1
    assert usuario.rol == "buscador"
    assert usuario.estado_cuenta == "pendiente"
    assert usuario.clave_hash == "hash:unaClaveSegura1"
    assert usuarios.buscadores == {1}
    assert accesos.registros[-1].accion == "registro"
    assert accesos.registros[-1].ip == "127.0.0.1"


def test_registro_arrendador_guarda_ruc(entorno):
    servicio, usuarios, _ = entorno
    datos = RegistroArrendador(
        nombre_completo="Luis Ríos",
        correo="luis@example.com",
        contrasena="otraClaveSegura",
        telefono="987654321",
        numero_documento="87654321",
        ruc="12345678901",
    )

    usuario = servicio.registrar(datos, "arrendador")

    assert usuario.rol == "arrendador"
    assert usuarios.arrendadores[usuario.usuario_id] == "12345678901"


def test_correo_duplicado_se_rechaza_sin_importar_mayusculas(entorno):
    servicio, _, _ = entorno
    servicio.registrar(datos_buscador(), "buscador")

    with pytest.raises(Conflicto, match="correo"):
        servicio.registrar(datos_buscador(correo="ANA@example.com"), "buscador")


def test_documento_duplicado_se_rechaza(entorno):
    servicio, _, _ = entorno
    servicio.registrar(datos_buscador(numero_documento="12345678"), "buscador")

    with pytest.raises(Conflicto, match="Documento"):
        servicio.registrar(
            datos_buscador(correo="otra@example.com", numero_documento="12345678"),
            "buscador",
        )


def test_ingreso_entrega_token_y_registra_acceso(entorno):
    servicio, _, accesos = entorno
    servicio.registrar(datos_buscador(), "buscador")

    respuesta = servicio.ingresar(
        Credenciales(correo="ana@example.com", contrasena="unaClaveSegura1")
    )

    assert respuesta == {"access_token": "token-1", "token_type": "bearer"}
    assert accesos.registros[-1].accion == "inicio_sesion"


def test_ingreso_con_clave_incorrecta_falla(entorno):
    servicio, _, _ = entorno
    servicio.registrar(datos_buscador(), "buscador")

    with pytest.raises(NoAutorizado):
        servicio.ingresar(
            Credenciales(correo="ana@example.com", contrasena="incorrecta")
        )


def test_cuenta_suspendida_no_puede_ingresar(entorno):
    servicio, usuarios, _ = entorno
    servicio.registrar(datos_buscador(), "buscador")
    usuarios.usuarios[1].estado_cuenta = "suspendida"

    with pytest.raises(Prohibido, match="suspendida"):
        servicio.ingresar(
            Credenciales(correo="ana@example.com", contrasena="unaClaveSegura1")
        )


def test_cierre_de_sesion_registra_accion(entorno):
    servicio, _, accesos = entorno

    servicio.cerrar_sesion(7, "10.0.0.1", "pytest")

    assert accesos.registros[-1].usuario_id == 7
    assert accesos.registros[-1].accion == "cierre_sesion"
