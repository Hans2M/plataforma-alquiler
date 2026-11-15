import React from 'react';
export default function Mensaje({ error, correcto }) {
  return <>{error && <p className="alerta error" role="alert">{error}</p>}{correcto && <p className="alerta exito" role="status">{correcto}</p>}</>;
}
