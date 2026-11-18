import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Tarjeta from '../../componentes/alojamientos/Tarjeta.jsx';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import IconoPanel from '../../componentes/comunes/IconosPanel.jsx';
import SelectorUbigeo from '../../componentes/ubigeo/SelectorUbigeo.jsx';
import { get } from '../../servicios/api.js';
import { useCatalogosAlojamiento } from '../../servicios/catalogos.js';

const VACIO = {
  texto: '',
  distrito: '',
  departamento_id: '',
  provincia_id: '',
  distrito_id: '',
  tipo: '',
  precio_min: '',
  precio_max: '',
  dias: '',
  orden: 'recientes',
};

const FECHAS = [
  ['', 'Cualquier fecha'],
  ['1', 'Últimas 24 h'],
  ['7', 'Última semana'],
  ['30', 'Último mes'],
];

const ORDENES = [
  ['recientes', 'Más recientes'],
  ['precio_asc', 'Menor precio'],
  ['precio_desc', 'Mayor precio'],
];

function parametros(filtros) {
  const params = new URLSearchParams();
  Object.entries(filtros).forEach(([clave, valor]) => {
    if (valor !== '' && valor !== null && valor !== undefined) {
      params.set(clave, valor);
    }
  });
  return params;
}

export default function Inicio({ usuario }) {
  const [f, setF] = useState(VACIO);
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const [filtrosAbiertos, setFiltrosAbiertos] = useState(false);
  const catalogos = useCatalogosAlojamiento();

  async function buscar(evento, filtros = f) {
    evento?.preventDefault();
    setError('');

    const minimo = Number(filtros.precio_min);
    const maximo = Number(filtros.precio_max);
    if (filtros.precio_min !== '' && filtros.precio_max !== '' && minimo > maximo) {
      return setError('El precio mínimo no puede superar al precio máximo.');
    }

    setCargando(true);
    try {
      setItems(await get('/alojamientos?' + parametros(filtros)));
    } catch (e) {
      setError(e.message);
      setItems([]);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => { buscar(); }, []);

  function cambiar(campo, valor) {
    if (error) setError('');
    setF({ ...f, [campo]: valor });
  }

  function aplicar(cambios) {
    const siguientes = { ...f, ...cambios };
    setF(siguientes);
    buscar(null, siguientes);
  }

  function limpiar() {
    setF(VACIO);
    buscar(null, VACIO);
  }

  const hayFiltros = f.texto !== '' || f.distrito !== ''
    || f.departamento_id !== '' || f.provincia_id !== '' || f.distrito_id !== ''
    || f.tipo !== '' || f.precio_min !== '' || f.precio_max !== '' || f.dias !== ''
    || f.orden !== 'recientes';

  const filtrosActivos = [
    f.tipo,
    f.departamento_id,
    f.provincia_id,
    f.distrito_id,
    f.precio_min,
    f.precio_max,
    f.dias,
    f.orden === 'recientes' ? '' : f.orden,
  ].filter(Boolean).length;

  function cambiarUbigeo(ubicacion) {
    aplicar({
      departamento_id: ubicacion.departamentoId,
      provincia_id: ubicacion.provinciaId,
      distrito_id: ubicacion.distritoId,
    });
  }

  return <>
    <section className="hero"><div className="contenedor">
      <div className="etiqueta">Encuentra tu próximo espacio</div>
      <h1>Tu nuevo alojamiento, <em>más cerca.</em></h1>
      <p>Busca habitaciones, departamentos y casas, sin importar tu ocupación.</p>

      <form
        className={`buscador ${filtrosAbiertos ? 'filtrosAbiertos' : ''}`}
        onSubmit={buscar}
        role="search"
        aria-label="Buscar alojamientos"
      >
        <div className="buscadorCampos">
          <label className="campoBuscador">
            <span>¿Qué buscas?</span>
            <span className="campoConIcono">
              <IconoPanel nombre="buscar" tamano={18} />
              <input
                aria-label="Buscar por nombre"
                placeholder="Ej. habitación"
                value={f.texto}
                onChange={e => cambiar('texto', e.target.value)}
              />
            </span>
          </label>

          <label className="campoBuscador">
            <span>Distrito o ciudad</span>
            <input
              aria-label="Distrito o ciudad"
              placeholder="Ej. Tingo María"
              value={f.distrito}
              onChange={e => cambiar('distrito', e.target.value)}
            />
          </label>

          <label className="campoBuscador avanzado campoCompleto">
            <span>Tipo de alojamiento</span>
            <select
              aria-label="Tipo de alojamiento"
              value={f.tipo}
              onChange={e => aplicar({ tipo: e.target.value })}
            >
              <option value="">Todos los tipos</option>
              {catalogos.tipos.map((tipo) => (
                <option key={tipo.tipo_id} value={tipo.codigo}>{tipo.nombre}</option>
              ))}
            </select>
          </label>

          <label className="campoBuscador avanzado">
            <span>Precio mín. (S/)</span>
            <input
              aria-label="Precio mínimo"
              type="number"
              inputMode="decimal"
              min="0"
              placeholder="0"
              value={f.precio_min}
              onChange={e => cambiar('precio_min', e.target.value)}
            />
          </label>

          <label className="campoBuscador avanzado">
            <span>Precio máx. (S/)</span>
            <input
              aria-label="Precio máximo"
              type="number"
              inputMode="decimal"
              min="0"
              placeholder="Sin límite"
              value={f.precio_max}
              onChange={e => cambiar('precio_max', e.target.value)}
            />
          </label>

          <div className="buscadorAcciones">
            <button className="btn buscadorBoton" type="submit">Buscar</button>
            <button
              type="button"
              className="buscadorToggle"
              aria-expanded={filtrosAbiertos}
              aria-controls="filtrosBuscador"
              onClick={() => setFiltrosAbiertos(abiertos => !abiertos)}
            >
              <IconoPanel nombre="ajustes" tamano={17} />
              Filtros
              {filtrosActivos > 0 && <span className="contadorFiltros">{filtrosActivos}</span>}
              <svg
                className="chevronFiltros"
                viewBox="0 0 24 24"
                width="16"
                height="16"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </button>
          </div>
        </div>

        <div className="buscadorFiltros" id="filtrosBuscador">
          <div className="filtroUbigeo">
            <span className="buscadorEtiqueta">Ubicación exacta (UBIGEO)</span>
            <SelectorUbigeo
              variante="buscador"
              departamentos={catalogos.departamentos}
              departamentoId={f.departamento_id}
              provinciaId={f.provincia_id}
              distritoId={f.distrito_id}
              onCambio={cambiarUbigeo}
            />
          </div>

          <div className="chipsFecha" role="group" aria-label="Fecha de publicación">
            <span className="buscadorEtiqueta">Publicado</span>
            {FECHAS.map(([valor, etiqueta]) => <button
              key={valor || 'todas'}
              type="button"
              className={`chipFiltro ${f.dias === valor ? 'activo' : ''}`}
              aria-pressed={f.dias === valor}
              onClick={() => aplicar({ dias: valor })}
            >{etiqueta}</button>)}
          </div>

          <label className="ordenCampo">
            <span>Ordenar por</span>
            <select
              aria-label="Ordenar por"
              value={f.orden}
              onChange={e => aplicar({ orden: e.target.value })}
            >
              {ORDENES.map(([valor, etiqueta]) => (
                <option key={valor} value={valor}>{etiqueta}</option>
              ))}
            </select>
          </label>

          <button type="button" className="limpiarFiltros" onClick={limpiar}>
            Limpiar filtros
          </button>
        </div>
      </form>
    </div></section>

    <section className="contenedor seccion">
      <div className="seccionTitulo">
        <div>
          <p className="etiqueta">ALOJAMIENTOS</p>
          <h2>{hayFiltros ? 'Resultados de tu búsqueda' : 'Espacios disponibles'}</h2>
        </div>
        <p className="resultadosConteo" aria-live="polite">
          {cargando
            ? 'Buscando…'
            : <><strong>{items.length}</strong> {items.length === 1 ? 'espacio' : 'espacios'}</>}
        </p>
      </div>

      {usuario?.rol === 'arrendador' && <div className="avisoCatalogo">
        <div>
          <strong>Estás explorando el catálogo público</strong>
          <p>Compara precios y características de otras publicaciones. El contacto directo está reservado a cuentas de buscador.</p>
        </div>
        <Link className="btn secundario" to="/mis-alojamientos">Mis alojamientos</Link>
      </div>}

      <Mensaje error={error} />
      {cargando
        ? <p>Cargando alojamientos…</p>
        : items.length
          ? <div className="rejilla">{items.map(i => <Tarjeta key={i.alojamiento_id} item={i} />)}</div>
          : <div className="vacio">
            {hayFiltros
              ? <>
                <p>No encontramos alojamientos con esos filtros. Prueba ampliando el precio o cambiando el distrito.</p>
                <button className="btn secundario" type="button" onClick={limpiar}>Limpiar filtros</button>
              </>
              : 'Aún no hay alojamientos publicados. Los arrendadores pueden crear el primero.'}
          </div>}
    </section>
  </>;
}
