"""Dobles en memoria de los puertos de persistencia.

Permiten probar los servicios sin PostgreSQL ni SQLAlchemy.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from dominio.consultas import CoincidenciaCompanero
from modelos.alojamiento import Alojamiento, Comodidad, ImagenAlojamiento
from modelos.perfil_companero import PerfilCompanero
from modelos.registro_acceso import RegistroAcceso
from modelos.usuario import Usuario
from modelos.verificacion_identidad import VerificacionIdentidad


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
    ) -> list[Alojamiento]:
        items = [a for a in self.items.values() if a.estado == "activo"]
        if distrito:
            items = [a for a in items if distrito.lower() in a.distrito.lower()]
        if tipo:
            items = [a for a in items if tipo.lower() in a.tipo.lower()]
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


class RepositorioCompanerosFalso:
    def __init__(self) -> None:
        self.perfiles: dict[int, PerfilCompanero] = {}
        self.contactos: dict[int, tuple[str, str | None]] = {}
        self.fotos: dict[int, bool] = {}
        self._siguiente_id = 1

    def por_buscador(self, uid: int) -> PerfilCompanero | None:
        return self.perfiles.get(uid)

    def coincidencias(
        self, uid: int, perfil: PerfilCompanero
    ) -> list[CoincidenciaCompanero]:
        resultado = []
        for buscador_id, otro in self.perfiles.items():
            if (
                buscador_id == uid
                or otro.estado != "activo"
                or otro.presupuesto_min > perfil.presupuesto_max
                or otro.presupuesto_max < perfil.presupuesto_min
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
                )
            )
        return resultado

    def agregar(self, perfil: PerfilCompanero) -> None:
        perfil.perfil_id = self._siguiente_id
        self._siguiente_id += 1
        self.perfiles[perfil.buscador_id] = perfil


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
