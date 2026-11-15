const API = '/api';
export function token() { return sessionStorage.getItem('token_alquiler'); }
export function guardarToken(valor) { sessionStorage.setItem('token_alquiler', valor); }
export function cerrarToken() { sessionStorage.removeItem('token_alquiler'); }

const ETIQUETAS = {
  nombre_completo: 'Nombre completo',
  correo: 'Correo',
  contrasena: 'Contraseña',
  telefono: 'Teléfono',
  tipo_documento: 'Tipo de documento',
  numero_documento: 'Número de documento',
  ruc: 'RUC',
  titulo: 'Título',
  descripcion: 'Descripción',
  precio: 'Precio',
  direccion: 'Dirección',
  distrito: 'Distrito',
  tipo: 'Tipo',
  estado: 'Estado',
  presupuesto_min: 'Presupuesto mínimo',
  presupuesto_max: 'Presupuesto máximo',
  observacion: 'Observación',
  decision: 'Decisión',
  estado_cuenta: 'Estado de cuenta',
};

function traducir(mensaje = '') {
  if (/field required/i.test(mensaje)) return 'es obligatorio';
  const minimo = mensaje.match(/at least (\d+) characters?/i);
  if (minimo) return `debe tener al menos ${minimo[1]} caracteres`;
  const maximo = mensaje.match(/at most (\d+) characters?/i);
  if (maximo) return `debe tener como máximo ${maximo[1]} caracteres`;
  if (/valid email/i.test(mensaje)) return 'no es un correo electrónico válido';
  if (/string should match pattern/i.test(mensaje)) return 'tiene un formato no válido';
  if (/input should be a valid (integer|number)/i.test(mensaje)) return 'debe ser un número válido';
  if (/input should be a valid string/i.test(mensaje)) return 'debe ser texto válido';
  const opciones = mensaje.match(/input should be (.+)/i);
  if (opciones) return `debe ser ${opciones[1]}`;
  if (/greater than 0/i.test(mensaje)) return 'debe ser mayor que cero';
  const valorError = mensaje.match(/^value error,\s*(.+)$/i);
  if (valorError) return valorError[1];
  return mensaje.replace(/\.$/, '');
}

function describirError(item) {
  const campo = (item.loc || []).filter((parte) => !['body', 'query', 'path'].includes(parte)).join('.');
  const detalle = traducir(item.msg);
  return campo ? `${ETIQUETAS[campo] || campo}: ${detalle}` : detalle;
}

export function mensajeDeError(dato, estado) {
  const detalle = dato?.detail;
  if (typeof detalle === 'string' && detalle.trim()) return detalle;
  if (Array.isArray(detalle) && detalle.length) {
    const mensajes = detalle.map(describirError).filter(Boolean);
    if (mensajes.length) return [...new Set(mensajes)].join(' · ');
  }
  if (estado === 409) return 'Ya existe un registro con esos datos';
  if (estado === 401) return 'Correo o contraseña incorrectos';
  if (estado === 403) return 'No tienes permiso para esta acción';
  if (estado === 404) return 'No se encontró el recurso solicitado';
  if (estado >= 500) return 'Ocurrió un error en el servidor. Inténtalo más tarde';
  return 'No se pudo completar la operación';
}

export async function solicitar(ruta, opciones = {}) {
  const cabeceras = { ...opciones.headers };
  if (!(opciones.body instanceof FormData)) cabeceras['Content-Type'] = 'application/json';
  if (token()) cabeceras.Authorization = `Bearer ${token()}`;
  const respuesta = await fetch(API + ruta, { ...opciones, headers: cabeceras });
  if (!respuesta.ok) {
    const dato = await respuesta.json().catch(() => ({}));
    throw new Error(mensajeDeError(dato, respuesta.status));
  }
  if (respuesta.status === 204) return null;
  return respuesta.json();
}

export const get = (ruta) => solicitar(ruta);
export const post = (ruta, obj) => solicitar(ruta, { method: 'POST', body: JSON.stringify(obj) });
export const put = (ruta, obj) => solicitar(ruta, { method: 'PUT', body: JSON.stringify(obj) });
export const patch = (ruta, obj) => solicitar(ruta, { method: 'PATCH', body: JSON.stringify(obj) });
export const del = (ruta) => solicitar(ruta, { method: 'DELETE' });
export const subir = (ruta, archivo) => { const datos = new FormData(); datos.append('archivo', archivo); return solicitar(ruta, { method: 'POST', body: datos }); };
