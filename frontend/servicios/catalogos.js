import { useEffect, useState } from 'react';
import { get } from './api.js';

export const CATALOGOS_VACIOS = {
  tipos: [],
  departamentos: [],
};

/**
 * Carga los catálogos públicos de alojamiento (tipos y árbol UBIGEO).
 * Si la petición falla, la interfaz sigue funcionando con los valores
 * heredados que ya mostraba antes.
 */
export function useCatalogosAlojamiento() {
  const [catalogos, setCatalogos] = useState(CATALOGOS_VACIOS);

  useEffect(() => {
    let vigente = true;
    get('/catalogos/alojamientos')
      .then((datos) => {
        if (!vigente) return;
        setCatalogos({
          tipos: datos?.tipos || [],
          departamentos: datos?.departamentos || [],
        });
      })
      .catch(() => { /* Los formularios mantienen la selección manual. */ });
    return () => { vigente = false; };
  }, []);

  return catalogos;
}

/** Busca un distrito dentro del árbol UBIGEO y devuelve su contexto. */
export function buscarDistrito(departamentos, distritoId) {
  const id = Number(distritoId);
  if (!id) return null;
  for (const departamento of departamentos || []) {
    for (const provincia of departamento.provincias || []) {
      for (const distrito of provincia.distritos || []) {
        if (distrito.distrito_id === id) {
          return { departamento, provincia, distrito };
        }
      }
    }
  }
  return null;
}

/** Texto legible para mostrar una ubicación guardada. */
export function nombreDistrito(departamentos, distritoId) {
  const hallado = buscarDistrito(departamentos, distritoId);
  if (!hallado) return '';
  return `${hallado.distrito.nombre}, ${hallado.provincia.nombre}, ${hallado.departamento.nombre}`;
}
