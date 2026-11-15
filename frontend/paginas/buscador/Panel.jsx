import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import IconoPanel from '../../componentes/comunes/IconosPanel.jsx';
import Mensaje from '../../componentes/comunes/Mensaje.jsx';
import { del, subir } from '../../servicios/api.js';

const PERMITIDOS = ['image/jpeg', 'image/png', 'image/webp'];
const TAMANO_MAXIMO = 5 * 1024 * 1024;

const ROLES = {
  buscador: { etiqueta: 'Buscador', icono: 'buscar' },
  arrendador: { etiqueta: 'Arrendador', icono: 'edificio' },
  administrador: { etiqueta: 'Administrador', icono: 'ajustes' },
};

const ESTADOS = {
  verificada: { etiqueta: 'Cuenta verificada', icono: 'check', tono: 'ok' },
  pendiente: { etiqueta: 'Verificación pendiente', icono: 'reloj', tono: 'pendiente' },
  suspendida: { etiqueta: 'Cuenta suspendida', icono: 'alerta', tono: 'alerta' },
};

const OPCIONES = {
  buscador: [
    {
      titulo: 'Buscar alojamiento',
      descripcion: 'Explora habitaciones, departamentos y casas disponibles cerca de ti.',
      ruta: '/',
      icono: 'buscar',
    },
    {
      titulo: 'Compartir vivienda',
      descripcion: 'Encuentra personas compatibles y conversa directamente por WhatsApp.',
      ruta: '/companeros',
      icono: 'personas',
    },
    {
      titulo: 'Verificar identidad',
      descripcion: 'Acredita quién eres y genera confianza en la comunidad.',
      ruta: '/verificacion',
      icono: 'escudo',
    },
  ],
  arrendador: [
    {
      titulo: 'Mis alojamientos',
      descripcion: 'Publica, edita y controla la disponibilidad de tus espacios.',
      ruta: '/mis-alojamientos',
      icono: 'casa',
    },
    {
      titulo: 'Explorar catálogo',
      descripcion: 'Compara precios y características de otras publicaciones.',
      ruta: '/',
      icono: 'catalogo',
    },
    {
      titulo: 'Verificar identidad',
      descripcion: 'Obtén la insignia de cuenta verificada para tus publicaciones.',
      ruta: '/verificacion',
      icono: 'escudo',
    },
  ],
  administrador: [
    {
      titulo: 'Administrar plataforma',
      descripcion: 'Revisa cuentas y decide sobre las solicitudes de identidad.',
      ruta: '/administracion',
      icono: 'ajustes',
    },
    {
      titulo: 'Explorar catálogo',
      descripcion: 'Consulta las publicaciones activas desde la vista pública.',
      ruta: '/',
      icono: 'catalogo',
    },
  ],
};

function iniciales(nombre = '') {
  return nombre
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte.charAt(0))
    .join('')
    .toUpperCase();
}

export default function Panel({ usuario, alActualizar }) {
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [subiendo, setSubiendo] = useState(false);
  const [version, setVersion] = useState(0);
  const entrada = useRef(null);
  const temporizador = useRef(null);

  useEffect(() => () => clearTimeout(temporizador.current), []);

  const rol = ROLES[usuario.rol] || { etiqueta: usuario.rol, icono: 'usuario' };
  const estado = ESTADOS[usuario.estado_cuenta] || {
    etiqueta: usuario.estado_cuenta,
    icono: 'reloj',
    tono: 'pendiente',
  };
  const opciones = OPCIONES[usuario.rol] || [];
  const foto = usuario.foto_url ? `${usuario.foto_url}?v=${version}` : null;

  function avisar(mensaje) {
    setAviso(mensaje);
    clearTimeout(temporizador.current);
    temporizador.current = setTimeout(() => setAviso(''), 4200);
  }

  async function subirFoto(evento) {
    const archivo = evento.target.files?.[0];
    evento.target.value = '';
    if (!archivo) return;

    setError('');
    setAviso('');
    if (!PERMITIDOS.includes(archivo.type)) {
      return setError('Elige una imagen JPG, PNG o WebP.');
    }
    if (archivo.size > TAMANO_MAXIMO) {
      return setError('La imagen supera los 5 MB. Elige una más liviana.');
    }

    setSubiendo(true);
    try {
      const actualizado = await subir('/usuarios/me/foto', archivo);
      alActualizar(actualizado);
      setVersion((valor) => valor + 1);
      avisar('Foto de perfil actualizada.');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubiendo(false);
    }
  }

  async function quitarFoto() {
    setError('');
    setAviso('');
    setSubiendo(true);
    try {
      const actualizado = await del('/usuarios/me/foto');
      alActualizar(actualizado);
      setVersion((valor) => valor + 1);
      avisar('Foto de perfil eliminada.');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubiendo(false);
    }
  }

  return <main className="contenedor seccion panelPersonal">
    <section className="perfilCabecera" aria-labelledby="titulo-panel">
      <div className="perfilAvatar">
        <span className="perfilAvatarMarco">
          {foto
            ? <img src={foto} alt={`Foto de perfil de ${usuario.nombre_completo}`} />
            : <span className="perfilIniciales" aria-hidden="true">{iniciales(usuario.nombre_completo)}</span>}
        </span>
        <button
          type="button"
          className="perfilAvatarBoton"
          aria-label={foto ? 'Cambiar foto de perfil' : 'Subir foto de perfil'}
          title={foto ? 'Cambiar foto' : 'Subir foto'}
          onClick={() => entrada.current?.click()}
          disabled={subiendo}
        >
          <IconoPanel nombre="camara" tamano={18} />
        </button>
        <input
          ref={entrada}
          className="entradaFoto"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          aria-label="Elegir foto de perfil"
          onChange={subirFoto}
          disabled={subiendo}
        />
      </div>

      <div className="perfilDatos">
        <p className="etiqueta">MI PANEL</p>
        <h1 id="titulo-panel">Hola, {usuario.nombre_completo}</h1>
        <p className="perfilCorreo">{usuario.correo}</p>

        <div className="perfilInsignias">
          <span className="insigniaPerfil rol">
            <IconoPanel nombre={rol.icono} tamano={16} />
            {rol.etiqueta}
          </span>
          <span className={`insigniaPerfil ${estado.tono}`}>
            <IconoPanel nombre={estado.icono} tamano={16} />
            {estado.etiqueta}
          </span>
        </div>

        <div className="perfilFotoAcciones">
          <button
            type="button"
            className="btn secundario"
            onClick={() => entrada.current?.click()}
            disabled={subiendo}
          >
            {subiendo ? 'Guardando…' : foto ? 'Cambiar foto' : 'Subir foto'}
          </button>
          {foto && <button
            type="button"
            className="btn texto eliminarFoto"
            onClick={quitarFoto}
            disabled={subiendo}
          >
            <IconoPanel nombre="basura" tamano={16} />
            Quitar
          </button>}
          <span className="textoPequeno">JPG, PNG o WebP, hasta 5 MB.</span>
        </div>

        {error && <Mensaje error={error} />}
        {aviso && <Mensaje correcto={aviso} />}
      </div>
    </section>

    <section aria-labelledby="titulo-opciones">
      <div className="seccionTitulo opcionesTitulo">
        <div>
          <p className="etiqueta">ACCESOS RÁPIDOS</p>
          <h2 id="titulo-opciones">¿Qué quieres hacer hoy?</h2>
        </div>
      </div>
      <div className="rejilla opcionesPanel">
        {opciones.map((opcion) => <Link className="opcionPanel" to={opcion.ruta} key={opcion.ruta}>
          <span className="opcionPanelIcono"><IconoPanel nombre={opcion.icono} tamano={26} /></span>
          <h3>{opcion.titulo}</h3>
          <p>{opcion.descripcion}</p>
          <span className="opcionPanelEnlace" aria-hidden="true">Abrir sección <span>→</span></span>
        </Link>)}
      </div>
    </section>
  </main>;
}
