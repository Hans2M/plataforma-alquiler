import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { get, patch, post } from '../../servicios/api.js';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';

const VACIO = { tipos: [], estados: [], habitos: [], preferencias: [] };

const NUEVO_TIPO = { codigo: '', nombre: '', descripcion: '', orden: '10' };
const NUEVO_HABITO = { nombre: '', categoria: 'convivencia', orden: '10' };
const NUEVA_PREFERENCIA = { nombre: '', categoria: 'convivencia', orden: '10' };

const RUTA_EDICION = {
  tipos: (item) => `/administracion/catalogos/tipos/${item.tipo_id}`,
  estados: (item) => `/administracion/catalogos/estados/${item.dominio}/${item.codigo}`,
  habitos: (item) => `/administracion/catalogos/habitos/${item.habito_id}`,
  preferencias: (item) => `/administracion/catalogos/preferencias/${item.preferencia_id}`,
};

const CATEGORIAS_HABITO = [
  ['convivencia', 'Convivencia'],
  ['rutina', 'Rutina'],
  ['ocio', 'Ocio'],
];

const CATEGORIAS_PREFERENCIA = [
  ['convivencia', 'Convivencia'],
  ['perfil', 'Perfil'],
];

function claveDe(seccion, item) {
  if (seccion === 'estados') return `estado-${item.dominio}-${item.codigo}`;
  if (seccion === 'tipos') return `tipo-${item.tipo_id}`;
  if (seccion === 'habitos') return `habito-${item.habito_id}`;
  return `preferencia-${item.preferencia_id}`;
}

function borradorDe(item) {
  return {
    nombre: item.nombre ?? '',
    descripcion: item.descripcion ?? '',
    orden: String(item.orden ?? 0),
    activo: Boolean(item.activo),
    categoria: item.categoria ?? '',
  };
}

function FilaCatalogo({
  seccion,
  item,
  borradores,
  abrir,
  cambiar,
  guardar,
  cancelar,
  categorias,
  contexto,
}) {
  const clave = claveDe(seccion, item);
  const draft = borradores[clave];

  if (!draft) {
    return <article className="catalogoFila">
      <div className="catalogoResumen">
        <strong>{item.nombre}</strong>
        <span className="textoPequeno">
          {contexto ? `${contexto} · ` : ''}
          {item.codigo ? `${item.codigo} · ` : ''}
          {item.descripcion || 'Sin descripción'}
        </span>
      </div>
      <span className={`chipEstado ${item.activo ? 'activo' : 'inactivo'}`}>
        {item.activo ? 'Activo' : 'Inactivo'}
      </span>
      <span className="catalogoOrden">Orden {item.orden}</span>
      <button className="btn secundario" type="button" onClick={() => abrir(clave, item)}>
        Editar
      </button>
    </article>;
  }

  return <form
    className="catalogoFila catalogoEdicion"
    onSubmit={(e) => { e.preventDefault(); guardar(clave, item, seccion); }}
  >
    <label>Nombre
      <input
        required
        minLength={2}
        maxLength={80}
        value={draft.nombre}
        onChange={(e) => cambiar(clave, 'nombre', e.target.value)}
      />
    </label>
    <label>Descripción
      <input
        maxLength={200}
        value={draft.descripcion}
        onChange={(e) => cambiar(clave, 'descripcion', e.target.value)}
      />
    </label>
    {categorias && <label>Categoría
      <select
        value={draft.categoria}
        onChange={(e) => cambiar(clave, 'categoria', e.target.value)}
      >
        {categorias.map(([valor, etiqueta]) => (
          <option key={valor} value={valor}>{etiqueta}</option>
        ))}
      </select>
    </label>}
    <label>Orden
      <input
        type="number"
        min="0"
        max="999"
        value={draft.orden}
        onChange={(e) => cambiar(clave, 'orden', e.target.value)}
      />
    </label>
    <label className="casillaFiltro">
      <input
        type="checkbox"
        checked={draft.activo}
        onChange={(e) => cambiar(clave, 'activo', e.target.checked)}
      />
      Activo
    </label>
    <div className="acciones">
      <button className="btn" type="submit">Guardar</button>
      <button className="btn texto" type="button" onClick={() => cancelar(clave)}>Cancelar</button>
    </div>
  </form>;
}

export default function Catalogos() {
  const [datos, setDatos] = useState(VACIO);
  const [borradores, setBorradores] = useState({});
  const [nuevoTipo, setNuevoTipo] = useState(NUEVO_TIPO);
  const [nuevoHabito, setNuevoHabito] = useState(NUEVO_HABITO);
  const [nuevaPreferencia, setNuevaPreferencia] = useState(NUEVA_PREFERENCIA);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [cargando, setCargando] = useState(true);

  async function cargar() {
    try {
      setDatos(await get('/administracion/catalogos'));
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => { cargar(); }, []);

  useEffect(() => {
    if (!mensaje) return undefined;
    const temporizador = setTimeout(() => setMensaje(''), 4500);
    return () => clearTimeout(temporizador);
  }, [mensaje]);

  const estadosPorDominio = useMemo(() => {
    const grupos = {};
    for (const estado of datos.estados || []) {
      grupos[estado.dominio] = [...(grupos[estado.dominio] || []), estado];
    }
    return grupos;
  }, [datos.estados]);

  function abrir(clave, item) {
    setError('');
    setMensaje('');
    setBorradores((actual) => ({ ...actual, [clave]: borradorDe(item) }));
  }

  function cambiar(clave, campo, valor) {
    setBorradores((actual) => ({
      ...actual,
      [clave]: { ...actual[clave], [campo]: valor },
    }));
  }

  function cancelar(clave) {
    setBorradores((actual) => {
      const siguientes = { ...actual };
      delete siguientes[clave];
      return siguientes;
    });
  }

  async function guardar(clave, item, seccion) {
    setError('');
    setMensaje('');
    const draft = borradores[clave];
    const cuerpo = {
      nombre: draft.nombre,
      descripcion: draft.descripcion || null,
      orden: Number(draft.orden) || 0,
      activo: Boolean(draft.activo),
    };
    if (draft.categoria) cuerpo.categoria = draft.categoria;
    try {
      await patch(RUTA_EDICION[seccion](item), cuerpo);
      cancelar(clave);
      setMensaje('Catálogo actualizado.');
      await cargar();
    } catch (e) {
      setError(e.message);
    }
  }

  async function crearTipo(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    try {
      await post('/administracion/catalogos/tipos', {
        codigo: nuevoTipo.codigo.trim().toLowerCase(),
        nombre: nuevoTipo.nombre.trim(),
        descripcion: nuevoTipo.descripcion.trim() || null,
        orden: Number(nuevoTipo.orden) || 0,
      });
      setNuevoTipo(NUEVO_TIPO);
      setMensaje('Tipo de alojamiento creado.');
      await cargar();
    } catch (err) {
      setError(err.message);
    }
  }

  async function crearHabito(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    try {
      await post('/administracion/catalogos/habitos', {
        nombre: nuevoHabito.nombre.trim(),
        categoria: nuevoHabito.categoria,
        orden: Number(nuevoHabito.orden) || 0,
        activo: true,
      });
      setNuevoHabito(NUEVO_HABITO);
      setMensaje('Hábito creado.');
      await cargar();
    } catch (err) {
      setError(err.message);
    }
  }

  async function crearPreferencia(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    try {
      await post('/administracion/catalogos/preferencias', {
        nombre: nuevaPreferencia.nombre.trim(),
        categoria: nuevaPreferencia.categoria,
        orden: Number(nuevaPreferencia.orden) || 0,
        activo: true,
      });
      setNuevaPreferencia(NUEVA_PREFERENCIA);
      setMensaje('Preferencia creada.');
      await cargar();
    } catch (err) {
      setError(err.message);
    }
  }

  return <main className="contenedor seccion">
    <p className="etiqueta">ADMINISTRACIÓN</p>
    <div className="seccionTitulo">
      <div>
        <h1>Catálogos de la plataforma</h1>
        <p className="textoPequeno">
          Los códigos internos son fijos; aquí se editan las etiquetas, el orden y la visibilidad.
        </p>
      </div>
      <Link className="btn secundario" to="/administracion">Volver a administración</Link>
    </div>
    <Mensaje error={error} correcto={mensaje} />

    {cargando
      ? <p>Cargando catálogos…</p>
      : <>
        <section className="panel catalogoSeccion">
          <h2>Tipos de alojamiento</h2>
          <p className="textoPequeno">
            Se usan en el buscador y en el formulario de publicación. Desactiva un tipo para
            dejar de ofrecerlo sin borrar las publicaciones existentes.
          </p>
          {(datos.tipos || []).map((tipo) => <FilaCatalogo
            key={tipo.tipo_id}
            seccion="tipos"
            item={tipo}
            borradores={borradores}
            abrir={abrir}
            cambiar={cambiar}
            guardar={guardar}
            cancelar={cancelar}
          />)}

          <form className="catalogoNuevo" onSubmit={crearTipo}>
            <h3>Nuevo tipo</h3>
            <label>Código
              <input
                required
                minLength={2}
                maxLength={40}
                pattern="[a-z0-9_]+"
                placeholder="loft"
                value={nuevoTipo.codigo}
                onChange={(e) => setNuevoTipo({ ...nuevoTipo, codigo: e.target.value })}
              />
            </label>
            <label>Nombre
              <input
                required
                minLength={2}
                maxLength={60}
                value={nuevoTipo.nombre}
                onChange={(e) => setNuevoTipo({ ...nuevoTipo, nombre: e.target.value })}
              />
            </label>
            <label>Descripción
              <input
                maxLength={200}
                value={nuevoTipo.descripcion}
                onChange={(e) => setNuevoTipo({ ...nuevoTipo, descripcion: e.target.value })}
              />
            </label>
            <label>Orden
              <input
                type="number"
                min="0"
                max="999"
                value={nuevoTipo.orden}
                onChange={(e) => setNuevoTipo({ ...nuevoTipo, orden: e.target.value })}
              />
            </label>
            <button className="btn" type="submit">Crear tipo</button>
          </form>
        </section>

        <section className="panel catalogoSeccion">
          <h2>Estados</h2>
          <p className="textoPequeno">
            Los estados no se crean ni se renombran desde aquí: la aplicación los usa en su
            lógica. Puedes ajustar la etiqueta, el orden y la visibilidad.
          </p>
          {Object.entries(estadosPorDominio).map(([dominio, estados]) => <div key={dominio} className="catalogoGrupo">
            <h3>{dominio}</h3>
            {estados.map((estado) => <FilaCatalogo
              key={`${dominio}-${estado.codigo}`}
              seccion="estados"
              item={estado}
              contexto={dominio}
              borradores={borradores}
              abrir={abrir}
              cambiar={cambiar}
              guardar={guardar}
              cancelar={cancelar}
            />)}
          </div>)}
        </section>

        <section className="panel catalogoSeccion">
          <h2>Hábitos y pasatiempos</h2>
          <p className="textoPequeno">
            Opciones que los buscadores eligen en su perfil de convivencia.
          </p>
          {(datos.habitos || []).map((habito) => <FilaCatalogo
            key={habito.habito_id}
            seccion="habitos"
            item={habito}
            contexto={`Categoría: ${habito.categoria}`}
            categorias={CATEGORIAS_HABITO}
            borradores={borradores}
            abrir={abrir}
            cambiar={cambiar}
            guardar={guardar}
            cancelar={cancelar}
          />)}

          <form className="catalogoNuevo" onSubmit={crearHabito}>
            <h3>Nuevo hábito</h3>
            <label>Nombre
              <input
                required
                minLength={2}
                maxLength={80}
                value={nuevoHabito.nombre}
                onChange={(e) => setNuevoHabito({ ...nuevoHabito, nombre: e.target.value })}
              />
            </label>
            <label>Categoría
              <select
                value={nuevoHabito.categoria}
                onChange={(e) => setNuevoHabito({ ...nuevoHabito, categoria: e.target.value })}
              >
                {CATEGORIAS_HABITO.map(([valor, etiqueta]) => (
                  <option key={valor} value={valor}>{etiqueta}</option>
                ))}
              </select>
            </label>
            <label>Orden
              <input
                type="number"
                min="0"
                max="999"
                value={nuevoHabito.orden}
                onChange={(e) => setNuevoHabito({ ...nuevoHabito, orden: e.target.value })}
              />
            </label>
            <button className="btn" type="submit">Crear hábito</button>
          </form>
        </section>

        <section className="panel catalogoSeccion">
          <h2>Preferencias de convivencia</h2>
          <p className="textoPequeno">
            Expectativas que un buscador declara sobre la persona con quien convivirá.
          </p>
          {(datos.preferencias || []).map((preferencia) => <FilaCatalogo
            key={preferencia.preferencia_id}
            seccion="preferencias"
            item={preferencia}
            contexto={`Categoría: ${preferencia.categoria}`}
            categorias={CATEGORIAS_PREFERENCIA}
            borradores={borradores}
            abrir={abrir}
            cambiar={cambiar}
            guardar={guardar}
            cancelar={cancelar}
          />)}

          <form className="catalogoNuevo" onSubmit={crearPreferencia}>
            <h3>Nueva preferencia</h3>
            <label>Nombre
              <input
                required
                minLength={2}
                maxLength={100}
                value={nuevaPreferencia.nombre}
                onChange={(e) => setNuevaPreferencia({ ...nuevaPreferencia, nombre: e.target.value })}
              />
            </label>
            <label>Categoría
              <select
                value={nuevaPreferencia.categoria}
                onChange={(e) => setNuevaPreferencia({ ...nuevaPreferencia, categoria: e.target.value })}
              >
                {CATEGORIAS_PREFERENCIA.map(([valor, etiqueta]) => (
                  <option key={valor} value={valor}>{etiqueta}</option>
                ))}
              </select>
            </label>
            <label>Orden
              <input
                type="number"
                min="0"
                max="999"
                value={nuevaPreferencia.orden}
                onChange={(e) => setNuevaPreferencia({ ...nuevaPreferencia, orden: e.target.value })}
              />
            </label>
            <button className="btn" type="submit">Crear preferencia</button>
          </form>
        </section>
      </>}
  </main>;
}
