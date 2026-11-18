import React from 'react';
import { Link } from 'react-router-dom';

function textoPublicacion(fecha) {
  if (!fecha) return '';
  const valor = new Date(fecha);
  if (Number.isNaN(valor.getTime())) return '';
  const dias = Math.floor((Date.now() - valor.getTime()) / 86400000);
  if (dias <= 0) return 'Publicado hoy';
  if (dias === 1) return 'Publicado ayer';
  if (dias < 30) return `Publicado hace ${dias} días`;
  return `Publicado el ${valor.toLocaleDateString('es-PE', {
    day: '2-digit', month: 'short', year: 'numeric',
  })}`;
}

export default function Tarjeta({ item }) {
  const foto = item.imagen_principal_id
    ? `/api/alojamientos/imagenes/${item.imagen_principal_id}`
    : null;
  const publicado = textoPublicacion(item.fecha_publicacion);
  return <Link className="tarjeta opcion" to={`/alojamientos/${item.alojamiento_id}`} aria-label={`Ver detalle de ${item.titulo}`}>
    <div className={foto ? 'fotoTarjetaMarco' : 'imagenFalsa'}>
      {foto
        ? <img className="fotoTarjeta" src={foto} alt={`Foto de ${item.titulo}`} loading="lazy" />
        : <span aria-hidden="true">⌂</span>}
      <span className="chip">{item.tipo_nombre || item.tipo}</span>
    </div>
    <div className="tarjetaContenido">
      <h3>{item.titulo}</h3>
      <p>{item.distrito_completo || item.distrito} · {item.direccion}</p>
      <p className="clamp">{item.descripcion}</p>
      {publicado && <p className="tarjetaFecha">{publicado}</p>}
      <div className="tarjetaPie"><strong>S/ {Number(item.precio).toFixed(2)}</strong><span className="verDetalle">Ver detalle →</span></div>
    </div>
  </Link>;
}
