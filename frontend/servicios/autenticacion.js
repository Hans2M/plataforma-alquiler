import { get, post, token, guardarToken, cerrarToken } from './api.js';

export async function iniciarSesion(correo, contrasena) {
  const respuesta = await post('/autenticacion/login', { correo, contrasena });
  guardarToken(respuesta.access_token);
  return get('/usuarios/me');
}
export const perfilActual = () => token() ? get('/usuarios/me') : Promise.resolve(null);
export async function cerrarSesion() {
  if (token()) { try { await post('/autenticacion/logout', {}); } catch (_) { /* un token vencido puede rechazarse */ } }
  cerrarToken();
}
