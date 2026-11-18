import React, { useEffect, useState } from 'react';
import { get, post, patch, del, subir } from '../../servicios/api.js';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import SelectorUbigeo from '../../componentes/ubigeo/SelectorUbigeo.jsx';
import { useCatalogosAlojamiento } from '../../servicios/catalogos.js';

const inicial = {
  titulo: '',
  descripcion: '',
  precio: '',
  direccion: '',
  departamento_id: '',
  provincia_id: '',
  distrito_id: '',
  tipo_id: '',
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
  const catalogos = useCatalogosAlojamiento();

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
    if (!f.distrito_id) return setError('Selecciona el departamento, la provincia y el distrito.');
    if (!f.tipo_id) return setError('Selecciona el tipo de alojamiento.');
    setEnviando(true);
    try {
      const item = await post('/alojamientos', {
        titulo: f.titulo,
        descripcion: f.descripcion,
        precio: Number(f.precio),
        direccion: f.direccion,
        distrito_id: Number(f.distrito_id),
        tipo_id: Number(f.tipo_id),
        estado: f.estado,
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

          <SelectorUbigeo
            departamentos={catalogos.departamentos}
            departamentoId={f.departamento_id}
            provinciaId={f.provincia_id}
            distritoId={f.distrito_id}
            requerido
            onCambio={(ubicacion) => setF((actual) => ({
              ...actual,
              departamento_id: ubicacion.departamentoId,
              provincia_id: ubicacion.provinciaId,
              distrito_id: ubicacion.distritoId,
            }))}
          />

          <label>Tipo de alojamiento
            <select
              required
              value={f.tipo_id}
              onChange={e => setF({ ...f, tipo_id: e.target.value })}
            >
              <option value="">Selecciona un tipo</option>
              {catalogos.tipos.map((tipo) => (
                <option key={tipo.tipo_id} value={tipo.tipo_id}>{tipo.nombre}</option>
              ))}
            </select>
          </label>
          <p className="ayudaCampo">
            Los tipos disponibles los administra la plataforma y pueden cambiar con el tiempo.
          </p>

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
                <p>{item.distrito_completo || item.distrito} · {item.tipo_nombre || item.tipo} · S/ {Number(item.precio).toFixed(2)} · {item.estado}</p>
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
