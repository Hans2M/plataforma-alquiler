from decimal import Decimal

import pytest

from dominio.errores import Conflicto, NoEncontrado
from esquemas.datos import (
    EstadoCatalogoEditar,
    HabitoCatalogoEntrada,
    PreferenciaCatalogoEntrada,
    TipoAlojamientoEditar,
    TipoAlojamientoEntrada,
)
from pruebas.falsos import RepositorioCatalogosFalso
from servicios.catalogos import ServicioCatalogos


@pytest.fixture
def entorno():
    repositorio = RepositorioCatalogosFalso()
    return ServicioCatalogos(repositorio), repositorio


def test_tipos_activos_por_defecto_y_todos_para_administracion(entorno):
    servicio, _ = entorno

    activos = servicio.tipos()
    todos = servicio.tipos(incluir_inactivos=True)

    assert [t.codigo for t in activos] == ["habitacion", "departamento"]
    assert "casa" in [t.codigo for t in todos]


def test_ubigeo_devuelve_arbol_departamento_provincia_distrito(entorno):
    servicio, _ = entorno

    departamentos = servicio.ubigeo()

    assert [d.nombre for d in departamentos] == ["Huánuco", "Lima"]
    huanuco = departamentos[0]
    assert [p.nombre for p in huanuco.provincias] == ["Leoncio Prado"]
    assert [d.nombre for d in huanuco.provincias[0].distritos] == [
        "Rupa-Rupa",
        "Huánuco",
    ]


def test_crear_tipo_valida_codigo_y_nombre_unicos(entorno):
    servicio, _ = entorno

    creado = servicio.crear_tipo(
        TipoAlojamientoEntrada(
            codigo="loft", nombre="Loft", descripcion="Espacio tipo loft", orden=50
        )
    )

    assert creado.tipo_id == 10
    with pytest.raises(Conflicto, match="código"):
        servicio.crear_tipo(TipoAlojamientoEntrada(codigo="loft", nombre="Otro"))
    with pytest.raises(Conflicto, match="nombre"):
        servicio.crear_tipo(TipoAlojamientoEntrada(codigo="loft2", nombre="Loft"))


def test_editar_tipo_permite_desactivar_sin_borrar(entorno):
    servicio, repositorio = entorno

    actualizado = servicio.editar_tipo(
        1, TipoAlojamientoEditar(nombre="Cuarto", activo=False)
    )

    assert actualizado.nombre == "Cuarto"
    assert actualizado.activo is False
    assert repositorio.tipos_catalogo[1] is actualizado
    assert "habitacion" not in [t.codigo for t in servicio.tipos()]


def test_editar_tipo_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(NoEncontrado, match="Tipo"):
        servicio.editar_tipo(99, TipoAlojamientoEditar(nombre="Fantasma"))


def test_editar_estado_cambia_solo_etiqueta_y_visibilidad(entorno):
    servicio, _ = entorno

    estado = servicio.editar_estado(
        "alojamiento",
        "activo",
        EstadoCatalogoEditar(nombre="Publicado", orden=5, activo=False),
    )

    assert estado.codigo == "activo"
    assert estado.nombre == "Publicado"
    assert estado.activo is False


def test_editar_estado_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(NoEncontrado, match="Estado"):
        servicio.editar_estado(
            "alojamiento", "inexistente", EstadoCatalogoEditar(nombre="Estado fantasma")
        )


def test_crear_habito_y_preferencia_con_nombre_unico(entorno):
    servicio, _ = entorno

    habito = servicio.crear_habito(
        HabitoCatalogoEntrada(nombre="Toco guitarra", categoria="ocio", orden=80)
    )
    preferencia = servicio.crear_preferencia(
        PreferenciaCatalogoEntrada(nombre="Compañero nocturno", orden=90)
    )

    assert habito.nombre == "Toco guitarra"
    assert preferencia.nombre == "Compañero nocturno"
    with pytest.raises(Conflicto, match="hábito"):
        servicio.crear_habito(HabitoCatalogoEntrada(nombre="Toco guitarra"))
    with pytest.raises(Conflicto, match="preferencia"):
        servicio.crear_preferencia(
            PreferenciaCatalogoEntrada(nombre="Compañero nocturno")
        )
