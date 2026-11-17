from decimal import Decimal

import pytest

from dominio.errores import NoEncontrado, SolicitudInvalida
from esquemas.datos import PerfilEntrada
from pruebas.falsos import RepositorioCompanerosFalso
from servicios.companeros import ServicioCompaneros


@pytest.fixture
def entorno():
    repositorio = RepositorioCompanerosFalso()
    return ServicioCompaneros(repositorio), repositorio


def perfil(**cambios):
    base = {
        "presupuesto_min": Decimal("300"),
        "presupuesto_max": Decimal("600"),
        "habitos": "No fumo",
        "preferencias": "Ambiente tranquilo",
    }
    base.update(cambios)
    return PerfilEntrada(**base)


def test_mi_perfil_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(NoEncontrado, match="perfil"):
        servicio.mi_perfil(1)


def test_guardar_perfil_crea_y_luego_actualiza_sin_duplicar(entorno):
    servicio, repositorio = entorno

    creado = servicio.guardar_perfil(1, perfil())
    actualizado = servicio.guardar_perfil(
        1, perfil(presupuesto_min=Decimal("400"), descripcion="Actualizado")
    )

    assert creado is actualizado
    assert len(repositorio.perfiles) == 1
    assert actualizado.presupuesto_min == Decimal("400")
    assert actualizado.descripcion == "Actualizado"


def test_coincidencias_requiere_perfil_activo(entorno):
    servicio, _ = entorno

    with pytest.raises(SolicitudInvalida, match="perfil activo"):
        servicio.coincidencias(1)

    servicio.guardar_perfil(1, perfil(estado="inactivo"))
    with pytest.raises(SolicitudInvalida, match="perfil activo"):
        servicio.coincidencias(1)


def test_coincidencias_por_presupuesto_solapado(entorno):
    servicio, repositorio = entorno
    servicio.guardar_perfil(1, perfil())
    servicio.guardar_perfil(2, perfil(presupuesto_min=Decimal("500"), presupuesto_max=Decimal("800")))
    servicio.guardar_perfil(3, perfil(presupuesto_min=Decimal("1000"), presupuesto_max=Decimal("1200")))

    coincidencias = servicio.coincidencias(1)

    assert [p.buscador_id for p in coincidencias] == [2]
    assert len(repositorio.perfiles) == 3


def test_coincidencias_incluyen_perfil_publico_y_contacto(entorno):
    servicio, repositorio = entorno
    repositorio.contactos[2] = ("Carla Díaz", "934567890")
    repositorio.fotos[2] = True
    servicio.guardar_perfil(1, perfil())
    servicio.guardar_perfil(
        2,
        perfil(
            presupuesto_min=Decimal("500"),
            habitos="Lee por las noches",
            preferencias="Ambiente silencioso",
            descripcion="Busca un cuarto céntrico",
        ),
    )

    coincidencia = servicio.coincidencias(1)[0]

    assert coincidencia.nombre_completo == "Carla Díaz"
    assert coincidencia.telefono == "934567890"
    assert coincidencia.presupuesto_min == Decimal("500")
    assert coincidencia.presupuesto_max == Decimal("600")
    assert coincidencia.habitos == "Lee por las noches"
    assert coincidencia.preferencias == "Ambiente silencioso"
    assert coincidencia.descripcion == "Busca un cuarto céntrico"
    assert coincidencia.foto_perfil is True


def test_coincidencia_sin_telefono_sigue_siendo_visible(entorno):
    servicio, _ = entorno
    servicio.guardar_perfil(1, perfil())
    servicio.guardar_perfil(2, perfil(presupuesto_min=Decimal("500")))

    coincidencias = servicio.coincidencias(1)

    assert coincidencias[0].telefono is None


def test_perfil_guarda_catalogos_estructurados(entorno):
    servicio, _ = entorno

    guardado = servicio.guardar_perfil(
        1, perfil(habito_ids=[1, 3], preferencia_ids=[1])
    )

    assert guardado.habito_ids == [1, 3]
    assert guardado.habito_nombres == ["No fumo", "Leo"]
    assert guardado.preferencia_ids == [1]
    assert guardado.preferencia_nombres == ["Ambiente tranquilo"]


def test_perfil_rechaza_catalogo_inexistente(entorno):
    servicio, _ = entorno

    with pytest.raises(SolicitudInvalida, match="hábitos"):
        servicio.guardar_perfil(1, perfil(habito_ids=[99]))

    with pytest.raises(SolicitudInvalida, match="preferencias"):
        servicio.guardar_perfil(1, perfil(preferencia_ids=[99]))


def test_coincidencias_calculan_compatibilidad_por_afinidad(entorno):
    servicio, _ = entorno
    servicio.guardar_perfil(
        1,
        perfil(habito_ids=[1, 2], preferencia_ids=[1], fuma=False),
    )
    servicio.guardar_perfil(
        2,
        perfil(
            presupuesto_min=Decimal("500"),
            habito_ids=[1, 2],
            preferencia_ids=[1],
            fuma=False,
        ),
    )

    coincidencia = servicio.coincidencias(1)[0]

    # 50 por presupuesto + 10 por 2 hábitos + 5 por preferencia + 5 por fumar igual.
    assert coincidencia.compatibilidad == 70
    assert coincidencia.habito_nombres == ("No fumo", "Hago deporte")
    assert coincidencia.fuma is False


def test_coincidencias_ordenan_por_compatibilidad(entorno):
    servicio, _ = entorno
    servicio.guardar_perfil(1, perfil(habito_ids=[1, 2, 3]))
    servicio.guardar_perfil(2, perfil(presupuesto_min=Decimal("500")))
    servicio.guardar_perfil(
        3, perfil(presupuesto_min=Decimal("500"), habito_ids=[1, 2, 3])
    )

    coincidencias = servicio.coincidencias(1)

    assert [c.buscador_id for c in coincidencias] == [3, 2]
    assert coincidencias[0].compatibilidad > coincidencias[1].compatibilidad


def test_catalogos_disponibles_para_formulario(entorno):
    servicio, _ = entorno

    habitos, preferencias = servicio.catalogos()

    assert [h.nombre for h in habitos] == ["No fumo", "Hago deporte", "Leo"]
    assert [p.nombre for p in preferencias] == [
        "Ambiente tranquilo",
        "Buena comunicación",
    ]
