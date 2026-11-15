/** Isotipo de AlojaRed: casa + destello sobre un azulejo con degradado azul-teal. */
export default function IconoMarca({ className = '' }) {
  return <span className={`marcaIcono ${className}`.trim()} aria-hidden="true">
    <svg viewBox="0 0 48 48" focusable="false">
      <path
        d="M24 9.2c.75 0 1.48.25 2.08.72l13.1 10.36c1.28 1.01 1.52 2.86.55 4.16a2.62 2.62 0 0 1-2.1 1.03h-1.1v9.08a4.05 4.05 0 0 1-4.05 4.05H15.52a4.05 4.05 0 0 1-4.05-4.05v-9.08h-1.1c-.83 0-1.61-.39-2.1-1.03a2.73 2.73 0 0 1 .55-4.16l13.1-10.36c.6-.47 1.33-.72 2.08-.72ZM20.9 38.6v-7.15a3.1 3.1 0 0 1 6.2 0v7.15Z"
        fill="#fff"
        fillRule="evenodd"
      />
      <path
        d="M38.4 8.4c.45 3 1.25 3.8 4.25 4.25-3 .45-3.8 1.25-4.25 4.25-.45-3-1.25-3.8-4.25-4.25 3-.45 3.8-1.25 4.25-4.25Z"
        fill="#ffe08a"
      />
    </svg>
  </span>;
}
