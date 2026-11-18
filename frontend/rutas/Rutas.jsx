import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import Inicio from '../paginas/buscador/Inicio.jsx';
import DetalleAlojamiento from '../paginas/buscador/DetalleAlojamiento.jsx';
import Login from '../paginas/autenticacion/Login.jsx';
import Registro from '../paginas/autenticacion/Registro.jsx';
import Panel from '../paginas/buscador/Panel.jsx';
import Companeros from '../paginas/buscador/Companeros.jsx';
import Verificacion from '../paginas/buscador/Verificacion.jsx';
import MisAlojamientos from '../paginas/arrendador/MisAlojamientos.jsx';
import Administracion from '../paginas/administrador/Administracion.jsx';
import Catalogos from '../paginas/administrador/Catalogos.jsx';

function Proteger({usuario,roles,children}) {
  if (!usuario) return <Navigate to="/ingresar" replace/>;
  if (roles && !roles.includes(usuario.rol)) return <Navigate to="/panel" replace/>;
  return children;
}
export default function Rutas({usuario,alIngresar}){
 return <Routes>
  <Route path="/" element={<Inicio usuario={usuario}/>}/>
  <Route path="/alojamientos/:id" element={<DetalleAlojamiento usuario={usuario}/>}/>
  <Route path="/ingresar" element={usuario?<Navigate to="/panel"/>:<Login alIngresar={alIngresar}/>}/>
  <Route path="/registro" element={<Registro/>}/>
  <Route path="/panel" element={<Proteger usuario={usuario}><Panel usuario={usuario} alActualizar={alIngresar}/></Proteger>}/>
  <Route path="/mis-alojamientos" element={<Proteger usuario={usuario} roles={['arrendador']}><MisAlojamientos/></Proteger>}/>
  <Route path="/companeros" element={<Proteger usuario={usuario} roles={['buscador']}><Companeros/></Proteger>}/>
  <Route path="/verificacion" element={<Proteger usuario={usuario}><Verificacion/></Proteger>}/>
  <Route path="/administracion" element={<Proteger usuario={usuario} roles={['administrador']}><Administracion/></Proteger>}/>
  <Route path="/administracion/catalogos" element={<Proteger usuario={usuario} roles={['administrador']}><Catalogos/></Proteger>}/>
  <Route path="*" element={<Navigate to="/"/>}/>
 </Routes>
}
