import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { post } from '../../servicios/api.js';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import MarcoAutenticacion from '../../componentes/autenticacion/MarcoAutenticacion.jsx';
import IconoPanel from '../../componentes/comunes/IconosPanel.jsx';
import IconoOjo from '../../componentes/comunes/IconoOjo.jsx';

const DOCUMENTOS = {
  DNI: { etiqueta: 'DNI', longitud: 8, ayuda: '8 dígitos, sin puntos ni guiones', mensaje: 'El DNI debe tener exactamente 8 dígitos.', patron: /^\d{8}$/ },
  CE: { etiqueta: 'Carné de extranjería', longitud: 9, ayuda: '9 dígitos', mensaje: 'El carné de extranjería debe tener exactamente 9 dígitos.', patron: /^\d{9}$/ },
  PASAPORTE: { etiqueta: 'Pasaporte', longitud: 12, ayuda: 'Entre 8 y 12 letras o números', mensaje: 'El pasaporte debe tener entre 8 y 12 letras o números.', patron: /^[A-Za-z0-9]{8,12}$/ },
};

const inicial = {
  nombre_completo: '',
  correo: '',
  telefono: '',
  tipo_documento: 'DNI',
  numero_documento: '',
  ruc: '',
  contrasena: '',
  confirmacion: '',
};

function validar(f, rol) {
  if (f.nombre_completo.trim().length < 2) return 'Ingresa tu nombre completo.';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.correo.trim())) return 'Ingresa un correo electrónico válido.';
  if (rol === 'arrendador') {
    if (!/^\d{9}$/.test(f.telefono)) return 'El teléfono del arrendador debe tener 9 dígitos (celular para WhatsApp).';
  } else if (f.telefono && !/^\d{7,9}$/.test(f.telefono)) {
    return 'El teléfono debe tener entre 7 y 9 dígitos.';
  }
  const documento = DOCUMENTOS[f.tipo_documento];
  if (!documento.patron.test(f.numero_documento)) return documento.mensaje;
  if (rol === 'arrendador' && !/^\d{11}$/.test(f.ruc)) return 'El RUC debe tener exactamente 11 dígitos.';
  if (f.contrasena.length < 10) return 'La contraseña debe tener al menos 10 caracteres.';
  if (f.contrasena !== f.confirmacion) return 'Las contraseñas no coinciden.';
  return '';
}

export default function Registro() {
  const [rol, setRol] = useState('buscador');
  const [f, setF] = useState(inicial);
  const [error, setError] = useState('');
  const [correcto, setCorrecto] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [verContrasena, setVerContrasena] = useState(false);
  const [verConfirmacion, setVerConfirmacion] = useState(false);
  const navegar = useNavigate();
  const documento = DOCUMENTOS[f.tipo_documento];
  const coinciden = f.contrasena.length > 0 && f.confirmacion.length > 0 && f.contrasena === f.confirmacion;
  const noCoinciden = f.confirmacion.length > 0 && f.contrasena !== f.confirmacion;
  const esArrendador = rol === 'arrendador';

  function cambiar(campo, valor) {
    if (error) setError('');
    if (campo === 'ruc') valor = valor.replace(/\D/g, '').slice(0, 11);
    if (campo === 'telefono') valor = valor.replace(/\D/g, '').slice(0, 9);
    if (campo === 'numero_documento') {
      valor = f.tipo_documento === 'PASAPORTE'
        ? valor.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12)
        : valor.replace(/\D/g, '').slice(0, documento.longitud);
    }
    setF({ ...f, [campo]: valor });
  }

  function cambiarRol(valor) {
    setF({ ...f, ruc: '' });
    setRol(valor);
  }

  async function enviar(e) {
    e.preventDefault();
    setError('');
    setCorrecto('');
    const problema = validar(f, rol);
    if (problema) return setError(problema);
    setEnviando(true);
    try {
      const datos = {
        nombre_completo: f.nombre_completo.trim(),
        correo: f.correo.trim(),
        contrasena: f.contrasena,
        tipo_documento: f.tipo_documento,
        numero_documento: f.numero_documento,
      };
      if (f.telefono) datos.telefono = f.telefono;
      if (rol === 'arrendador') {
        datos.telefono = f.telefono;
        datos.ruc = f.ruc;
      }
      await post('/autenticacion/registro/' + rol, datos);
      setCorrecto('Cuenta creada. Ahora puedes ingresar.');
      setTimeout(() => navegar('/ingresar'), 900);
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return <MarcoAutenticacion variante="registro">
    <header className="cabeceraAuth">
      <p className="etiqueta">ÚNETE A LA PLATAFORMA</p>
      <h1>Crear una cuenta</h1>
      <p>Publica o encuentra alojamiento con contacto seguro y verificado.</p>
    </header>

    <Mensaje error={error} correcto={correcto} />

    <form className="formAuth" onSubmit={enviar} noValidate>
      <fieldset className="grupoRol">
        <legend>Tipo de cuenta</legend>
        <div className="rolesAuth">
          <label className={`rolAuth ${rol === 'buscador' ? 'activo' : ''}`}>
            <input
              type="radio"
              name="rol"
              value="buscador"
              aria-label="Buscador de alojamiento"
              checked={rol === 'buscador'}
              onChange={() => cambiarRol('buscador')}
            />
            <span className="rolIcono"><IconoPanel nombre="buscar" tamano={20} /></span>
            <span className="rolTexto">
              <strong>Busco alojamiento</strong>
              <small>Habitaciones, departamentos y compañeros.</small>
            </span>
            <span className="rolMarca" aria-hidden="true" />
          </label>

          <label className={`rolAuth ${rol === 'arrendador' ? 'activo' : ''}`}>
            <input
              type="radio"
              name="rol"
              value="arrendador"
              aria-label="Arrendador"
              checked={rol === 'arrendador'}
              onChange={() => cambiarRol('arrendador')}
            />
            <span className="rolIcono"><IconoPanel nombre="casa" tamano={20} /></span>
            <span className="rolTexto">
              <strong>Ofrezco alojamiento</strong>
              <small>Publica y recibe contactos por WhatsApp.</small>
            </span>
            <span className="rolMarca" aria-hidden="true" />
          </label>
        </div>
      </fieldset>

      <div className="seccionAuth">
        <h2>Datos personales</h2>

        <label>Nombre completo
          <input required autoComplete="name" maxLength={150} id="registro-nombre" placeholder="Nombres y apellidos" value={f.nombre_completo} onChange={e => cambiar('nombre_completo', e.target.value)} />
        </label>

        <div className="filaAuth">
          <label>Correo electrónico
            <input required type="email" autoComplete="email" inputMode="email" maxLength={180} id="registro-correo" placeholder="tucorreo@ejemplo.com" value={f.correo} onChange={e => cambiar('correo', e.target.value)} />
          </label>

          <label>Teléfono / WhatsApp {esArrendador ? '(obligatorio)' : '(opcional)'}
            <input
              required={esArrendador}
              type="tel"
              autoComplete="tel"
              inputMode="numeric"
              id="registro-telefono"
              placeholder="987654321"
              maxLength={9}
              value={f.telefono}
              onChange={e => cambiar('telefono', e.target.value)}
            />
            <span className="ayudaCampo">
              {esArrendador
                ? '9 dígitos. Los buscadores lo usarán para contactarte por WhatsApp.'
                : 'Opcional. Entre 7 y 9 dígitos.'}
            </span>
          </label>
        </div>
      </div>

      <div className="seccionAuth">
        <h2>Documento de identidad</h2>

        <div className="filaAuth">
          <label>Tipo de documento
            <select value={f.tipo_documento} onChange={e => setF({ ...f, tipo_documento: e.target.value, numero_documento: '' })}>
              <option value="DNI">DNI</option>
              <option value="CE">Carné de extranjería</option>
              <option value="PASAPORTE">Pasaporte</option>
            </select>
          </label>

          <label>Número de {documento.etiqueta}
            <input
              required
              inputMode={f.tipo_documento === 'PASAPORTE' ? 'text' : 'numeric'}
              id="registro-documento"
              autoComplete="off"
              maxLength={documento.longitud}
              value={f.numero_documento}
              onChange={e => cambiar('numero_documento', e.target.value)}
            />
            <span className="ayudaCampo">{documento.ayuda}</span>
          </label>
        </div>

        {esArrendador && <label>RUC
          <input required inputMode="numeric" id="registro-ruc" autoComplete="off" placeholder="20123456789" maxLength={11} value={f.ruc} onChange={e => cambiar('ruc', e.target.value)} />
          <span className="ayudaCampo">11 dígitos. Obligatorio para publicar alojamientos.</span>
        </label>}
      </div>

      <div className="seccionAuth">
        <h2>Seguridad</h2>

        <div className="filaAuth">
          <div className="campoConEtiqueta">
            <label htmlFor="registro-contrasena">Contraseña</label>
            <span className="campoClave">
              <input
                required
                type={verContrasena ? 'text' : 'password'}
                autoComplete="new-password"
                minLength={10}
                maxLength={128}
                id="registro-contrasena"
                placeholder="Mínimo 10 caracteres"
                className={coinciden ? 'coincide' : noCoinciden ? 'noCoincide' : ''}
                value={f.contrasena}
                onChange={e => cambiar('contrasena', e.target.value)}
              />
              <button
                type="button"
                className="botonVer"
                aria-label={verContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                aria-pressed={verContrasena}
                title={verContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                onClick={e => { e.preventDefault(); setVerContrasena(v => !v); }}
              ><IconoOjo abierto={verContrasena} /></button>
            </span>
            <span className="ayudaCampo">Mínimo 10 caracteres.</span>
          </div>

          <div className="campoConEtiqueta">
            <label htmlFor="registro-confirmacion">Repetir contraseña</label>
            <span className="campoClave">
              <input
                required
                type={verConfirmacion ? 'text' : 'password'}
                autoComplete="new-password"
                minLength={10}
                maxLength={128}
                id="registro-confirmacion"
                placeholder="Repite tu contraseña"
                className={coinciden ? 'coincide' : noCoinciden ? 'noCoincide' : ''}
                value={f.confirmacion}
                onChange={e => cambiar('confirmacion', e.target.value)}
              />
              <button
                type="button"
                className="botonVer"
                aria-label={verConfirmacion ? 'Ocultar repetición de contraseña' : 'Mostrar repetición de contraseña'}
                aria-pressed={verConfirmacion}
                title={verConfirmacion ? 'Ocultar repetición de contraseña' : 'Mostrar repetición de contraseña'}
                onClick={e => { e.preventDefault(); setVerConfirmacion(v => !v); }}
              ><IconoOjo abierto={verConfirmacion} /></button>
            </span>
            {coinciden && <span className="ayudaCampo ayudaExito">✓ Las contraseñas coinciden.</span>}
            {noCoinciden && <span className="ayudaCampo ayudaError">Las contraseñas aún no coinciden.</span>}
          </div>
        </div>
      </div>

      <button className="btn ancho btnAuth" type="submit" disabled={enviando}>
        {enviando ? 'Creando cuenta…' : 'Registrarme'}
        {!enviando && <span aria-hidden="true">→</span>}
      </button>
    </form>

    <p className="pieAuth">
      <span>¿Ya tienes una cuenta?</span>
      <Link to="/ingresar">Iniciar sesión</Link>
    </p>
  </MarcoAutenticacion>;
}
