import React, { useEffect, useState } from 'react';
import { get, subir } from '../../servicios/api.js';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import IconoPanel from '../../componentes/comunes/IconosPanel.jsx';

const ESTADOS = {
  sin_solicitud: {
    etiqueta: 'Sin solicitud',
    clase: 'espera',
    icono: 'reloj',
    texto: 'Envía tu documento para que un administrador revise tu identidad.',
  },
  pendiente: {
    etiqueta: 'En revisión',
    clase: 'espera',
    icono: 'reloj',
    texto: 'Recibimos tu documento. La revisión suele tardar menos de 24 horas.',
  },
  aprobada: {
    etiqueta: 'Identidad verificada',
    clase: 'ok',
    icono: 'check',
    texto: 'Tu cuenta está verificada. Puedes contactar arrendadores con confianza.',
  },
  rechazada: {
    etiqueta: 'Solicitud rechazada',
    clase: 'alerta',
    icono: 'alerta',
    texto: 'Revisa el motivo y vuelve a enviar un documento legible.',
  },
};

export default function Verificacion() {
  const [estado, setEstado] = useState(null);
  const [archivo, setArchivo] = useState(null);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function cargar() {
    try {
      setEstado(await get('/verificaciones/mi-estado'));
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { cargar(); }, []);

  async function enviar(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    if (!archivo) return setError('Selecciona un documento legible.');
    setEnviando(true);
    try {
      await subir('/verificaciones/solicitar', archivo);
      setMensaje('Solicitud enviada para revisión.');
      setArchivo(null);
      await cargar();
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  const clave = estado?.estado || 'sin_solicitud';
  const info = ESTADOS[clave] || ESTADOS.sin_solicitud;
  const puedeSolicitar = clave === 'sin_solicitud' || clave === 'rechazada';

  return <main className="contenedor formularioPagina paginaVerificacion">
    <section className="panel panelVerificacion">
      <header className="cabeceraVerificacion">
        <span className="iconoVerificacion"><IconoPanel nombre="escudo" tamano={26} /></span>
        <div>
          <p className="etiqueta">SEGURIDAD</p>
          <h1>Verificación de identidad</h1>
          <p>Verifica tu cuenta para generar más confianza al contactar o publicar.</p>
        </div>
      </header>

      <div className={`estadoVerificacion ${info.clase}`} role="status">
        <span className="estadoVerificacionIcono"><IconoPanel nombre={info.icono} tamano={20} /></span>
        <div>
          <strong>{info.etiqueta}</strong>
          <span>{info.texto}</span>
          {estado?.observacion && <span className="estadoObservacion">Motivo: {estado.observacion}</span>}
        </div>
      </div>

      <Mensaje error={error} correcto={mensaje} />

      {puedeSolicitar && <form className="formVerificacion" onSubmit={enviar}>
        <label className={`archivoVerificacion ${archivo ? 'conArchivo' : ''}`}>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,application/pdf"
            onChange={e => { setArchivo(e.target.files?.[0] || null); setError(''); }}
          />
          <span className="archivoIcono"><IconoPanel nombre="camara" tamano={22} /></span>
          <span className="archivoTexto">
            <strong>{archivo ? archivo.name : 'Sube tu documento'}</strong>
            <small>JPG, PNG, WebP o PDF · máximo 5 MB</small>
          </span>
          <span className="archivoAccion">{archivo ? 'Cambiar' : 'Seleccionar'}</span>
        </label>

        <button className="btn ancho btnAuth" type="submit" disabled={!archivo || enviando}>
          {enviando ? 'Enviando…' : 'Solicitar verificación'}
          {!enviando && <span aria-hidden="true">→</span>}
        </button>
      </form>}

      <p className="avisoPrivacidad">
        <IconoPanel nombre="escudo" tamano={16} />
        Tu documento es privado. Solo los administradores autorizados pueden acceder a él.
      </p>
    </section>
  </main>;
}
