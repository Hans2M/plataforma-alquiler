"""Composición de dependencias de la capa API.

Aquí (y solo aquí) se unen puertos, implementaciones concretas y servicios.
Los routers piden servicios; los tests pueden sustituirlos con
app.dependency_overrides.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from configuracion.base_datos import obtener_db
from dominio.puertos import (
    RepositorioAccesos,
    RepositorioAlojamientos,
    RepositorioCompaneros,
    RepositorioUsuarios,
    RepositorioVerificaciones,
)
from repositorios.alojamientos import RepositorioAlojamientosSQLAlchemy
from repositorios.companeros import RepositorioCompanerosSQLAlchemy
from repositorios.registros_acceso import RepositorioAccesosSQLAlchemy
from repositorios.usuarios import RepositorioUsuariosSQLAlchemy
from repositorios.verificaciones import RepositorioVerificacionesSQLAlchemy
from servicios.administracion import ServicioAdministracion
from servicios.alojamientos import ServicioAlojamientos
from servicios.autenticacion import ServicioAutenticacion
from servicios.companeros import ServicioCompaneros
from servicios.usuarios import ServicioUsuarios
from servicios.verificaciones import ServicioVerificaciones


def repositorio_usuarios(db: Session = Depends(obtener_db, scope="function")) -> RepositorioUsuarios:
    return RepositorioUsuariosSQLAlchemy(db)


def repositorio_accesos(db: Session = Depends(obtener_db, scope="function")) -> RepositorioAccesos:
    return RepositorioAccesosSQLAlchemy(db)


def repositorio_alojamientos(
    db: Session = Depends(obtener_db, scope="function"),
) -> RepositorioAlojamientos:
    return RepositorioAlojamientosSQLAlchemy(db)


def repositorio_companeros(
    db: Session = Depends(obtener_db, scope="function"),
) -> RepositorioCompaneros:
    return RepositorioCompanerosSQLAlchemy(db)


def repositorio_verificaciones(
    db: Session = Depends(obtener_db, scope="function"),
) -> RepositorioVerificaciones:
    return RepositorioVerificacionesSQLAlchemy(db)


def servicio_autenticacion(
    usuarios: RepositorioUsuarios = Depends(repositorio_usuarios),
    accesos: RepositorioAccesos = Depends(repositorio_accesos),
) -> ServicioAutenticacion:
    return ServicioAutenticacion(usuarios, accesos)


def servicio_alojamientos(
    alojamientos: RepositorioAlojamientos = Depends(repositorio_alojamientos),
) -> ServicioAlojamientos:
    return ServicioAlojamientos(alojamientos)


def servicio_companeros(
    companeros: RepositorioCompaneros = Depends(repositorio_companeros),
) -> ServicioCompaneros:
    return ServicioCompaneros(companeros)


def servicio_usuarios(
    accesos: RepositorioAccesos = Depends(repositorio_accesos),
    usuarios: RepositorioUsuarios = Depends(repositorio_usuarios),
) -> ServicioUsuarios:
    return ServicioUsuarios(accesos, usuarios)


def servicio_verificaciones(
    verificaciones: RepositorioVerificaciones = Depends(repositorio_verificaciones),
    usuarios: RepositorioUsuarios = Depends(repositorio_usuarios),
) -> ServicioVerificaciones:
    return ServicioVerificaciones(verificaciones, usuarios)


def servicio_administracion(
    usuarios: RepositorioUsuarios = Depends(repositorio_usuarios),
) -> ServicioAdministracion:
    return ServicioAdministracion(usuarios)
