from fastapi import APIRouter, Depends, Query

from api.dependencias import servicio_catalogos
from esquemas.datos import (
    CatalogosAlojamientoSalida,
    EstadoCatalogoSalida,
)
from servicios.catalogos import ServicioCatalogos

router = APIRouter(prefix='/api/catalogos', tags=['Catálogos'])


@router.get('/alojamientos', response_model=CatalogosAlojamientoSalida)
def catalogos_alojamientos(
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    """Tipos de alojamiento activos y árbol UBIGEO para formularios y filtros."""
    return {
        'tipos': servicio.tipos(),
        'departamentos': servicio.ubigeo(),
    }


@router.get('/estados', response_model=list[EstadoCatalogoSalida])
def estados(
    dominio: str | None = Query(None, max_length=30),
    servicio: ServicioCatalogos = Depends(servicio_catalogos),
):
    return servicio.estados(dominio)
