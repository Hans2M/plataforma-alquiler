import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Encabezado from './componentes/comunes/Encabezado.jsx';
import Rutas from './rutas/Rutas.jsx';
import { perfilActual, cerrarSesion } from './servicios/autenticacion.js';
import { aplicarTema, guardarTema, temaGuardado, temaInicial } from './servicios/tema.js';

export default function App() {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [tema, setTema] = useState(temaInicial);
  const navegar = useNavigate();

  useEffect(() => {
    perfilActual()
      .then(setUsuario)
      .catch(() => {})
      .finally(() => setCargando(false));
  }, []);

  useEffect(() => {
    aplicarTema(tema);
  }, [tema]);

  useEffect(() => {
    const consulta = window.matchMedia?.('(prefers-color-scheme: dark)');
    if (!consulta) return undefined;
    const alCambiar = (evento) => {
      if (!temaGuardado()) setTema(evento.matches ? 'oscuro' : 'claro');
    };
    consulta.addEventListener?.('change', alCambiar);
    return () => consulta.removeEventListener?.('change', alCambiar);
  }, []);

  async function salir() {
    await cerrarSesion();
    setUsuario(null);
    navegar('/');
  }

  function alternarTema() {
    setTema((actual) => {
      const nuevo = actual === 'oscuro' ? 'claro' : 'oscuro';
      guardarTema(nuevo);
      return nuevo;
    });
  }

  return <>
    <Encabezado
      usuario={usuario}
      salir={salir}
      tema={tema}
      alternarTema={alternarTema}
    />
    {cargando
      ? <main className="contenedor seccion">Cargando sesión…</main>
      : <Rutas usuario={usuario} alIngresar={setUsuario} />}
    <footer className="pie">
      <div className="contenedor">
        Plataforma Web de Gestión y Búsqueda de Alojamientos · Proyecto académico · 2026-II
      </div>
    </footer>
  </>;
}
