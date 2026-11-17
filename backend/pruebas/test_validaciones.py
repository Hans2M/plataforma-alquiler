import pytest
from pydantic import ValidationError
from esquemas.datos import PerfilEntrada, AlojamientoEntrada, RegistroArrendador, RegistroBuscador

def datos_buscador(**cambios):
    base = {
        'nombre_completo': 'Ana Torres',
        'correo': 'ana@example.com',
        'contrasena': 'unaClaveSegura1',
        'numero_documento': '12345678',
    }
    base.update(cambios)
    return RegistroBuscador(**base)

def test_presupuesto_invertido_rechazado():
    with pytest.raises(ValidationError):
        PerfilEntrada(presupuesto_min=800, presupuesto_max=200)

def test_precio_invalido_rechazado():
    with pytest.raises(ValidationError):
        AlojamientoEntrada(titulo='Habitacion',descripcion='Habitacion equipada',precio=0,direccion='Av. Ficticia 123',distrito='Tingo Maria',tipo='habitacion')

def test_entrada_valida():
    entrada = AlojamientoEntrada(titulo='Habitación céntrica',descripcion='Con escritorio y acceso',precio=250,direccion='Av. Ficticia 123',distrito='Tingo Maria',tipo='habitacion')
    assert entrada.estado == 'activo'

def test_dni_exige_exactamente_ocho_digitos():
    with pytest.raises(ValidationError, match='exactamente 8 dígitos'):
        datos_buscador(numero_documento='1234567')

def test_dni_no_admite_letras():
    with pytest.raises(ValidationError, match='exactamente 8 dígitos'):
        datos_buscador(numero_documento='1234ABCD')

def test_ce_exige_exactamente_nueve_digitos():
    with pytest.raises(ValidationError, match='exactamente 9 dígitos'):
        datos_buscador(tipo_documento='CE', numero_documento='12345678')

def test_pasaporte_alfanumerico_es_valido():
    datos = datos_buscador(tipo_documento='PASAPORTE', numero_documento='ab123456')
    assert datos.numero_documento == 'AB123456'

def test_documento_limpia_espacios_y_guiones():
    datos = datos_buscador(numero_documento=' 12-345-678 ')
    assert datos.numero_documento == '12345678'

def test_documento_es_obligatorio():
    with pytest.raises(ValidationError, match='Field required'):
        RegistroBuscador(
            nombre_completo='Ana Torres',
            correo='ana@example.com',
            contrasena='unaClaveSegura1',
        )

def test_telefono_debe_tener_entre_siete_y_nueve_digitos():
    with pytest.raises(ValidationError, match='entre 7 y 9 dígitos'):
        datos_buscador(telefono='123')

def test_telefono_valido_se_acepta():
    datos = datos_buscador(telefono='987654321')
    assert datos.telefono == '987654321'

def test_ruc_es_obligatorio_para_arrendador():
    with pytest.raises(ValidationError, match='Field required'):
        RegistroArrendador(
            nombre_completo='Luis Ríos',
            correo='luis@example.com',
            contrasena='otraClaveSegura',
            telefono='987654321',
            numero_documento='87654321',
        )

def test_ruc_exige_once_digitos():
    with pytest.raises(ValidationError, match='exactamente 11 dígitos'):
        RegistroArrendador(
            nombre_completo='Luis Ríos',
            correo='luis@example.com',
            contrasena='otraClaveSegura',
            telefono='987654321',
            numero_documento='87654321',
            ruc='1234567890',
        )

def test_arrendador_valido_con_ruc():
    datos = RegistroArrendador(
        nombre_completo='Luis Ríos',
        correo='luis@example.com',
        contrasena='otraClaveSegura',
        telefono='987654321',
        numero_documento='87654321',
        ruc='20123456789',
    )
    assert datos.ruc == '20123456789'

def test_contrasena_corta_rechazada():
    with pytest.raises(ValidationError, match='at least 10 characters'):
        datos_buscador(contrasena='123456789')

def test_telefono_es_obligatorio_para_arrendador():
    with pytest.raises(ValidationError, match='Field required'):
        RegistroArrendador(
            nombre_completo='Luis Ríos',
            correo='luis@example.com',
            contrasena='otraClaveSegura',
            numero_documento='87654321',
            ruc='20123456789',
        )

def test_telefono_arrendador_exige_nueve_digitos():
    with pytest.raises(ValidationError, match='9 dígitos'):
        RegistroArrendador(
            nombre_completo='Luis Ríos',
            correo='luis@example.com',
            contrasena='otraClaveSegura',
            telefono='98765432',
            numero_documento='87654321',
            ruc='20123456789',
        )


def test_descripcion_de_perfil_exige_minimo_diez_caracteres():
    with pytest.raises(ValidationError, match='al menos 10 caracteres'):
        PerfilEntrada(presupuesto_min=300, presupuesto_max=600, descripcion='Corta')


def test_descripcion_de_perfil_se_limpia_y_acepta_texto_util():
    datos = PerfilEntrada(
        presupuesto_min=300,
        presupuesto_max=600,
        descripcion='  Busco un cuarto tranquilo y céntrico.  ',
    )
    assert datos.descripcion == 'Busco un cuarto tranquilo y céntrico.'


def test_descripcion_de_perfil_limita_quinientos_caracteres():
    with pytest.raises(ValidationError):
        PerfilEntrada(
            presupuesto_min=300,
            presupuesto_max=600,
            descripcion='x' * 501,
        )


def test_catalogos_de_perfil_no_admiten_duplicados():
    datos = PerfilEntrada(
        presupuesto_min=300,
        presupuesto_max=600,
        habito_ids=[1, 1, 2],
        preferencia_ids=[3, 3],
    )
    assert datos.habito_ids == [1, 2]
    assert datos.preferencia_ids == [3]


def test_catalogos_de_perfil_limitan_cantidad():
    with pytest.raises(ValidationError, match='máximo 15'):
        PerfilEntrada(
            presupuesto_min=300,
            presupuesto_max=600,
            habito_ids=list(range(1, 17)),
        )


def test_campos_tipados_de_perfil_se_validan():
    with pytest.raises(ValidationError):
        PerfilEntrada(presupuesto_min=300, presupuesto_max=600, nivel_orden=9)
    with pytest.raises(ValidationError):
        PerfilEntrada(presupuesto_min=300, presupuesto_max=600, edad=15)
    with pytest.raises(ValidationError):
        PerfilEntrada(presupuesto_min=300, presupuesto_max=600, horario='cualquiera')
