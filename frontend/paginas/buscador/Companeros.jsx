import React, { useEffect, useState } from 'react';
import IconoWhatsApp from '../../componentes/comunes/IconoWhatsApp.jsx';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import { get, put } from '../../servicios/api.js';
import { enlaceWhatsApp, mensajeCompanero } from '../../servicios/whatsapp.js';

const vacio = {
  presupuesto_min: '0',
  presupuesto_max: '500',
  habitos: '',
  preferencias: '',
  descripcion: '',
  estado: 'activo',
};

const campos = [
  ['presupuesto_min', 'Presupuesto mínimo S/'],
  ['presupuesto_max', 'Presupuesto máximo S/'],
  ['habitos', 'Hábitos'],
  ['preferencias', 'Preferencias'],
];

function aFormulario(perfil) {
  return {
    presupuesto_min: String(perfil.presupuesto_min ?? ''),
    presupuesto_max: String(perfil.presupuesto_max ?? ''),
    habitos: perfil.habitos ?? '',
    preferencias: perfil.preferencias ?? '',
    descripcion: perfil.descripcion ?? '',
    estado: perfil.estado ?? 'activo',
  };
}

function monto(valor) {
  return `S/ ${Number(valor).toFixed(2)}`;
}

function AvatarPersona({ persona }) {
  const [fallo, setFallo] = useState(false);
  const inicial = (persona.nombre_completo || '?').charAt(0).toUpperCase();

  if (!persona.foto_url || fallo) {
    return <span className="avatarContacto" aria-hidden="true">{inicial}</span>;
  }

  return <span className="avatarContacto" aria-hidden="true">
    <img
      src={persona.foto_url}
      alt=""
      loading="lazy"
      onError={() => setFallo(true)}
    />
  </span>;
}

export default function Companeros() {
  const [f, setF] = useState(vacio);
  const [perfil, setPerfil] = useState(null);
  const [editando, setEditando] = useState(true);
  const [cargando, setCargando] = useState(true);
  const [coincidencias, setCoincidencias] = useState([]);
  const [buscando, setBuscando] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');

  useEffect(() => {
    let vigente = true;
    get('/companeros/mi-perfil')
      .then((datos) => {
        if (!vigente) return;
        setPerfil(datos);
        setF(aFormulario(datos));
        setEditando(false);
      })
      .catch(() => { if (vigente) setEditando(true); })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, []);

  useEffect(() => {
    if (!mensaje) return undefined;
    const temporizador = setTimeout(() => setMensaje(''), 4500);
    return () => clearTimeout(temporizador);
  }, [mensaje]);

  useEffect(() => {
    if (!perfil || perfil.estado !== 'activo') {
      setCoincidencias([]);
      return undefined;
    }
    let vigente = true;
    setBuscando(true);
    setError('');
    get('/companeros/coincidencias')
      .then((lista) => vigente && setCoincidencias(lista))
      .catch((e) => vigente && setError(e.message))
      .finally(() => vigente && setBuscando(false));
    return () => { vigente = false; };
  }, [perfil]);

  async function guardar(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    const cuerpo = {
      presupuesto_min: Number(f.presupuesto_min),
      presupuesto_max: Number(f.presupuesto_max),
      habitos: f.habitos.trim() || null,
      preferencias: f.preferencias.trim() || null,
      descripcion: f.descripcion.trim() || null,
      estado: f.estado,
    };
    if (!Number.isFinite(cuerpo.presupuesto_min) || !Number.isFinite(cuerpo.presupuesto_max)) {
      return setError('Ingresa un presupuesto válido.');
    }
    if (cuerpo.presupuesto_max < cuerpo.presupuesto_min) {
      return setError('El presupuesto máximo debe ser mayor o igual al mínimo.');
    }
    try {
      const guardado = await put('/companeros/mi-perfil', cuerpo);
      setPerfil(guardado);
      setF(aFormulario(guardado));
      setEditando(false);
      setMensaje(perfil ? 'Perfil actualizado correctamente.' : 'Perfil creado correctamente.');
    } catch (err) {
      setError(err.message);
    }
  }

  function editar() {
    setMensaje('');
    setError('');
    setF(aFormulario(perfil));
    setEditando(true);
  }

  function cancelar() {
    setMensaje('');
    setError('');
    setF(aFormulario(perfil));
    setEditando(false);
  }

  async function buscarCoincidencias() {
    setError('');
    setBuscando(true);
    try {
      setCoincidencias(await get('/companeros/coincidencias'));
    } catch (err) {
      setError(err.message);
    } finally {
      setBuscando(false);
    }
  }

  if (cargando) {
    return <main className="contenedor seccion"><p>Cargando tu perfil de convivencia…</p></main>;
  }

  return <main className="contenedor seccion">
    <p className="etiqueta">COMPARTIR VIVIENDA</p>
    <h1>Mi perfil de convivencia</h1>
    <Mensaje error={error} correcto={mensaje} />

    <div className="perfilConvivencia">
      <section>
        {perfil && !editando
          ? <article className="panel resumenPerfil">
            <div className="resumenCabecera">
              <span className="resumenIcono" aria-hidden="true">✓</span>
              <div>
                <p className="etiqueta">PERFIL GUARDADO</p>
                <h2>Tu perfil de convivencia está listo</h2>
              </div>
              <span className={`chipEstado ${perfil.estado}`}>{perfil.estado}</span>
            </div>
            <dl className="resumenDatos">
              <div>
                <dt>Presupuesto</dt>
                <dd>{monto(perfil.presupuesto_min)} — {monto(perfil.presupuesto_max)}</dd>
              </div>
              <div>
                <dt>Hábitos</dt>
                <dd>{perfil.habitos || 'Sin especificar'}</dd>
              </div>
              <div>
                <dt>Preferencias</dt>
                <dd>{perfil.preferencias || 'Sin especificar'}</dd>
              </div>
              <div>
                <dt>Descripción</dt>
                <dd>{perfil.descripcion || 'Sin descripción'}</dd>
              </div>
            </dl>
            <div className="acciones">
              <button className="btn secundario" type="button" onClick={editar}>Editar perfil</button>
              <button className="btn" type="button" onClick={buscarCoincidencias} disabled={buscando}>
                {buscando ? 'Buscando…' : 'Buscar coincidencias'}
              </button>
            </div>
          </article>
          : <article className="panel">
            <h2>{perfil ? 'Editar perfil de convivencia' : 'Crea tu perfil de convivencia'}</h2>
            <p>Completa tus datos para encontrar personas con un presupuesto y hábitos compatibles.</p>
            <form onSubmit={guardar}>
              {campos.map(([clave, etiqueta]) => <label key={clave}>{etiqueta}
                <input
                  type={clave.startsWith('presupuesto') ? 'number' : 'text'}
                  inputMode={clave.startsWith('presupuesto') ? 'decimal' : undefined}
                  min={clave.startsWith('presupuesto') ? '0' : undefined}
                  step={clave.startsWith('presupuesto') ? '0.01' : undefined}
                  required={clave.startsWith('presupuesto')}
                  value={f[clave]}
                  onChange={(e) => setF({ ...f, [clave]: e.target.value })}
                />
              </label>)}
              <label>Descripción
                <textarea rows="3" value={f.descripcion} maxLength={500} onChange={(e) => setF({ ...f, descripcion: e.target.value })} />
              </label>
              <label>Estado
                <select value={f.estado} onChange={(e) => setF({ ...f, estado: e.target.value })}>
                  <option value="activo">Activo</option>
                  <option value="inactivo">Inactivo</option>
                </select>
              </label>
              <div className="acciones">
                <button className="btn" type="submit">Guardar perfil</button>
                {perfil && <button className="btn secundario" type="button" onClick={cancelar}>Cancelar</button>}
              </div>
            </form>
          </article>}

        {perfil && <section className="panel coincidenciasPanel">
          <div className="seccionTitulo">
            <div>
              <p className="etiqueta">COINCIDENCIAS</p>
              <h2>Personas compatibles</h2>
            </div>
            <span className="contadorCoincidencias" aria-label={`${coincidencias.length} coincidencias`}>
              {coincidencias.length}
            </span>
          </div>

          {buscando && <p>Buscando perfiles compatibles…</p>}
          {!buscando && coincidencias.length === 0
            ? <div className="vacio">
              <p><strong>Aún no hay coincidencias.</strong></p>
              <p>Cuando otro buscador registre un perfil con un presupuesto que se superponga al tuyo, aparecerá aquí con su perfil y su WhatsApp.</p>
            </div>
            : <div className="listaCoincidencias">
              {coincidencias.map((c) => {
                const enlace = c.telefono
                  ? enlaceWhatsApp(c.telefono, mensajeCompanero(c, perfil))
                  : null;
                return <article className="coincidencia" key={c.perfil_id}>
                  <div className="coincidenciaCabecera">
                    <AvatarPersona persona={c} />
                    <div>
                      <h3>{c.nombre_completo}</h3>
                      <p className="textoPequeno">{monto(c.presupuesto_min)} — {monto(c.presupuesto_max)}</p>
                    </div>
                  </div>
                  <div className="etiquetasPerfil">
                    {c.habitos && <span>Hábitos: {c.habitos}</span>}
                    {c.preferencias && <span>Prefiere: {c.preferencias}</span>}
                  </div>
                  {c.descripcion && <p className="textoCoincidencia">{c.descripcion}</p>}
                  {enlace
                    ? <a className="btn whatsapp" href={enlace} target="_blank" rel="noopener noreferrer">
                      <IconoWhatsApp /> Contactar por WhatsApp
                    </a>
                    : <p className="aviso">Esta persona aún no habilitó un número de contacto. Intenta más adelante.</p>}
                </article>;
              })}
            </div>}
        </section>}
      </section>
    </div>
  </main>;
}
