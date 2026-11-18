import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import IconoWhatsApp from '../../componentes/comunes/IconoWhatsApp.jsx';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import { get } from '../../servicios/api.js';
import { enlaceWhatsApp, mensajeAlojamiento } from '../../servicios/whatsapp.js';

function formatearTelefono(telefono) {
  const digitos = String(telefono || '').replace(/\D/g, '');
  if (digitos.length !== 9) return telefono || 'No registrado';
  return `+51 ${digitos.slice(0, 3)} ${digitos.slice(3, 6)} ${digitos.slice(6)}`;
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  const valor = new Date(fecha);
  return Number.isNaN(valor.getTime()) ? '' : valor.toLocaleDateString('es-PE', {
    day: '2-digit', month: 'long', year: 'numeric',
  });
}

export default function DetalleAlojamiento({ usuario }) {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [imagenes, setImagenes] = useState([]);
  const [activa, setActiva] = useState(0);
  const [contacto, setContacto] = useState(null);
  const [error, setError] = useState('');
  const [errorContacto, setErrorContacto] = useState('');
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError('');
    setActiva(0);
    Promise.all([
      get(`/alojamientos/${id}`),
      get(`/alojamientos/${id}/imagenes`).catch(() => []),
    ]).then(([alojamiento, fotos]) => {
      if (!vigente) return;
      setItem(alojamiento);
      setImagenes(Array.isArray(fotos) ? fotos : []);
    }).catch((e) => vigente && setError(e.message))
      .finally(() => vigente && setCargando(false));
    return () => { vigente = false; };
  }, [id]);

  const puedeContactar = usuario?.rol === 'buscador';

  useEffect(() => {
    if (!puedeContactar || !item) {
      setContacto(null);
      setErrorContacto('');
      return undefined;
    }
    let vigente = true;
    setErrorContacto('');
    get(`/alojamientos/${id}/contacto`)
      .then((datos) => vigente && setContacto(datos))
      .catch((e) => vigente && setErrorContacto(e.message));
    return () => { vigente = false; };
  }, [id, puedeContactar, item]);

  if (cargando) {
    return <main className="contenedor seccion"><p>Cargando alojamiento…</p></main>;
  }

  if (error || !item) {
    return <main className="contenedor seccion">
      <Mensaje error={error || 'Alojamiento no disponible'} />
      <Link className="btn secundario" to="/">Volver al catálogo</Link>
    </main>;
  }

  const principal = imagenes[activa]?.url
    || (item.imagen_principal_id ? `/api/alojamientos/imagenes/${item.imagen_principal_id}` : null);
  const enlace = contacto?.telefono
    ? enlaceWhatsApp(contacto.telefono, mensajeAlojamiento({
      ...item,
      nombre_arrendador: contacto.nombre_completo,
    }))
    : null;

  return <main className="contenedor seccion detalleAlojamiento">
    <Link className="volver" to="/">← Volver al catálogo</Link>
    <div className="detalleColumnas">
      <section>
        <div className={principal ? 'fotoPrincipalMarco' : 'fotoPrincipalMarco vacia'}>
          {principal
            ? <img className="fotoPrincipal" src={principal} alt={`Foto de ${item.titulo}`} />
            : <span aria-hidden="true">⌂</span>}
          <span className="chip chipTipo">{item.tipo_nombre || item.tipo}</span>
        </div>
        {imagenes.length > 1 && <div className="miniaturas" aria-label="Galería de fotos">
          {imagenes.map((foto, indice) => <button
            key={foto.imagen_id}
            type="button"
            className={indice === activa ? 'miniatura activa' : 'miniatura'}
            onClick={() => setActiva(indice)}
            aria-label={`Ver foto ${indice + 1}`}
          >
            <img src={foto.url} alt={`Vista ${indice + 1} de ${item.titulo}`} loading="lazy" />
          </button>)}
        </div>}

        <div className="panel detalleDescripcion">
          <p className="etiqueta">{item.distrito_completo || item.distrito}</p>
          <h1>{item.titulo}</h1>
          <p className="detalleDireccion">📍 {item.direccion}</p>
          <p className="detallePrecio">S/ {Number(item.precio).toFixed(2)} <small>/ mes</small></p>
          <p>{item.descripcion}</p>
          <p className="detalleFecha">Publicado el {formatearFecha(item.fecha_publicacion)}</p>
        </div>
      </section>

      <aside className="panel panelContacto">
        <h2>{puedeContactar ? 'Contacta al arrendador' : 'Contacto protegido'}</h2>
        {!usuario && <>
          <p>Inicia sesión para ver el teléfono y comunicarte por WhatsApp con la persona que publica este alojamiento.</p>
          <Link className="btn ancho" to="/ingresar">Iniciar sesión</Link>
          <p className="textoPequeno">¿Aún no tienes cuenta? <Link to="/registro">Regístrate gratis</Link>.</p>
        </>}

        {usuario && !puedeContactar && <div className="contactoReservado">
          <span className="contactoReservadoIcono" aria-hidden="true">🔒</span>
          <p>
            {usuario.rol === 'arrendador'
              ? 'Estás explorando la publicación de otro arrendador.'
              : 'Estás revisando esta publicación como administrador.'}
          </p>
          <p className="textoPequeno">
            Puedes comparar el precio, las fotos y la descripción. El teléfono y el
            WhatsApp del arrendador están reservados para cuentas de buscador.
          </p>
          {usuario.rol === 'arrendador' && <Link className="btn secundario ancho" to="/mis-alojamientos">
            Gestionar mis alojamientos
          </Link>}
          {usuario.rol === 'administrador' && <Link className="btn secundario ancho" to="/administracion">
            Ir a administración
          </Link>}
        </div>}

        {puedeContactar && errorContacto && <Mensaje error={errorContacto} />}

        {puedeContactar && !contacto && !errorContacto && <p>Cargando datos de contacto…</p>}

        {puedeContactar && contacto && <>
          <div className="contactoArrendador">
            <span className="avatarContacto" aria-hidden="true">{contacto.nombre_completo.charAt(0).toUpperCase()}</span>
            <div>
              <strong>{contacto.nombre_completo}</strong>
              <p className="textoPequeno">{contacto.correo}</p>
            </div>
          </div>
          <p className="telefonoContacto">
            <span aria-hidden="true">📱</span> {formatearTelefono(contacto.telefono)}
          </p>
          {enlace
            ? <a className="btn whatsapp ancho" href={enlace} target="_blank" rel="noopener noreferrer">
              <IconoWhatsApp /> Escribir por WhatsApp
            </a>
            : <p className="aviso">El arrendador aún no registró un teléfono de contacto.</p>}
          <p className="textoPequeno">El mensaje se abrirá con una presentación y los datos de esta publicación.</p>
        </>}
      </aside>
    </div>
  </main>;
}
