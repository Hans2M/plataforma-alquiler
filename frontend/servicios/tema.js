/** Preferencia de tema global (claro / oscuro) con persistencia local. */

export const CLAVE_TEMA = 'alojaRedTema';

export function temaGuardado() {
  try {
    const valor = localStorage.getItem(CLAVE_TEMA);
    return valor === 'claro' || valor === 'oscuro' ? valor : null;
  } catch (_) {
    return null;
  }
}

export function temaDelSistema() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro';
}

export function temaInicial() {
  const actual = document.documentElement.dataset.tema;
  if (actual === 'claro' || actual === 'oscuro') return actual;
  return temaGuardado() || temaDelSistema();
}

export function aplicarTema(tema) {
  const oscuro = tema === 'oscuro';
  document.documentElement.dataset.tema = tema;
  document.documentElement.style.colorScheme = oscuro ? 'dark' : 'light';
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', oscuro ? '#0a1420' : '#126daf');
}

export function guardarTema(tema) {
  try {
    localStorage.setItem(CLAVE_TEMA, tema);
  } catch (_) {
    /* El almacenamiento puede estar bloqueado; el tema sigue activo en la sesión. */
  }
}
