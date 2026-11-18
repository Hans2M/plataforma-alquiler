from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from dominio.errores import NoEncontrado, Prohibido, ValidacionInvalida
from esquemas.datos import AlojamientoEditar, AlojamientoEntrada
from modelos.usuario import Usuario
from pruebas.falsos import RepositorioAlojamientosFalso
from servicios.alojamientos import ServicioAlojamientos


@pytest.fixture
def entorno():
    repositorio = RepositorioAlojamientosFalso()
    return ServicioAlojamientos(repositorio), repositorio


def entrada(**cambios):
    base = {
        "titulo": "Habitación céntrica",
        "descripcion": "Habitación amoblada con escritorio",
        "precio": Decimal("450.00"),
        "direccion": "Av. Ejemplo 123",
        "distrito": "Tingo María",
        "tipo": "habitacion",
        "comodidad_ids": [1],
    }
    base.update(cambios)
    return AlojamientoEntrada(**base)


def test_crear_publicacion_asigna_propietario_y_comodidades(entorno):
    servicio, repositorio = entorno

    alojamiento = servicio.crear(5, entrada())

    assert alojamiento.alojamiento_id == 1
    assert alojamiento.arrendador_id == 5
    assert alojamiento.estado == "activo"
    assert alojamiento.destacado is False
    assert repositorio.comodidades_asignadas[1] == {1}


def test_crear_rechaza_comodidad_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(ValidacionInvalida, match="comodidad"):
        servicio.crear(5, entrada(comodidad_ids=[99]))


def test_crear_sin_comodidades_es_valido(entorno):
    servicio, repositorio = entorno

    alojamiento = servicio.crear(5, entrada(comodidad_ids=[]))

    assert repositorio.comodidades_asignadas[alojamiento.alojamiento_id] == set()


def test_modificar_solo_lo_permite_al_propietario(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada())

    with pytest.raises(Prohibido, match="propietario"):
        servicio.modificar(9, 1, AlojamientoEditar(titulo="Intento ajeno"))


def test_modificar_actualiza_campos_y_comodidades(entorno):
    servicio, repositorio = entorno
    servicio.crear(5, entrada())

    actualizado = servicio.modificar(
        5, 1, AlojamientoEditar(titulo="Nuevo título", comodidad_ids=[2])
    )

    assert actualizado.titulo == "Nuevo título"
    assert repositorio.comodidades_asignadas[1] == {2}


def test_modificar_rechaza_comodidad_inexistente(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada())

    with pytest.raises(ValidacionInvalida):
        servicio.modificar(5, 1, AlojamientoEditar(comodidad_ids=[99]))


def test_desactivar_exige_propietario_y_oculta_el_detalle(entorno):
    servicio, repositorio = entorno
    servicio.crear(5, entrada())

    with pytest.raises(Prohibido, match="propietario"):
        servicio.desactivar(9, 1)

    servicio.desactivar(5, 1)

    assert repositorio.items[1].estado == "inactivo"
    with pytest.raises(NoEncontrado, match="no disponible"):
        servicio.detalle(1)


def test_detalle_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(NoEncontrado):
        servicio.detalle(404)


def test_imagenes_de_publicacion_inactiva(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada())
    servicio.desactivar(5, 1)

    with pytest.raises(NoEncontrado, match="Publicación"):
        servicio.imagenes(1)


def test_registrar_imagen_valida_propiedad(entorno):
    servicio, repositorio = entorno
    servicio.crear(5, entrada())

    with pytest.raises(NoEncontrado, match="propia"):
        servicio.registrar_imagen(9, 1, "publicos/alojamientos/1/foto.jpg")

    imagen = servicio.registrar_imagen(5, 1, "publicos/alojamientos/1/foto.jpg")

    assert imagen.imagen_id == 1
    assert imagen.ruta_archivo == "publicos/alojamientos/1/foto.jpg"
    assert repositorio.imagenes[1] is imagen


def test_ruta_imagen_valida_publicacion_activa(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada())
    servicio.registrar_imagen(5, 1, "publicos/alojamientos/1/foto.jpg")

    assert servicio.ruta_imagen(1) == "publicos/alojamientos/1/foto.jpg"

    servicio.desactivar(5, 1)
    with pytest.raises(NoEncontrado, match="no publicada"):
        servicio.ruta_imagen(1)


def test_ruta_imagen_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(NoEncontrado, match="Imagen no encontrada"):
        servicio.ruta_imagen(99)


def test_busqueda_filtra_por_estado_y_precio(entorno):
    servicio, repositorio = entorno
    servicio.crear(5, entrada())
    servicio.crear(6, entrada(titulo="Suite cara", precio=Decimal("900.00")))

    resultados = servicio.buscar(None, None, 500, None, 1, 12)

    assert [a.titulo for a in resultados] == ["Habitación céntrica"]
    assert len(servicio.de_arrendador(6)) == 1
    assert repositorio.items[2].precio == Decimal("900.00")


def test_contacto_expone_nombre_y_telefono_del_arrendador(entorno):
    servicio, repositorio = entorno
    servicio.crear(5, entrada())
    repositorio.usuarios[5] = Usuario(
        usuario_id=5,
        nombre_completo="María Quispe",
        correo="maria@example.com",
        clave_hash="hash",
        rol="arrendador",
        estado_cuenta="verificada",
        telefono="987654321",
    )

    contacto = servicio.contacto(1)

    assert contacto.arrendador_id == 5
    assert contacto.nombre_completo == "María Quispe"
    assert contacto.telefono == "987654321"
    assert contacto.correo == "maria@example.com"


def test_contacto_de_publicacion_inactiva_no_se_expone(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada())
    servicio.desactivar(5, 1)

    with pytest.raises(NoEncontrado, match="no disponible"):
        servicio.contacto(1)


def test_busqueda_combina_tipo_y_rango_de_precio(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada())
    servicio.crear(5, entrada(titulo="Departamento", tipo="departamento", precio=Decimal("900.00")))
    servicio.crear(5, entrada(titulo="Habitación económica", precio=Decimal("150.00")))

    resultados = servicio.buscar(
        None, "habitacion", 800, None, 1, 12,
        precio_min=200,
    )

    assert [a.titulo for a in resultados] == ["Habitación céntrica"]


def test_busqueda_rechaza_rango_de_precio_invertido(entorno):
    servicio, _ = entorno

    with pytest.raises(ValidacionInvalida, match="precio mínimo"):
        servicio.buscar(None, None, 300, None, 1, 12, precio_min=600)


def test_busqueda_ordena_por_precio(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada(titulo="Cara", precio=Decimal("900.00")))
    servicio.crear(5, entrada(titulo="Barata", precio=Decimal("300.00")))
    servicio.crear(5, entrada(titulo="Media", precio=Decimal("600.00")))

    ascendente = servicio.buscar(None, None, None, None, 1, 12, orden="precio_asc")
    descendente = servicio.buscar(None, None, None, None, 1, 12, orden="precio_desc")

    assert [a.titulo for a in ascendente] == ["Barata", "Media", "Cara"]
    assert [a.titulo for a in descendente] == ["Cara", "Media", "Barata"]


def test_busqueda_por_fecha_de_publicacion_reciente(entorno):
    servicio, repositorio = entorno
    servicio.crear(5, entrada(titulo="Reciente"))
    servicio.crear(5, entrada(titulo="Antigua"))
    repositorio.items[1].fecha_publicacion = datetime.now(timezone.utc)
    repositorio.items[2].fecha_publicacion = datetime.now(timezone.utc) - timedelta(days=40)

    resultados = servicio.buscar(None, None, None, None, 1, 12, dias=7)

    assert [a.titulo for a in resultados] == ["Reciente"]


def test_crear_con_ubigeo_y_tipo_deriva_el_texto_historico(entorno):
    servicio, _ = entorno

    alojamiento = servicio.crear(
        5,
        AlojamientoEntrada(
            titulo="Departamento en Rupa-Rupa",
            descripcion="Cerca al centro de Tingo María",
            precio=Decimal("700.00"),
            direccion="Jr. Ejemplo 456",
            distrito_id=1,
            tipo_id=2,
            comodidad_ids=[],
        ),
    )

    assert alojamiento.distrito_id == 1
    assert alojamiento.distrito == "Rupa-Rupa"
    assert alojamiento.tipo_id == 2
    assert alojamiento.tipo == "departamento"


def test_crear_rechaza_distrito_o_tipo_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(ValidacionInvalida, match="distrito"):
        servicio.crear(5, entrada(distrito_id=999))

    with pytest.raises(ValidacionInvalida, match="tipo"):
        servicio.crear(5, entrada(tipo_id=999))

    # El tipo 3 existe pero está inactivo en el catálogo.
    with pytest.raises(ValidacionInvalida, match="inactivo"):
        servicio.crear(5, entrada(tipo_id=3))


def test_busqueda_filtra_por_ubigeo(entorno):
    servicio, _ = entorno
    servicio.crear(5, entrada(titulo="En Huánuco", distrito_id=2))
    servicio.crear(5, entrada(titulo="En Lima", distrito_id=3))
    servicio.crear(5, entrada(titulo="Sin ubigeo"))

    por_departamento = servicio.buscar(
        None, None, None, None, 1, 12, departamento_id=2
    )
    por_provincia = servicio.buscar(None, None, None, None, 1, 12, provincia_id=1)
    por_distrito = servicio.buscar(None, None, None, None, 1, 12, distrito_id=3)

    assert [a.titulo for a in por_departamento] == ["En Lima"]
    assert [a.titulo for a in por_provincia] == ["En Huánuco"]
    assert [a.titulo for a in por_distrito] == ["En Lima"]
