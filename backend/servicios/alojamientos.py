from dominio.consultas import ContactoArrendador
from dominio.errores import NoEncontrado, Prohibido, ValidacionInvalida
from dominio.puertos import RepositorioAlojamientos
from esquemas.datos import AlojamientoEditar, AlojamientoEntrada
from modelos.alojamiento import Alojamiento, Comodidad, ImagenAlojamiento


class ServicioAlojamientos:
    """Casos de uso de publicaciones de alojamiento."""

    def __init__(self, alojamientos: RepositorioAlojamientos) -> None:
        self.alojamientos = alojamientos

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
        if (
            precio_min is not None
            and precio_max is not None
            and precio_min > precio_max
        ):
            raise ValidacionInvalida(
                "El precio mínimo no puede superar al precio máximo"
            )
        return self.alojamientos.buscar(
            distrito,
            tipo,
            precio_max,
            texto,
            pagina,
            limite,
            precio_min,
            dias,
            orden,
            distrito_id,
            provincia_id,
            departamento_id,
        )

    def de_arrendador(self, uid: int) -> list[Alojamiento]:
        return self.alojamientos.de_arrendador(uid)

    def comodidades(self) -> list[Comodidad]:
        return self.alojamientos.comodidades()

    def detalle(self, alojamiento_id: int) -> Alojamiento:
        obj = self.alojamientos.por_id(alojamiento_id)
        if obj is None or obj.estado != "activo":
            raise NoEncontrado("Alojamiento no disponible")
        return obj

    def imagenes(self, alojamiento_id: int) -> list[ImagenAlojamiento]:
        obj = self.alojamientos.por_id(alojamiento_id)
        if obj is None or obj.estado != "activo":
            raise NoEncontrado("Publicación no disponible")
        return self.alojamientos.imagenes_de(alojamiento_id)

    def ruta_imagen(self, imagen_id: int) -> str:
        imagen = self.alojamientos.imagen_por_id(imagen_id)
        if imagen is None:
            raise NoEncontrado("Imagen no encontrada")
        obj = self.alojamientos.por_id(imagen.alojamiento_id)
        if obj is None or obj.estado != "activo":
            raise NoEncontrado("Imagen no publicada")
        return imagen.ruta_archivo

    def contacto(self, alojamiento_id: int) -> ContactoArrendador:
        """Datos de contacto del propietario de una publicación activa.

        Solo se exponen a usuarios autenticados (la capa API exige sesión).
        """
        obj = self.alojamientos.por_id(alojamiento_id)
        if obj is None or obj.estado != "activo":
            raise NoEncontrado("Alojamiento no disponible")
        propietario = self.alojamientos.propietario_de(alojamiento_id)
        if propietario is None:
            raise NoEncontrado("Arrendador no encontrado")
        return ContactoArrendador(
            arrendador_id=propietario.usuario_id,
            nombre_completo=propietario.nombre_completo,
            telefono=propietario.telefono,
            correo=propietario.correo,
        )

    def crear(self, uid: int, datos: AlojamientoEntrada) -> Alojamiento:
        if not self.alojamientos.comodidades_validas(datos.comodidad_ids):
            raise ValidacionInvalida("Una comodidad no existe")
        valores = datos.model_dump(exclude={"comodidad_ids"})
        self._normalizar_ubicacion(valores, parcial=False)
        nuevo = Alojamiento(
            arrendador_id=uid,
            destacado=False,
            **valores,
        )
        self.alojamientos.agregar(nuevo)
        self.alojamientos.asignar_comodidades(
            nuevo.alojamiento_id, datos.comodidad_ids
        )
        return nuevo

    def _normalizar_ubicacion(self, valores: dict, parcial: bool) -> None:
        """Traduce UBIGEO/tipo a ids y mantiene el texto histórico.

        En creación exige ubicación y tipo (por id o por texto). En edición
        parcial solo valida los campos presentes.
        """
        distrito_id = valores.get("distrito_id")
        tipo_id = valores.get("tipo_id")

        if distrito_id is not None:
            distrito = self.alojamientos.distrito(distrito_id)
            if distrito is None:
                raise ValidacionInvalida("El distrito indicado no existe")
            valores["distrito"] = distrito.nombre
        elif not parcial and not valores.get("distrito"):
            raise ValidacionInvalida("Indica el distrito del alojamiento")

        if tipo_id is not None:
            tipo = self.alojamientos.tipo(tipo_id)
            if tipo is None or not tipo.activo:
                raise ValidacionInvalida(
                    "El tipo de alojamiento no existe o está inactivo"
                )
            valores["tipo"] = tipo.codigo
        elif not parcial and not valores.get("tipo"):
            raise ValidacionInvalida("Indica el tipo de alojamiento")

    def modificar(
        self, uid: int, alojamiento_id: int, datos: AlojamientoEditar
    ) -> Alojamiento:
        obj = self.alojamientos.por_id(alojamiento_id)
        if obj is None:
            raise NoEncontrado("Publicación no encontrada")
        if obj.arrendador_id != uid:
            raise Prohibido("Solo el propietario puede modificar esta publicación")

        cambios = datos.model_dump(exclude_unset=True)
        ids = cambios.pop("comodidad_ids", None)
        if ids is not None and not self.alojamientos.comodidades_validas(ids):
            raise ValidacionInvalida("Una comodidad no existe")
        self._normalizar_ubicacion(cambios, parcial=True)
        for clave, valor in cambios.items():
            setattr(obj, clave, valor)
        if ids is not None:
            self.alojamientos.asignar_comodidades(obj.alojamiento_id, ids)
        return obj

    def desactivar(self, uid: int, alojamiento_id: int) -> Alojamiento:
        obj = self.alojamientos.por_id(alojamiento_id)
        if obj is None:
            raise NoEncontrado("Publicación no encontrada")
        if obj.arrendador_id != uid:
            raise Prohibido("No eres el propietario")
        obj.estado = "inactivo"
        return obj

    def registrar_imagen(
        self, uid: int, alojamiento_id: int, ruta: str
    ) -> ImagenAlojamiento:
        obj = self.alojamientos.por_id(alojamiento_id)
        if obj is None or obj.arrendador_id != uid:
            raise NoEncontrado("Publicación propia no encontrada")
        imagen = ImagenAlojamiento(
            alojamiento_id=alojamiento_id,
            ruta_archivo=ruta,
            orden=0,
        )
        self.alojamientos.agregar_imagen(imagen)
        return imagen
