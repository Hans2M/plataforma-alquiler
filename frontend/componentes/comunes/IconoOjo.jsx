import React from 'react';

/**
 * Icono de ojo para alternar la visibilidad de una contraseña.
 * `abierto` dibuja el ojo abierto; en caso contrario, el ojo tachado.
 */
export default function IconoOjo({ abierto = false }) {
  return <svg
    viewBox="0 0 24 24"
    width="20"
    height="20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    {abierto
      ? <>
        <path d="M2.5 12s3.5-6.5 9.5-6.5S21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z" />
        <circle cx="12" cy="12" r="3" />
      </>
      : <>
        <path d="m3 3 18 18" />
        <path d="M10.6 10.7a3 3 0 0 0 4.2 4.2" />
        <path d="M9.9 5.4A10.9 10.9 0 0 1 12 5.2c6 0 9.5 6.8 9.5 6.8a17.7 17.7 0 0 1-3.2 4.1" />
        <path d="M6.2 6.4C3.9 8 2.5 12 2.5 12s3.5 6.8 9.5 6.8c1.6 0 3-.4 4.2-1.1" />
      </>}
  </svg>;
}
