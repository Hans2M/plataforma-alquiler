import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import MarcoAutenticacion from '../../componentes/autenticacion/MarcoAutenticacion.jsx';
import IconoPanel from '../../componentes/comunes/IconosPanel.jsx';
import IconoOjo from '../../componentes/comunes/IconoOjo.jsx';
import { iniciarSesion } from '../../servicios/autenticacion.js';

export default function Login({ alIngresar }) {
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [verContrasena, setVerContrasena] = useState(false);
  const [error, setError] = useState('');
  const navegar = useNavigate();

  async function entrar(e) {
    e.preventDefault();
    setError('');
    try {
      const u = await iniciarSesion(correo, contrasena);
      alIngresar(u);
      navegar('/panel');
    } catch (err) {
      setError(err.message);
    }
  }

  return <MarcoAutenticacion variante="ingresar">
    <header className="cabeceraAuth">
      <p className="etiqueta">BIENVENIDO</p>
      <h1>Iniciar sesión</h1>
      <p>Accede a tu panel, tus contactos y tus publicaciones guardadas.</p>
    </header>

    <Mensaje error={error} />

    <form className="formAuth" onSubmit={entrar}>
      <div className="campoConEtiqueta">
        <label htmlFor="login-correo">Correo electrónico</label>
        <span className="campoIconoAuth">
          <IconoPanel nombre="usuario" tamano={18} />
          <input
            type="email"
            id="login-correo"
            autoComplete="email"
            inputMode="email"
            required
            placeholder="tucorreo@ejemplo.com"
            value={correo}
            onChange={e => setCorreo(e.target.value)}
          />
        </span>
      </div>

      <div className="campoConEtiqueta">
        <label htmlFor="login-contrasena">Contraseña</label>
        <span className="campoIconoAuth">
          <IconoPanel nombre="escudo" tamano={18} />
          <input
            id="login-contrasena"
            className="conOjo"
            type={verContrasena ? 'text' : 'password'}
            autoComplete="current-password"
            required
            placeholder="Tu contraseña"
            value={contrasena}
            onChange={e => setContrasena(e.target.value)}
          />
          <button
            type="button"
            className="botonVer"
            aria-label={verContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            aria-pressed={verContrasena}
            title={verContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            onClick={e => { e.preventDefault(); setVerContrasena(v => !v); }}
          ><IconoOjo abierto={verContrasena} /></button>
        </span>
      </div>

      <button className="btn ancho btnAuth" type="submit">
        Ingresar
        <span aria-hidden="true">→</span>
      </button>
    </form>

    <p className="pieAuth">
      <span>¿Aún no tienes cuenta?</span>
      <Link to="/registro">Crear cuenta gratis</Link>
    </p>
  </MarcoAutenticacion>;
}
