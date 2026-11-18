import React, { useMemo } from 'react';
import { buscarDistrito } from '../../servicios/catalogos.js';

/**
 * Selector en cascada de departamento, provincia y distrito.
 *
 * Está controlado por el formulario padre. Cuando solo llega `distritoId`,
 * deduce el departamento y la provincia para mostrar la selección completa.
 * `onCambio` recibe siempre los tres valores; el consumidor decide cuáles
 * envía a la API.
 */
export default function SelectorUbigeo({
  departamentos = [],
  departamentoId = '',
  provinciaId = '',
  distritoId = '',
  onCambio,
  requerido = false,
  etiqueta = 'Ubicación',
  variante = 'formulario',
}) {
  const hallado = useMemo(
    () => buscarDistrito(departamentos, distritoId),
    [departamentos, distritoId],
  );

  const dep = String(departamentoId || hallado?.departamento.departamento_id || '');
  const prov = String(provinciaId || hallado?.provincia.provincia_id || '');

  const departamento = useMemo(
    () => departamentos.find((d) => String(d.departamento_id) === dep),
    [departamentos, dep],
  );
  const provincia = useMemo(
    () => (departamento?.provincias || []).find((p) => String(p.provincia_id) === prov),
    [departamento, prov],
  );

  function notificar(cambios) {
    onCambio?.({
      departamentoId: dep,
      provinciaId: prov,
      distritoId: distritoId === '' ? '' : String(distritoId),
      ...cambios,
    });
  }

  const buscador = variante === 'buscador';
  const campo = buscador ? 'campoBuscador' : '';
  const Titulo = ({ children }) => (buscador ? <span>{children}</span> : children);

  return <div className={`selectorUbigeo ${buscador ? 'selectorUbigeoBuscador' : ''}`.trim()}>
    <label className={campo}>
      <Titulo>Departamento</Titulo>
      <select
        aria-label={buscador ? 'Departamento' : undefined}
        value={dep}
        required={requerido}
        onChange={(e) => notificar({
          departamentoId: e.target.value,
          provinciaId: '',
          distritoId: '',
        })}
      >
        <option value="">{etiqueta === 'Ubicación' ? 'Todos' : 'Selecciona'}</option>
        {departamentos.map((d) => (
          <option key={d.departamento_id} value={d.departamento_id}>{d.nombre}</option>
        ))}
      </select>
    </label>

    <label className={campo}>
      <Titulo>Provincia</Titulo>
      <select
        aria-label={buscador ? 'Provincia' : undefined}
        value={prov}
        disabled={!departamento}
        required={requerido && Boolean(departamento)}
        onChange={(e) => notificar({
          provinciaId: e.target.value,
          distritoId: '',
        })}
      >
        <option value="">{etiqueta === 'Ubicación' ? 'Todas' : 'Selecciona'}</option>
        {(departamento?.provincias || []).map((p) => (
          <option key={p.provincia_id} value={p.provincia_id}>{p.nombre}</option>
        ))}
      </select>
    </label>

    <label className={campo}>
      <Titulo>Distrito</Titulo>
      <select
        aria-label={buscador ? 'Distrito UBIGEO' : undefined}
        value={String(distritoId || '')}
        disabled={!provincia}
        required={requerido}
        onChange={(e) => notificar({ distritoId: e.target.value })}
      >
        <option value="">{etiqueta === 'Ubicación' ? 'Todos' : 'Selecciona'}</option>
        {(provincia?.distritos || []).map((d) => (
          <option key={d.distrito_id} value={d.distrito_id}>{d.nombre}</option>
        ))}
      </select>
    </label>
  </div>;
}
