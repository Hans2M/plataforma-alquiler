/** Utilidades de contacto por WhatsApp (Perú, +51). */

export function numeroWhatsApp(telefono) {
  const digitos = String(telefono || '').replace(/\D/g, '');
  if (!digitos) return '';
  if (digitos.length === 11 && digitos.startsWith('51')) return digitos;
  if (digitos.length === 9) return `51${digitos}`;
  return digitos;
}

export function enlaceWhatsApp(telefono, mensaje) {
  const numero = numeroWhatsApp(telefono);
  if (!numero) return null;
  return `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`;
}

export function mensajeAlojamiento(alojamiento) {
  const precio = Number(alojamiento.precio).toFixed(2);
  return (
    `Hola ${alojamiento.nombre_arrendador || ''}, vi tu publicación "${alojamiento.titulo}" ` +
    `en AlojaRed (${alojamiento.distrito}, S/ ${precio}) y me interesa alquilarla. ` +
    '¿Podemos coordinar una visita o conversar sobre la disponibilidad?'
  ).replace(/\s+/g, ' ').trim();
}

export function mensajeCompanero(coincidencia, propio) {
  const desde = Number(propio?.presupuesto_min ?? 0).toFixed(0);
  const hasta = Number(propio?.presupuesto_max ?? 0).toFixed(0);
  const nombre = (coincidencia?.nombre_completo || '').trim().split(/\s+/)[0];
  const saludo = nombre ? `Hola ${nombre},` : 'Hola,';
  return (
    `${saludo} vi tu perfil de convivencia en AlojaRed. ` +
    `Busco compartir alojamiento con un presupuesto entre S/ ${desde} y S/ ${hasta}, ` +
    'y nuestros rangos coinciden. ¿Te gustaría conversar para conocer más?'
  ).replace(/\s+/g, ' ').trim();
}
