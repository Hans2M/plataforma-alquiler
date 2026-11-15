import React, { useEffect, useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import IconoMarca from './IconoMarca.jsx';
import IconoPanel from './IconosPanel.jsx';

export default function Encabezado({ usuario, salir, tema, alternarTema }) {
  const oscuro = tema === 'oscuro';
  const etiquetaTema = oscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';

  const [abierto, setAbierto] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => { setAbierto(false); }, [pathname]);

  const iniciales = (usuario?.nombre_completo || '')
    .trim().split(/\s+/).slice(0, 2).map((p) => p.charAt(0)).join('').toUpperCase();

  function cerrarSesion() {
    setAbierto(false);
    salir();
  }

  return <header className="header">
    <div className="contenedor barra">
      <Link className="marca" to="/" aria-label="AlojaRed, ir al inicio">
        <IconoMarca />
        <span className="marcaTexto">Aloja<span>Red</span></span>
      </Link>
      <nav id="menu-principal" className={abierto ? 'abierta' : ''} aria-label="Navegación principal">
        <NavLink to="/">Explorar</NavLink>
        {usuario && <NavLink to="/panel" className="navPerfil">
          <span className="avatarNav" aria-hidden="true">
            {usuario.foto_url
              ? <img src={usuario.foto_url} alt="" />
              : iniciales}
          </span>
          Mi panel
        </NavLink>}
        {usuario?.rol === 'arrendador' && <NavLink to="/mis-alojamientos">Mis alojamientos</NavLink>}
        {usuario?.rol === 'buscador' && <NavLink to="/companeros">Compartir vivienda</NavLink>}
        {usuario?.rol === 'administrador' && <NavLink to="/administracion">Administración</NavLink>}
        {usuario && <NavLink to="/verificacion">Identidad</NavLink>}
        {usuario
          ? <button className="btn secundario" onClick={cerrarSesion}>Salir</button>
          : <><NavLink to="/ingresar">Ingresar</NavLink><Link className="btn" to="/registro">Registrarse</Link></>}
      </nav>
      <button
        className="botonTema"
        type="button"
        aria-label={etiquetaTema}
        aria-pressed={oscuro}
        title={etiquetaTema}
        onClick={alternarTema}
      >
        <IconoPanel nombre={oscuro ? 'sol' : 'luna'} tamano={20} />
      </button>
      <button
        className="menuBoton"
        type="button"
        aria-expanded={abierto}
        aria-controls="menu-principal"
        aria-label={abierto ? 'Cerrar menú' : 'Abrir menú'}
        onClick={() => setAbierto(!abierto)}
      >
        <span /><span /><span />
      </button>
    </div>
  </header>;
}
