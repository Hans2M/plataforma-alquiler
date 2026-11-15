import React from 'react';

const TRAZOS = {
  buscar: <>
    <circle cx="11" cy="11" r="6.5" />
    <path d="m16 16 4.5 4.5" />
  </>,
  personas: <>
    <circle cx="9" cy="8.5" r="3.2" />
    <path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5" />
    <path d="M16 5.6a3 3 0 0 1 0 5.8M17.5 14.2c1.9.6 3 2.1 3 4.8" />
  </>,
  escudo: <>
    <path d="M12 3.2 5 6v5.5c0 4.3 2.9 7.6 7 9.3 4.1-1.7 7-5 7-9.3V6l-7-2.8Z" />
    <path d="m9 12 2 2 4-4" />
  </>,
  casa: <>
    <path d="m3.5 10.5 8.5-7 8.5 7" />
    <path d="M5.5 9.5V20h13V9.5" />
    <path d="M10 20v-5.5h4V20" />
  </>,
  edificio: <>
    <path d="M4 20V5.5A1.5 1.5 0 0 1 5.5 4h7A1.5 1.5 0 0 1 14 5.5V20" />
    <path d="M14 9h4.5A1.5 1.5 0 0 1 20 10.5V20M2.5 20h19" />
    <path d="M7 8h2M7 11.5h2M7 15h2M16.5 12.5h1M16.5 16h1" />
  </>,
  catalogo: <>
    <rect x="3.5" y="4.5" width="7" height="7" rx="1.5" />
    <rect x="13.5" y="4.5" width="7" height="7" rx="1.5" />
    <rect x="3.5" y="14.5" width="7" height="5" rx="1.5" />
    <rect x="13.5" y="14.5" width="7" height="5" rx="1.5" />
  </>,
  ajustes: <>
    <path d="M4 7h9M17 7h3M4 17h3M11 17h9" />
    <circle cx="15" cy="7" r="2" />
    <circle cx="9" cy="17" r="2" />
  </>,
  camara: <>
    <path d="M4 8.5h3l1.5-2h7L17 8.5h3a1.5 1.5 0 0 1 1.5 1.5v8A1.5 1.5 0 0 1 20 19.5H4A1.5 1.5 0 0 1 2.5 18v-8A1.5 1.5 0 0 1 4 8.5Z" />
    <circle cx="12" cy="13.8" r="3.3" />
  </>,
  check: <path d="m5 12.5 4.5 4.5L19 7.5" />,
  reloj: <>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 7.5V12l3 2" />
  </>,
  alerta: <>
    <path d="M12 3.5 21 20H3L12 3.5Z" />
    <path d="M12 9.5v4.5M12 17.2v.3" />
  </>,
  usuario: <>
    <circle cx="12" cy="8" r="3.8" />
    <path d="M4.5 20c0-3.9 3.4-6.3 7.5-6.3s7.5 2.4 7.5 6.3" />
  </>,
  basura: <>
    <path d="M4.5 7h15M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13" />
    <path d="M10.5 10.5v6M13.5 10.5v6" />
  </>,
  sol: <>
    <circle cx="12" cy="12" r="4.2" />
    <path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M18.7 5.3l-1.6 1.6M6.9 17.1l-1.6 1.6" />
  </>,
  luna: <path d="M20.2 14.3A8.6 8.6 0 0 1 9.7 3.8a8.6 8.6 0 1 0 10.5 10.5Z" />,
};

export default function IconoPanel({ nombre, tamano = 24 }) {
  return <svg
    viewBox="0 0 24 24"
    width={tamano}
    height={tamano}
    fill="none"
    stroke="currentColor"
    strokeWidth="1.7"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    {TRAZOS[nombre] || null}
  </svg>;
}
