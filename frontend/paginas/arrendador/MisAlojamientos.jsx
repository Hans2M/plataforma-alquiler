import React, { useEffect, useState } from 'react';
import { get, post, patch, del, subir } from '../../servicios/api.js';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';

const inicial = {
  titulo: '',
  descripcion: '',
  precio: '',
  direccion: '',
  distrito: '',
  tipo: 'habitacion',
  estado: 'activo',
};

export default function MisAlojamientos() {
  const [f, setF] = useState(inicial);
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [foto, setFoto] = useState(null);
  const [vistaPrevia, setVistaPrevia] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function cargar() {
    try {
      setItems(await get('/alojamientos/mis-publicaciones'));
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { cargar(); }, []);

  useEffect(() => {
    if (!mensaje) return undefined;
    const temporizador = setTimeout(() => setMensaje(''), 4500);
    return () => clearTimeout(temporizador);
  }, [mensaje]);

  useEffect(() => () => {
    if (vistaPrevia) URL.revokeObjectURL(vistaPrevia);
  }, [vistaPrevia]);

  function elegirFoto(archivo) {
    setFoto(archivo);
    setVistaPrevia(archivo ? URL.createObjectURL(archivo) : '');
  }

  async function crear(e) {
    e.preventDefault();
    setError('');
    setMensaje('');
    setEnviando(true);
    try {
      const item = await post('/alojamientos', {
        ...f,
        precio: Number(f.precio),
        comodidad_ids: [],
      });
      if (foto) await subir(`/alojamientos/${item.alojamiento_id}/imagenes`, foto);
      setMensaje(foto
        ? 'Publicación guardada con su foto. Ya aparece en el catálogo.'
        : 'Publicación guardada. Puedes agregarle una foto más adelante.');
      setF(inicial);
      elegirFoto(null);
      await cargar();
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  async function cambiarEstado(item) {
    try {
      await patch('/alojamientos/' + item.alojamiento_id, {
        estado: item.estado === 'activo' ? 'inactivo' : 'activo',
      });
      await cargar();
    } catch (e) {
      setError(e.message);
    }
  }

  async function quitar(item) {
    if (!confirm('¿Desactivar esta publicación?')) return;
    try {
      await del('/alojamientos/' + item.alojamiento_id);
      await cargar();
    } catch (e) {
      setError(e.message);
    }
  }

  return <main className="contenedor seccion">
    <p className="etiqueta">ARRENDADORES</p>
    <h1>Gestionar alojamientos</h1>
    <Mensaje error={error} correcto={mensaje} />
    <div className="dosColumnas">
      <section className="panel">
        <h2>Nueva publicación</h2>
        <form onSubmit={crear}>
          {Object.entries({
            titulo: 'Título',
            descripcion: 'Descripción',
            precio: 'Precio S/',
            direccion: 'Dirección',
            distrito: 'Distrito',
          }).map(([clave, etiqueta]) => <label key={clave}>{etiqueta}
            <input
              required
              value={f[clave]}
              type={clave === 'precio' ? 'number' : 'text'}
              min={clave === 'precio' ? '0.01' : undefined}
              step={clave === 'precio' ? '0.01' : undefined}
              onChange={e => setF({ ...f, [clave]: e.target.value })}
            />
          </label>)}
          <label>Tipo
            <select value={f.tipo} onChange={e => setF({ ...f, tipo: e.target.value })}>
              <option value="habitacion">Habitación</option>
              <option value="departamento">Departamento</option>
              <option value="casa">Casa</option>
              <option value="compartido">Compartido</option>
            </select>
          </label>
          <label>Foto de la habitación (opcional)
            <input type="file" accept="image/jpeg,image/png,image/webp" onChange={e => elegirFoto(e.target.files?.[0] || null)} />
            <span className="ayudaCampo">JPG, PNG o WebP, hasta 5 MB. Se mostrará en el catálogo.</span>
          </label>
          {vistaPrevia && <img className="vistaPrevia" src={vistaPrevia} alt="Vista previa de la foto" />}
          <button className="btn" type="submit" disabled={enviando}>{enviando ? 'Publicando…' : 'Publicar alojamiento'}</button>
        </form>
      </section>

      <section>
        <h2>Mis publicaciones</h2>
        {items.length === 0
          ? <div className="vacio">No tienes publicaciones todavía. Crea la primera con una foto para que los buscadores puedan verla.</div>
          : <div className="listaPublicaciones">
            {items.map(item => <article className="panel mini publicacionItem" key={item.alojamiento_id}>
              <div className="miniaturaPublicacion">
                {item.imagen_principal_id
                  ? <img src={`/api/alojamientos/imagenes/${item.imagen_principal_id}`} alt={`Foto de ${item.titulo}`} loading="lazy" />
                  : <span aria-hidden="true">⌂</span>}
              </div>
              <div className="publicacionDatos">
                <h3>{item.titulo}</h3>
                <p>{item.distrito} · S/ {Number(item.precio).toFixed(2)} · {item.estado}</p>
                <div className="acciones">
                  <button onClick={() => cambiarEstado(item)} className="btn secundario" type="button">
                    {item.estado === 'activo' ? 'Desactivar' : 'Activar'}
                  </button>
                  <button className="btn peligro" onClick={() => quitar(item)} type="button">Retirar</button>
                </div>
              </div>
            </article>)}
          </div>}
      </section>
    </div>
  </main>;
}
