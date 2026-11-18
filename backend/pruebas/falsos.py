"""Dobles en memoria de los puertos de persistencia.

Permiten probar los servicios sin PostgreSQL ni SQLAlchemy.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from dominio.compatibilidad import calcular_compatibilidad
from dominio.consultas import CoincidenciaCompanero
from modelos.alojamiento import Alojamiento, Comodidad, ImagenAlojamiento
from modelos.catalogos import CatalogoEstado, TipoAlojamiento
from modelos.perfil_companero import (
    CatalogoHabito,
    CatalogoPreferencia,
    PerfilCompanero,
)
from modelos.registro_acceso import RegistroAcceso
from modelos.ubigeo import Departamento, Distrito, Provincia
from modelos.usuario import Usuario
from modelos.verificacion_identidad import VerificacionIdentidad

# UBIGEO mínimo compartido por los dobles en memoria.
DISTRITOS_FALSOS = {
    1: Distrito(
        distrito_id=1, provincia_id=1, codigo="100601", nombre="Rupa-Rupa"
    ),
    2: Distrito(
        distrito_id=2, provincia_id=1, codigo="100101", nombre="Huánuco"
    ),
    3: Distrito(
        distrito_id=3, provincia_id=2, codigo="150101", nombre="Lima"
    ),
}

TIPOS_FALSOS = {
    1: TipoAlojamiento(
        tipo_id=1,
        codigo="habitacion",
        nombre="Habitación",
        descripcion="Cuarto",
        orden=10,
        activo=True,
    ),
    2: TipoAlojamiento(
        tipo_id=2,
        codigo="departamento",
        nombre="Departamento",
        descripcion="Departamento independiente",
        orden=20,
        activo=True,
    ),
    3: TipoAlojamiento(
        tipo_id=3,
        codigo="casa",
        nombre="Casa",
        descripcion="Vivienda completa",
        orden=30,
        activo=False,
    ),
}


class RepositorioUsuariosFalso:
    def __init__(self) -> None:
        self.usuarios: dict[int, Usuario] = {}
        self.buscadores: set[int] = set()
        self.arrendadores: dict[int, str | None] = {}
        self._siguiente_id = 1

    def por_correo(self, correo: str) -> Usuario | None:
        correo = correo.strip().lower()
        for usuario in self.usuarios.values():
            if usuario.correo == correo:
                return usuario
        return None

    def por_documento(self, documento: str) -> Usuario | None:
        for usuario in self.usuarios.values():
            if usuario.numero_documento == documento:
                return usuario
        return None

    def por_id(self, uid: int) -> Usuario | None:
        return self.usuarios.get(uid)

    def agregar(self, usuario: Usuario) -> None:
        if usuario.usuario_id is None:
            usuario.usuario_id = self._siguiente_id
            self._siguiente_id += 1
        self.usuarios[usuario.usuario_id] = usuario

    def agregar_buscador(self, uid: int) -> None:
        self.buscadores.add(uid)

    def agregar_arrendador(self, uid: int, ruc: str | None) -> None:
        self.arrendadores[uid] = ruc

    def listar(self, limite: int = 100) -> list[Usuario]:
        return list(self.usuarios.values())[:limite]


class RepositorioAccesosFalso:
    def __init__(self) -> None:
        self.registros: list[RegistroAcceso] = []

    def registrar(
        self,
        usuario_id: int,
        accion: str,
        ip: str | None = None,
        dispositivo: str | None = None,
    ) -> None:
        self.registros.append(
            RegistroAcceso(
                usuario_id=usuario_id,
                accion=accion,
                ip=ip,
                dispositivo=dispositivo,
            )
        )

    def de_usuario(self, uid: int) -> list[RegistroAcceso]:
        return [r for r in self.registros if r.usuario_id == uid]


class RepositorioAlojamientosFalso:
    def __init__(self) -> None:
        self.items: dict[int, Alojamiento] = {}
        self.imagenes: dict[int, ImagenAlojamiento] = {}
        self.comodidades_asignadas: dict[int, set[int]] = {}
        self.usuarios: dict[int, Usuario] = {}
        self.comodidades_catalogo = [
            Comodidad(comodidad_id=1, nombre="wifi"),
            Comodidad(comodidad_id=2, nombre="agua"),
        ]
        self.distritos = DISTRITOS_FALSOS
        self.tipos = TIPOS_FALSOS
        self._siguiente_id = 1
        self._siguiente_imagen_id = 1

    def buscar(
        self,
        distrito: str | None,
        tipo: str | None,
        precio_max: float | None,
        texto: str | None,
        pagina: int,
        limite: int,
        precio_min: float | None = None,
        dias: int | None = None,
        orden: str = "recientes",
        distrito_id: int | None = None,
        provincia_id: int | None = None,
        departamento_id: int | None = None,
    ) -> list[Alojamiento]:
        items = [a for a in self.items.values() if a.estado == "activo"]
        if distrito:
            items = [a for a in items if distrito.lower() in a.distrito.lower()]
        if tipo:
            items = [a for a in items if tipo.lower() in a.tipo.lower()]
        if distrito_id is not None:
            items = [a for a in items if a.distrito_id == distrito_id]
        if provincia_id is not None:
            items = [
                a for a in items
                if a.distrito_id in self.distritos
                and self.distritos[a.distrito_id].provincia_id == provincia_id
            ]
        if departamento_id is not None:
            # En los dobles: provincia 1 -> Huánuco (1), provincia 2 -> Lima (2).
            provincias = {
                provincia_id: departamento
                for provincia_id, departamento in ((1, 1), (2, 2))
            }
            items = [
                a for a in items
                if a.distrito_id in self.distritos
                and provincias.get(self.distritos[a.distrito_id].provincia_id)
                == departamento_id
            ]
        if precio_min is not None:
            items = [a for a in items if a.precio >= Decimal(str(precio_min))]
        if precio_max is not None:
            items = [a for a in items if a.precio <= Decimal(str(precio_max))]
        if texto:
            items = [a for a in items if texto.lower() in a.titulo.lower()]
        if dias is not None:
            desde = datetime.now(timezone.utc) - timedelta(days=dias)
            items = [
                a for a in items
                if a.fecha_publicacion is not None
                and a.fecha_publicacion >= desde
            ]
        if orden == "precio_asc":
            items.sort(key=lambda a: a.precio)
        elif orden == "precio_desc":
            items.sort(key=lambda a: a.precio, reverse=True)
        else:
            items.sort(
                key=lambda a: a.fecha_publicacion
                or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
            items.sort(key=lambda a: bool(a.destacado), reverse=True)
        inicio = (pagina - 1) * limite
        return items[inicio : inicio + limite]

    def de_arrendador(self, uid: int) -> list[Alojamiento]:
        return [a for a in self.items.values() if a.arrendador_id == uid]

    def por_id(self, alojamiento_id: int) -> Alojamiento | None:
        return self.items.get(alojamiento_id)

    def agregar(self, alojamiento: Alojamiento) -> None:
        alojamiento.alojamiento_id = self._siguiente_id
        self._siguiente_id += 1
        self.items[alojamiento.alojamiento_id] = alojamiento

    def comodidades(self) -> list[Comodidad]:
        return list(self.comodidades_catalogo)

    def comodidades_validas(self, ids: list[int]) -> bool:
        validas = {c.comodidad_id for c in self.comodidades_catalogo}
        return set(ids) <= validas

    def asignar_comodidades(self, alojamiento_id: int, ids: list[int]) -> None:
        self.comodidades_asignadas[alojamiento_id] = set(ids)

    def imagenes_de(self, alojamiento_id: int) -> list[ImagenAlojamiento]:
        return [i for i in self.imagenes.values() if i.alojamiento_id == alojamiento_id]

    def imagen_por_id(self, imagen_id: int) -> ImagenAlojamiento | None:
        return self.imagenes.get(imagen_id)

    def agregar_imagen(self, imagen: ImagenAlojamiento) -> None:
        imagen.imagen_id = self._siguiente_imagen_id
        self._siguiente_imagen_id += 1
        self.imagenes[imagen.imagen_id] = imagen

    def propietario_de(self, alojamiento_id: int) -> Usuario | None:
        alojamiento = self.items.get(alojamiento_id)
        if alojamiento is None:
            return None
        return self.usuarios.get(alojamiento.arrendador_id)

    def distrito(self, distrito_id: int) -> Distrito | None:
        return self.distritos.get(distrito_id)

    def tipo(self, tipo_id: int) -> TipoAlojamiento | None:
        return self.tipos.get(tipo_id)


class RepositorioCompanerosFalso:
    def __init__(self) -> None:
        self.perfiles: dict[int, PerfilCompanero] = {}
        self.contactos: dict[int, tuple[str, str | None]] = {}
        self.fotos: dict[int, bool] = {}
        self.habitos_catalogo = [
            CatalogoHabito(
                habito_id=1, nombre="No fumo", categoria="convivencia", orden=10, activo=True
            ),
            CatalogoHabito(
                habito_id=2, nombre="Hago deporte", categoria="ocio", orden=12, activo=True
            ),
            CatalogoHabito(
                habito_id=3, nombre="Leo", categoria="ocio", orden=20, activo=True
            ),
        ]
        self.preferencias_catalogo = [
            CatalogoPreferencia(
                preferencia_id=1,
                nombre="Ambiente tranquilo",
                categoria="convivencia",
                orden=10,
                activo=True,
            ),
            CatalogoPreferencia(
                preferencia_id=2,
                nombre="Buena comunicación",
                categoria="convivencia",
                orden=20,
                activo=True,
            ),
        ]
        self._siguiente_id = 1

    def por_buscador(self, uid: int) -> PerfilCompanero | None:
        return self.perfiles.get(uid)

    def coincidencias(
        self, uid: int, perfil: PerfilCompanero, filtros: dict | None = None
    ) -> list[CoincidenciaCompanero]:
        filtros = filtros or {}
        resultado = []
        for buscador_id, otro in self.perfiles.items():
            if (
                buscador_id == uid
                or otro.estado != "activo"
                or otro.presupuesto_min > perfil.presupuesto_max
                or otro.presupuesto_max < perfil.presupuesto_min
            ):
                continue
            if filtros.get("edad_min") is not None and (
                otro.edad is None or otro.edad < filtros["edad_min"]
            ):
                continue
            if filtros.get("edad_max") is not None and (
                otro.edad is None or otro.edad > filtros["edad_max"]
            ):
                continue
            if filtros.get("genero") and otro.genero != filtros["genero"]:
                continue
            if (
                filtros.get("genero_preferido")
                and otro.genero_preferido != filtros["genero_preferido"]
            ):
                continue
            if (
                filtros.get("mismo_distrito")
                and perfil.distrito_id is not None
                and otro.distrito_id != perfil.distrito_id
            ):
                continue
            nombre, telefono = self.contactos.get(
                buscador_id, (f"Compañero {buscador_id}", None)
            )
            resultado.append(
                CoincidenciaCompanero(
                    perfil_id=otro.perfil_id,
                    buscador_id=buscador_id,
                    nombre_completo=nombre,
                    telefono=telefono,
                    presupuesto_min=otro.presupuesto_min,
                    presupuesto_max=otro.presupuesto_max,
                    habitos=otro.habitos,
                    preferencias=otro.preferencias,
                    descripcion=otro.descripcion,
                    estado=otro.estado,
                    foto_perfil=self.fotos.get(buscador_id, False),
                    habito_ids=tuple(otro.habito_ids),
                    habito_nombres=tuple(otro.habito_nombres),
                    preferencia_ids=tuple(otro.preferencia_ids),
                    preferencia_nombres=tuple(otro.preferencia_nombres),
                    fuma=otro.fuma,
                    tiene_mascotas=otro.tiene_mascotas,
                    horario=otro.horario,
                    nivel_orden=otro.nivel_orden,
                    ocupacion=otro.ocupacion,
                    genero=otro.genero,
                    genero_preferido=otro.genero_preferido,
                    edad=otro.edad,
                    distrito_id=otro.distrito_id,
                    distrito_completo=otro.distrito_completo,
                    compatibilidad=calcular_compatibilidad(
                        habito_ids_a=perfil.habito_ids,
                        habito_ids_b=otro.habito_ids,
                        preferencia_ids_a=perfil.preferencia_ids,
                        preferencia_ids_b=otro.preferencia_ids,
                        fuma_a=perfil.fuma,
                        fuma_b=otro.fuma,
                        tiene_mascotas_a=perfil.tiene_mascotas,
                        tiene_mascotas_b=otro.tiene_mascotas,
                        horario_a=perfil.horario,
                        horario_b=otro.horario,
                        nivel_orden_a=perfil.nivel_orden,
                        nivel_orden_b=otro.nivel_orden,
                        ocupacion_a=perfil.ocupacion,
                        ocupacion_b=otro.ocupacion,
                    ),
                )
            )
        resultado.sort(key=lambda c: (-c.compatibilidad, c.perfil_id))
        return resultado

    def agregar(self, perfil: PerfilCompanero) -> None:
        perfil.perfil_id = self._siguiente_id
        self._siguiente_id += 1
        self.perfiles[perfil.buscador_id] = perfil

    def catalogos(self):
        return self.habitos_catalogo, self.preferencias_catalogo

    def habitos_validos(self, ids: list[int]) -> bool:
        disponibles = {h.habito_id for h in self.habitos_catalogo if h.activo}
        return set(ids) <= disponibles

    def preferencias_validas(self, ids: list[int]) -> bool:
        disponibles = {p.preferencia_id for p in self.preferencias_catalogo if p.activo}
        return set(ids) <= disponibles

    def asignar_habitos(self, perfil: PerfilCompanero, ids: list[int]) -> None:
        perfil.habitos_catalogo = [
            habito for habito in self.habitos_catalogo if habito.habito_id in set(ids)
        ]

    def asignar_preferencias(self, perfil: PerfilCompanero, ids: list[int]) -> None:
        perfil.preferencias_catalogo = [
            preferencia
            for preferencia in self.preferencias_catalogo
            if preferencia.preferencia_id in set(ids)
        ]

    def distrito(self, distrito_id: int) -> Distrito | None:
        return DISTRITOS_FALSOS.get(distrito_id)


class RepositorioCatalogosFalso:
    def __init__(self) -> None:
        self.tipos_catalogo = {
            tipo_id: TipoAlojamiento(
                tipo_id=tipo_id,
                codigo=tipo.codigo,
                nombre=tipo.nombre,
                descripcion=tipo.descripcion,
                orden=tipo.orden,
                activo=tipo.activo,
            )
            for tipo_id, tipo in TIPOS_FALSOS.items()
        }
        self.estados_catalogo = [
            CatalogoEstado(
                dominio="cuenta",
                codigo="pendiente",
                nombre="Pendiente",
                descripcion="Sin verificar",
                orden=10,
                activo=True,
            ),
            CatalogoEstado(
                dominio="alojamiento",
                codigo="activo",
                nombre="Activo",
                descripcion="Visible",
                orden=10,
                activo=True,
            ),
        ]
        self.habitos_catalogo = [
            CatalogoHabito(
                habito_id=1, nombre="No fumo", categoria="convivencia", orden=10
            )
        ]
        self.preferencias_catalogo = [
            CatalogoPreferencia(
                preferencia_id=1,
                nombre="Ambiente tranquilo",
                categoria="convivencia",
                orden=10,
            )
        ]
        self._siguiente_tipo = 10
        self._siguiente_habito = 10
        self._siguiente_preferencia = 10

    def tipos(self, incluir_inactivos: bool = False) -> list[TipoAlojamiento]:
        return [
            t for t in self.tipos_catalogo.values() if incluir_inactivos or t.activo
        ]

    def tipo(self, tipo_id: int) -> TipoAlojamiento | None:
        return self.tipos_catalogo.get(tipo_id)

    def tipo_por_codigo(self, codigo: str) -> TipoAlojamiento | None:
        return next(
            (t for t in self.tipos_catalogo.values() if t.codigo == codigo), None
        )

    def tipo_por_nombre(self, nombre: str) -> TipoAlojamiento | None:
        return next(
            (
                t
                for t in self.tipos_catalogo.values()
                if t.nombre.lower() == nombre.strip().lower()
            ),
            None,
        )

    def agregar_tipo(self, tipo: TipoAlojamiento) -> None:
        tipo.tipo_id = self._siguiente_tipo
        self._siguiente_tipo += 1
        self.tipos_catalogo[tipo.tipo_id] = tipo

    def estados(
        self, dominio: str | None = None, incluir_inactivos: bool = False
    ) -> list[CatalogoEstado]:
        return [
            e
            for e in self.estados_catalogo
            if (dominio is None or e.dominio == dominio)
            and (incluir_inactivos or e.activo)
        ]

    def estado(self, dominio: str, codigo: str) -> CatalogoEstado | None:
        return next(
            (
                e
                for e in self.estados_catalogo
                if e.dominio == dominio and e.codigo == codigo
            ),
            None,
        )

    def habitos(self, incluir_inactivos: bool = False) -> list[CatalogoHabito]:
        return [
            h for h in self.habitos_catalogo if incluir_inactivos or h.activo
        ]

    def habito(self, habito_id: int) -> CatalogoHabito | None:
        return next(
            (h for h in self.habitos_catalogo if h.habito_id == habito_id), None
        )

    def habito_por_nombre(self, nombre: str) -> CatalogoHabito | None:
        return next(
            (
                h
                for h in self.habitos_catalogo
                if h.nombre.lower() == nombre.strip().lower()
            ),
            None,
        )

    def agregar_habito(self, habito: CatalogoHabito) -> None:
        habito.habito_id = self._siguiente_habito
        self._siguiente_habito += 1
        self.habitos_catalogo.append(habito)

    def preferencias(
        self, incluir_inactivos: bool = False
    ) -> list[CatalogoPreferencia]:
        return [
            p
            for p in self.preferencias_catalogo
            if incluir_inactivos or p.activo
        ]

    def preferencia(self, preferencia_id: int) -> CatalogoPreferencia | None:
        return next(
            (
                p
                for p in self.preferencias_catalogo
                if p.preferencia_id == preferencia_id
            ),
            None,
        )

    def preferencia_por_nombre(self, nombre: str) -> CatalogoPreferencia | None:
        return next(
            (
                p
                for p in self.preferencias_catalogo
                if p.nombre.lower() == nombre.strip().lower()
            ),
            None,
        )

    def agregar_preferencia(self, preferencia: CatalogoPreferencia) -> None:
        preferencia.preferencia_id = self._siguiente_preferencia
        self._siguiente_preferencia += 1
        self.preferencias_catalogo.append(preferencia)

    def departamentos(self) -> list[Departamento]:
        return [
            Departamento(
                departamento_id=1,
                codigo="10",
                nombre="Huánuco",
                provincias=[
                    Provincia(
                        provincia_id=1,
                        departamento_id=1,
                        codigo="1006",
                        nombre="Leoncio Prado",
                        distritos=[
                            DISTRITOS_FALSOS[1],
                            DISTRITOS_FALSOS[2],
                        ],
                    )
                ],
            ),
            Departamento(
                departamento_id=2,
                codigo="15",
                nombre="Lima",
                provincias=[
                    Provincia(
                        provincia_id=2,
                        departamento_id=2,
                        codigo="1501",
                        nombre="Lima",
                        distritos=[DISTRITOS_FALSOS[3]],
                    )
                ],
            ),
        ]

    def distrito(self, distrito_id: int) -> Distrito | None:
        return DISTRITOS_FALSOS.get(distrito_id)


class RepositorioVerificacionesFalso:
    def __init__(self) -> None:
        self.items: dict[int, VerificacionIdentidad] = {}
        self._siguiente_id = 1

    def ultima_por_usuario(self, uid: int) -> VerificacionIdentidad | None:
        propias = [v for v in self.items.values() if v.usuario_id == uid]
        return propias[-1] if propias else None

    def pendientes(self) -> list[VerificacionIdentidad]:
        return [v for v in self.items.values() if v.estado == "pendiente"]

    def por_id(
        self, verificacion_id: int, bloquear: bool = False
    ) -> VerificacionIdentidad | None:
        return self.items.get(verificacion_id)

    def agregar(self, verificacion: VerificacionIdentidad) -> None:
        verificacion.verificacion_id = self._siguiente_id
        self._siguiente_id += 1
        self.items[verificacion.verificacion_id] = verificacion
