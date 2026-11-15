import React from 'react';
import { Link } from 'react-router-dom';
import IconoMarca from '../comunes/IconoMarca.jsx';
import IconoPanel from '../comunes/IconosPanel.jsx';

const BENEFICIOS = [
  {
    icono: 'escudo',
    titulo: 'Contacto protegido',
    texto: 'Tus datos solo se comparten cuando decides escribir.',
  },
  {
    icono: 'casa',
    titulo: 'Alojamientos reales',
    texto: 'Fotos, precios y distrito antes de contactar.',
  },
  {
    icono: 'personas',
    titulo: 'Mejor convivencia',
    texto: 'Encuentra personas compatibles por hábitos y presupuesto.',
  },
];

export default function MarcoAutenticacion({ children, variante = 'ingresar' }) {
  const esRegistro = variante === 'registro';

  return <main className="paginaAuth">
    <div className="contenedor">
      <section className="marcoAutenticacion">
        <aside className="ladoMarcaAuth">
          <span className="brilloAuth" aria-hidden="true" />
          <Link className="marcaAuth" to="/" aria-label="AlojaRed, volver al inicio">
            <IconoMarca />
            <span className="marcaTexto">Aloja<span>Red</span></span>
          </Link>

          <div className="textoMarcaAuth">
            <h2>{esRegistro
              ? 'Tu próximo hogar empieza aquí.'
              : 'Tu espacio te está esperando.'}</h2>
            <p>{esRegistro
              ? 'Crea tu cuenta y conecta con arrendadores y compañeros de forma segura.'
              : 'Ingresa para revisar tus contactos, tu perfil y las publicaciones que te interesan.'}</p>
          </div>

          <ul className="beneficiosAuth">
            {BENEFICIOS.map(({ icono, titulo, texto }) => <li key={titulo}>
              <span className="iconoBeneficio"><IconoPanel nombre={icono} tamano={19} /></span>
              <div>
                <strong>{titulo}</strong>
                <span>{texto}</span>
              </div>
            </li>)}
          </ul>

          <p className="selloAuth">
            <IconoPanel nombre="escudo" tamano={16} />
            Identidad verificada y datos protegidos
          </p>

          <span className="ilustracionAuth" aria-hidden="true">
            <IconoPanel nombre="casa" tamano={240} />
          </span>
        </aside>

        <div className="ladoFormularioAuth">
          {children}
        </div>
      </section>
    </div>
  </main>;
}
