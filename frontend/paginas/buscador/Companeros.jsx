import React, { useEffect, useState } from 'react';
import IconoWhatsApp from '../../componentes/comunes/IconoWhatsApp.jsx';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import { get, put } from '../../servicios/api.js';
import { enlaceWhatsApp, mensajeCompanero } from '../../servicios/whatsapp.js';

const OPCIONES_VACIAS = {
  horarios: [],
  ocupaciones: [],
  generos: [],
  generos_preferidos: [],
};

const vacio = {
  presupuesto_min: '0',
  presupuesto_max: '500',
  habito_ids: [],
  preferencia_ids: [],
  fuma: '',
  tiene_mascotas: '',
  horario: '',
  nivel_orden: '',
  ocupacion: '',
  genero: '',
  genero_preferido: '',
  edad: '',
  descripcion: '',
  estado: 'activo',
};

function aFormulario(perfil) {
  return {
    presupuesto_min: String(perfil.presupuesto_min ?? ''),
    presupuesto_max: String(perfil.presupuesto_max ?? ''),
    habito_ids: perfil.habito_ids ?? [],
    preferencia_ids: perfil.preferencia_ids ?? [],
    fuma: perfil.fuma === true ? 'si' : perfil.fuma === false ? 'no' : '',
    tiene_mascotas:
      perfil.tiene_mascotas === true ? 'si' : perfil.tiene_mascotas === false ? 'no' : '',
    horario: perfil.horario ?? '',
    nivel_orden: perfil.nivel_orden == null ? '' : String(perfil.nivel_orden),
    ocupacion: perfil.ocupacion ?? '',
    genero: perfil.genero ?? '',
    genero_preferido: perfil.genero_preferido ?? '',
    edad: perfil.edad == null ? '' : String(perfil.edad),
    descripcion: perfil.descripcion ?? '',
    estado: perfil.estado ?? 'activo',
  };
}

function aCuerpo(f) {
  return {
    presupuesto_min: Number(f.presupuesto_min),
    presupuesto_max: Number(f.presupuesto_max),
    habito_ids: f.habito_ids,
    preferencia_ids: f.preferencia_ids,
    fuma: f.fuma === '' ? null : f.fuma === 'si',
    tiene_mascotas: f.tiene_mascotas === '' ? null : f.tiene_mascotas === 'si',
    horario: f.horario || null,
    nivel_orden: f.nivel_orden === '' ? null : Number(f.nivel_orden),
    ocupacion: f.ocupacion || null,
    genero: f.genero || null,
    genero_preferido: f.genero_preferido || null,
    edad: f.edad === '' ? null : Number(f.edad),
    descripcion: f.descripcion.trim() || null,
    estado: f.estado,
  };
}

function etiquetaOpcion(lista, valor) {
  if (!valor) return '';
  return lista?.find((opcion) => opcion.valor === valor)?.etiqueta || valor;
}

function resumenTipado(persona, opciones) {
  const partes = [];
  if (persona.fuma === true) partes.push('Fuma');
  if (persona.fuma === false) partes.push('No fuma');
  if (persona.tiene_mascotas === true) partes.push('Con mascotas');
  if (persona.tiene_mascotas === false) partes.push('Sin mascotas');
  if (persona.horario) partes.push(etiquetaOpcion(opciones.horarios, persona.horario));
  if (persona.nivel_orden) partes.push(`Orden ${persona.nivel_orden}/5`);
  if (persona.ocupacion) partes.push(etiquetaOpcion(opciones.ocupaciones, persona.ocupacion));
  if (persona.edad) partes.push(`${persona.edad} años`);
  if (persona.genero) partes.push(etiquetaOpcion(opciones.generos, persona.genero));
  if (persona.genero_preferido) {
    partes.push(`Convive con: ${etiquetaOpcion(opciones.generos_preferidos, persona.genero_preferido)}`);
  }
  return partes.join(' · ');
}

function montos(valor) {
  return `S/ ${Number(valor).toFixed(2)}`;
}

function EtiquetasCatalogo({ nombres, legado }) {
  if (nombres?.length) {
    return (
      <div className="etiquetasPerfil">
        {nombres.map((nombre) => <span key={nombre}>{nombre}</span>)}
      </div>
    );
  }
  return <>{legado || 'Sin especificar'}</>;
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
  const [catalogos, setCatalogos] = useState({ habitos: [], preferencias: [] });
  const [opciones, setOpciones] = useState(OPCIONES_VACIAS);

  useEffect(() => {
    let vigente = true;
    get('/companeros/catalogos')
      .then((datos) => {
        if (!vigente) return;
        setCatalogos({
          habitos: datos.habitos || [],
          preferencias: datos.preferencias || [],
        });
        setOpciones({ ...OPCIONES_VACIAS, ...(datos.opciones || {}) });
      })
      .catch(() => { /* El formulario sigue aceptando los campos tipados. */ });
    return () => { vigente = false; };
  }, []);

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

  function alternarCatalogo(campo, identificador) {
    setF((actual) => {
      const seleccion = new Set(actual[campo]);
      if (seleccion.has(identificador)) seleccion.delete(identificador);
      else seleccion.add(identificador);
      return { ...actual, [campo]: [...seleccion] };
    });
  }

  async function guardar(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    const cuerpo = aCuerpo(f);
    if (!Number.isFinite(cuerpo.presupuesto_min) || !Number.isFinite(cuerpo.presupuesto_max)) {
      return setError('Ingresa un presupuesto válido.');
    }
    if (cuerpo.presupuesto_max < cuerpo.presupuesto_min) {
      return setError('El presupuesto máximo debe ser mayor o igual al mínimo.');
    }
    if (cuerpo.descripcion && cuerpo.descripcion.length < 10) {
      return setError('La descripción debe tener al menos 10 caracteres.');
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
                <dd>{montos(perfil.presupuesto_min)} — {montos(perfil.presupuesto_max)}</dd>
              </div>
              <div>
                <dt>Hábitos y pasatiempos</dt>
                <dd><EtiquetasCatalogo nombres={perfil.habito_nombres} legado={perfil.habitos} /></dd>
              </div>
              <div>
                <dt>Preferencias</dt>
                <dd><EtiquetasCatalogo nombres={perfil.preferencia_nombres} legado={perfil.preferencias} /></dd>
              </div>
              <div>
                <dt>Estilo de vida</dt>
                <dd>{resumenTipado(perfil, opciones) || 'Sin especificar'}</dd>
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
            <p>Completa tus datos para encontrar personas con un presupuesto, hábitos y estilo de vida compatibles.</p>
            <form onSubmit={guardar}>
              <div className="camposPerfil">
                <label>Presupuesto mínimo S/
                  <input
                    type="number"
                    inputMode="decimal"
                    min="0"
                    step="0.01"
                    required
                    value={f.presupuesto_min}
                    onChange={(e) => setF({ ...f, presupuesto_min: e.target.value })}
                  />
                </label>
                <label>Presupuesto máximo S/
                  <input
                    type="number"
                    inputMode="decimal"
                    min="0"
                    step="0.01"
                    required
                    value={f.presupuesto_max}
                    onChange={(e) => setF({ ...f, presupuesto_max: e.target.value })}
                  />
                </label>
                <label>¿Fumas?
                  <select value={f.fuma} onChange={(e) => setF({ ...f, fuma: e.target.value })}>
                    <option value="">Sin especificar</option>
                    <option value="no">No</option>
                    <option value="si">Sí</option>
                  </select>
                </label>
                <label>¿Tienes mascotas?
                  <select value={f.tiene_mascotas} onChange={(e) => setF({ ...f, tiene_mascotas: e.target.value })}>
                    <option value="">Sin especificar</option>
                    <option value="no">No</option>
                    <option value="si">Sí</option>
                  </select>
                </label>
                <label>Horario
                  <select value={f.horario} onChange={(e) => setF({ ...f, horario: e.target.value })}>
                    <option value="">Sin especificar</option>
                    {opciones.horarios.map((o) => <option key={o.valor} value={o.valor}>{o.etiqueta}</option>)}
                  </select>
                </label>
                <label>Nivel de orden
                  <select value={f.nivel_orden} onChange={(e) => setF({ ...f, nivel_orden: e.target.value })}>
                    <option value="">Sin especificar</option>
                    <option value="1">1 · Muy flexible</option>
                    <option value="2">2 · Relajado</option>
                    <option value="3">3 · Equilibrado</option>
                    <option value="4">4 · Ordenado</option>
                    <option value="5">5 · Muy ordenado</option>
                  </select>
                </label>
                <label>Ocupación
                  <select value={f.ocupacion} onChange={(e) => setF({ ...f, ocupacion: e.target.value })}>
                    <option value="">Sin especificar</option>
                    {opciones.ocupaciones.map((o) => <option key={o.valor} value={o.valor}>{o.etiqueta}</option>)}
                  </select>
                </label>
                <label>Edad
                  <input
                    type="number"
                    inputMode="numeric"
                    min="18"
                    max="99"
                    placeholder="Opcional"
                    value={f.edad}
                    onChange={(e) => setF({ ...f, edad: e.target.value })}
                  />
                </label>
                <label>Género
                  <select value={f.genero} onChange={(e) => setF({ ...f, genero: e.target.value })}>
                    <option value="">Sin especificar</option>
                    {opciones.generos.map((o) => <option key={o.valor} value={o.valor}>{o.etiqueta}</option>)}
                  </select>
                </label>
                <label>Convivo mejor con
                  <select value={f.genero_preferido} onChange={(e) => setF({ ...f, genero_preferido: e.target.value })}>
                    <option value="">Sin especificar</option>
                    {opciones.generos_preferidos.map((o) => <option key={o.valor} value={o.valor}>{o.etiqueta}</option>)}
                  </select>
                </label>
              </div>

              <fieldset className="grupoPerfil">
                <legend>Hábitos y pasatiempos</legend>
                <p className="textoPequeno">Selecciona las opciones que describan tu día a día.</p>
                <div className="opcionesPerfil">
                  {catalogos.habitos.map((habito) => <label
                    key={habito.habito_id}
                    className={`opcionPerfil ${f.habito_ids.includes(habito.habito_id) ? 'activa' : ''}`}
                  >
                    <input
                      type="checkbox"
                      checked={f.habito_ids.includes(habito.habito_id)}
                      onChange={() => alternarCatalogo('habito_ids', habito.habito_id)}
                    />
                    <span>{habito.nombre}</span>
                  </label>)}
                </div>
              </fieldset>

              <fieldset className="grupoPerfil">
                <legend>Preferencias de convivencia</legend>
                <div className="opcionesPerfil">
                  {catalogos.preferencias.map((preferencia) => <label
                    key={preferencia.preferencia_id}
                    className={`opcionPerfil ${f.preferencia_ids.includes(preferencia.preferencia_id) ? 'activa' : ''}`}
                  >
                    <input
                      type="checkbox"
                      checked={f.preferencia_ids.includes(preferencia.preferencia_id)}
                      onChange={() => alternarCatalogo('preferencia_ids', preferencia.preferencia_id)}
                    />
                    <span>{preferencia.nombre}</span>
                  </label>)}
                </div>
              </fieldset>

              <label>Descripción
                <textarea
                  rows="4"
                  minLength={10}
                  maxLength={500}
                  value={f.descripcion}
                  onChange={(e) => setF({ ...f, descripcion: e.target.value })}
                  placeholder="Cuéntanos qué tipo de convivencia buscas (mínimo 10 caracteres)."
                />
                <small className="contadorDescripcion">{f.descripcion.length}/500</small>
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
                const estiloVida = resumenTipado(c, opciones);
                return <article className="coincidencia" key={c.perfil_id}>
                  <div className="coincidenciaCabecera">
                    <AvatarPersona persona={c} />
                    <div>
                      <h3>{c.nombre_completo}</h3>
                      <p className="textoPequeno">{montos(c.presupuesto_min)} — {montos(c.presupuesto_max)}</p>
                    </div>
                    <span className="nivelCompatibilidad" title="Afinidad por presupuesto, hábitos y preferencias">
                      {c.compatibilidad}% compatible
                    </span>
                  </div>
                  <div className="etiquetasPerfil">
                    {c.habito_nombres?.map((nombre) => <span key={nombre}>{nombre}</span>)}
                    {c.preferencia_nombres?.map((nombre) => <span key={nombre}>Prefiere: {nombre}</span>)}
                    {!c.habito_nombres?.length && c.habitos && <span>Hábitos: {c.habitos}</span>}
                    {!c.preferencia_nombres?.length && c.preferencias && <span>Prefiere: {c.preferencias}</span>}
                  </div>
                  {estiloVida && <p className="textoPequeno">{estiloVida}</p>}
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
