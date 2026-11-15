from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import main
from api.dependencias import servicio_alojamientos, servicio_autenticacion, servicio_usuarios
from configuracion.configuracion import settings
from dominio.errores import Conflicto, NoEncontrado
from modelos.alojamiento import Alojamiento
from modelos.usuario import Usuario
from seguridad.autenticacion import usuario_actual


@pytest.fixture
def cliente():
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


def test_salud_no_depende_de_base_de_datos(cliente):
    respuesta = cliente.get("/api/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "servicio": "backend"}


def test_error_de_dominio_se_traduce_a_404(cliente):
    class ServicioFalso:
        def detalle(self, alojamiento_id):
            raise NoEncontrado("Alojamiento no disponible")

    main.app.dependency_overrides[servicio_alojamientos] = lambda: ServicioFalso()

    respuesta = cliente.get("/api/alojamientos/99")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Alojamiento no disponible"}


def test_error_de_dominio_se_traduce_a_409(cliente):
    class ServicioFalso:
        def registrar(self, datos, rol, ip=None, agente=None):
            raise Conflicto("Este correo ya está registrado")

    main.app.dependency_overrides[servicio_autenticacion] = lambda: ServicioFalso()

    respuesta = cliente.post(
        "/api/autenticacion/registro/buscador",
        json={
            "nombre_completo": "Ana Torres",
            "correo": "ana@example.com",
            "contrasena": "unaClaveSegura1",
            "numero_documento": "12345678",
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Este correo ya está registrado"}


def test_rol_no_autorizado_sigue_bloqueando(cliente):
    class ServicioFalso:
        def crear(self, uid, datos):
            raise AssertionError("No debería ejecutarse el caso de uso")

    main.app.dependency_overrides[servicio_alojamientos] = lambda: ServicioFalso()
    main.app.dependency_overrides[usuario_actual] = lambda: Usuario(
        usuario_id=1,
        nombre_completo="Buscador",
        correo="buscador@example.com",
        clave_hash="hash",
        rol="buscador",
        estado_cuenta="verificada",
    )

    respuesta = cliente.post(
        "/api/alojamientos",
        json={
            "titulo": "Habitación",
            "descripcion": "Habitación amoblada",
            "precio": 450,
            "direccion": "Av. Ejemplo 123",
            "distrito": "Tingo María",
            "tipo": "habitacion",
        },
    )

    assert respuesta.status_code == 403
    assert respuesta.json() == {"detail": "No autorizado para este rol"}


@pytest.mark.parametrize("rol", ["arrendador", "administrador"])
def test_contacto_solo_se_entrega_a_buscadores(cliente, rol):
    class ServicioFalso:
        def contacto(self, alojamiento_id):
            raise AssertionError("No debería ejecutarse el caso de uso")

    main.app.dependency_overrides[servicio_alojamientos] = lambda: ServicioFalso()
    main.app.dependency_overrides[usuario_actual] = lambda: Usuario(
        usuario_id=1,
        nombre_completo="Otra cuenta",
        correo="cuenta@example.com",
        clave_hash="hash",
        rol=rol,
        estado_cuenta="verificada",
    )

    respuesta = cliente.get("/api/alojamientos/7/contacto")

    assert respuesta.status_code == 403
    assert respuesta.json() == {"detail": "No autorizado para este rol"}


def test_publicacion_delega_en_el_servicio(cliente):
    class ServicioFalso:
        def crear(self, uid, datos):
            return Alojamiento(
                alojamiento_id=7,
                arrendador_id=uid,
                titulo=datos.titulo,
                descripcion=datos.descripcion,
                precio=datos.precio,
                direccion=datos.direccion,
                distrito=datos.distrito,
                tipo=datos.tipo,
                estado=datos.estado,
                destacado=False,
                fecha_publicacion=datetime.now(timezone.utc),
            )

    main.app.dependency_overrides[servicio_alojamientos] = lambda: ServicioFalso()
    main.app.dependency_overrides[usuario_actual] = lambda: Usuario(
        usuario_id=5,
        nombre_completo="Arrendador",
        correo="arrendador@example.com",
        clave_hash="hash",
        rol="arrendador",
        estado_cuenta="verificada",
    )

    respuesta = cliente.post(
        "/api/alojamientos",
        json={
            "titulo": "Habitación",
            "descripcion": "Habitación amoblada",
            "precio": 450,
            "direccion": "Av. Ejemplo 123",
            "distrito": "Tingo María",
            "tipo": "habitacion",
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["alojamiento_id"] == 7
    assert respuesta.json()["arrendador_id"] == 5


def _usuario_con_foto(usuario_id=7, foto_perfil=None):
    return Usuario(
        usuario_id=usuario_id,
        nombre_completo="Lucía Ramos",
        correo="lucia@example.com",
        clave_hash="hash",
        rol="buscador",
        estado_cuenta="verificada",
        foto_perfil=foto_perfil,
        fecha_registro=datetime.now(timezone.utc),
    )


def test_subir_foto_de_perfil_almacena_y_expone_solo_la_url(
    cliente, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "archivos_dir", tmp_path)

    class ServicioFalso:
        def cambiar_foto(self, usuario, ruta):
            anterior = usuario.foto_perfil
            usuario.foto_perfil = ruta
            return anterior

    main.app.dependency_overrides[servicio_usuarios] = lambda: ServicioFalso()
    main.app.dependency_overrides[usuario_actual] = lambda: _usuario_con_foto()

    respuesta = cliente.post(
        "/api/usuarios/me/foto",
        files={"archivo": ("perfil.png", b"\x89PNG\r\n\x1a\n" + b"0" * 64, "image/png")},
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["foto_url"] == "/api/usuarios/7/foto"
    assert "foto_perfil" not in datos
    almacenadas = list((tmp_path / "publicos" / "perfiles" / "7").iterdir())
    assert len(almacenadas) == 1
    assert almacenadas[0].read_bytes().startswith(b"\x89PNG")


def test_subir_foto_rechaza_formatos_que_no_son_imagen(cliente, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "archivos_dir", tmp_path)
    main.app.dependency_overrides[usuario_actual] = lambda: _usuario_con_foto()

    respuesta = cliente.post(
        "/api/usuarios/me/foto",
        files={"archivo": ("nota.txt", b"texto", "text/plain")},
    )

    assert respuesta.status_code == 415
    assert not (tmp_path / "publicos").exists()


def test_foto_de_perfil_se_sirve_publicamente(cliente, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "archivos_dir", tmp_path)
    destino = tmp_path / "publicos" / "perfiles" / "7" / "perfil.png"
    destino.parent.mkdir(parents=True)
    destino.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)

    class ServicioFalso:
        def ruta_foto(self, uid):
            return "publicos/perfiles/7/perfil.png"

    main.app.dependency_overrides[servicio_usuarios] = lambda: ServicioFalso()

    respuesta = cliente.get("/api/usuarios/7/foto")

    assert respuesta.status_code == 200
    assert respuesta.headers["cache-control"] == "no-cache"
    assert respuesta.content.startswith(b"\x89PNG")


def test_foto_inexistente_devuelve_404(cliente):
    class ServicioFalso:
        def ruta_foto(self, uid):
            raise NoEncontrado("Foto de perfil no disponible")

    main.app.dependency_overrides[servicio_usuarios] = lambda: ServicioFalso()

    respuesta = cliente.get("/api/usuarios/7/foto")

    assert respuesta.status_code == 404


def test_quitar_foto_elimina_el_archivo_anterior(cliente, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "archivos_dir", tmp_path)
    destino = tmp_path / "publicos" / "perfiles" / "7" / "perfil.png"
    destino.parent.mkdir(parents=True)
    destino.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)

    class ServicioFalso:
        def quitar_foto(self, usuario):
            usuario.foto_perfil = None
            return "publicos/perfiles/7/perfil.png"

    main.app.dependency_overrides[servicio_usuarios] = lambda: ServicioFalso()
    main.app.dependency_overrides[usuario_actual] = lambda: _usuario_con_foto(
        foto_perfil="publicos/perfiles/7/perfil.png"
    )

    respuesta = cliente.delete("/api/usuarios/me/foto")

    assert respuesta.status_code == 200
    assert respuesta.json()["foto_url"] is None
    assert not destino.exists()
