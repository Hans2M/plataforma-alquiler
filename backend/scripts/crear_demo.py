"""Carga datos de demostración para probar el contacto entre usuarios.

Crea:
- Un arrendador con tres publicaciones y fotos generadas.
- Un buscador y dos compañeros con perfiles de convivencia compatibles.
- Un perfil de convivencia para el buscador principal.

Es idempotente: si un correo o una publicación ya existe, no lo duplica.

Ejecutar dentro del backend:
    docker compose exec backend python -m scripts.crear_demo
"""

from __future__ import annotations

import struct
import zlib
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from configuracion.base_datos import SessionLocal
from configuracion.configuracion import settings
from modelos.alojamiento import Alojamiento, ImagenAlojamiento
from modelos.perfil_companero import PerfilCompanero
from modelos.usuario import Usuario
from repositorios.usuarios import RepositorioUsuariosSQLAlchemy
from seguridad.autenticacion import hash_clave

CLAVE_DEMO = "DemoSegura123"

ARRENDADOR = {
    "correo": "arrendador.demo@example.com",
    "nombre_completo": "María Quispe Huamán",
    "telefono": "987654321",
    "numero_documento": "71234567",
    "ruc": "20712345671",
    "colores": ((66, 133, 199), (18, 109, 175)),
}

BUSCADORES = [
    {
        "correo": "buscador.demo@example.com",
        "nombre_completo": "Lucía Ramos Torres",
        "telefono": "912345678",
        "numero_documento": "71234568",
        "colores": ((236, 140, 92), (180, 62, 96)),
        "perfil": {
            "presupuesto_min": Decimal("450.00"),
            "presupuesto_max": Decimal("700.00"),
            "habitos": "No fumo, soy ordenada y trabajo de día",
            "preferencias": "Ambiente tranquilo y respeto por el descanso",
            "descripcion": "Busco compartir un departamento céntrico y bien comunicado.",
        },
    },
    {
        "correo": "companero1.demo@example.com",
        "nombre_completo": "Carlos Mendoza Ruiz",
        "telefono": "934567890",
        "numero_documento": "71234569",
        "colores": ((70, 160, 140), (24, 96, 128)),
        "perfil": {
            "presupuesto_min": Decimal("400.00"),
            "presupuesto_max": Decimal("650.00"),
            "habitos": "Estudio de noche, no fumo y cocino los fines de semana",
            "preferencias": "Compañero responsable y comunicativo",
            "descripcion": "Soy estudiante de ingeniería y busco un espacio tranquilo para estudiar.",
        },
    },
    {
        "correo": "companero2.demo@example.com",
        "nombre_completo": "Ana Flores Díaz",
        "telefono": "956789012",
        "numero_documento": "71234570",
        "colores": ((142, 108, 196), (58, 84, 168)),
        "perfil": {
            "presupuesto_min": Decimal("500.00"),
            "presupuesto_max": Decimal("800.00"),
            "habitos": "Deportista, madrugo y mantengo los espacios limpios",
            "preferencias": "Buena comunicación y convivencia respetuosa",
            "descripcion": "Trabajo cerca del centro y quiero compartir un departamento.",
        },
    },
]

PUBLICACIONES = [
    {
        "titulo": "Habitación luminosa en el centro",
        "descripcion": (
            "Habitación amoblada con cama de dos plazas, escritorio y closet. "
            "Incluye agua, luz e internet. A cinco minutos de la plaza principal."
        ),
        "precio": Decimal("480.00"),
        "direccion": "Jr. Huánuco 245",
        "distrito": "Tingo María",
        "tipo": "habitacion",
        "colores": ((255, 214, 170), (120, 176, 214)),
    },
    {
        "titulo": "Departamento compartido cerca de la UNAS",
        "descripcion": (
            "Departamento de dos dormitorios con sala, cocina equipada y lavandería. "
            "Ideal para estudiantes o profesionales que buscan un ambiente ordenado."
        ),
        "precio": Decimal("650.00"),
        "direccion": "Av. Universitaria 120",
        "distrito": "Tingo María",
        "tipo": "departamento",
        "colores": ((180, 220, 200), (90, 140, 190)),
    },
    {
        "titulo": "Minit departamento amoblado",
        "descripcion": (
            "Espacio independiente con baño propio, cocina pequeña y terraza. "
            "Servicios incluidos y entrada independiente. Disponible desde hoy."
        ),
        "precio": Decimal("720.00"),
        "direccion": "Prolongación Raymondi 330",
        "distrito": "Tingo María",
        "tipo": "departamento",
        "colores": ((235, 205, 220), (110, 160, 170)),
    },
]


def _mezclar(color: tuple[int, int, int], otro: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(int(a * (1 - factor) + b * factor) for a, b in zip(color, otro))


def _png_habitacion(ancho: int, alto: int, inicio: tuple[int, int, int], fin: tuple[int, int, int]) -> bytes:
    """Ilustración sencilla de una habitación para los datos de demostración."""
    piso = _mezclar(fin, (62, 43, 30), 0.55)
    madera = _mezclar(fin, (92, 61, 38), 0.65)
    marco = _mezclar(fin, (32, 42, 52), 0.72)
    colcha = _mezclar(inicio, fin, 0.45)
    pared = _mezclar(inicio, (255, 255, 255), 0.12)
    filas = bytearray()

    for y in range(alto):
        filas.append(0)  # filtro None de PNG
        for x in range(ancho):
            t = (x / max(ancho - 1, 1) + y / max(alto - 1, 1)) / 2
            r = int(pared[0] * (1 - t) + fin[0] * t)
            g = int(pared[1] * (1 - t) + fin[1] * t)
            b = int(pared[2] * (1 - t) + fin[2] * t)

            # Piso de madera con juntas.
            if y >= 300:
                tono = 0.88 if (y // 26) % 2 == 0 else 1.0
                r, g, b = (int(c * tono) for c in piso)
                if y % 26 == 0:
                    r, g, b = _mezclar((r, g, b), (40, 30, 24), 0.35)
                if x in (158, 159, 470, 471):
                    r, g, b = _mezclar((r, g, b), (40, 30, 24), 0.22)

            # Ventana con marco y cielo.
            if 52 <= x <= 214 and 52 <= y <= 198:
                if x < 62 or x > 204 or y < 62 or y > 188 or 128 <= x <= 136 or 122 <= y <= 130:
                    r, g, b = marco
                else:
                    cielo = _mezclar((185, 220, 240), (246, 250, 252), (y - 62) / 126)
                    r, g, b = cielo
                    if x - y in range(-30, 8):
                        r, g, b = _mezclar(cielo, (255, 255, 255), 0.35)

            # Cuadro decorativo.
            if 524 <= x <= 596 and 78 <= y <= 160:
                if x < 532 or x > 588 or y < 86 or y > 152:
                    r, g, b = marco
                else:
                    r, g, b = _mezclar(inicio, (255, 255, 255), 0.25)

            # Cama: cabecero, colchón, almohadas y colcha.
            if 316 <= x <= 594 and 170 <= y <= 232:
                r, g, b = madera
            if 326 <= x <= 586 and 226 <= y <= 318:
                r, g, b = (246, 244, 238) if y < 268 else colcha
                if y >= 310:
                    r, g, b = _mezclar(colcha, (40, 40, 40), 0.25)
            if 342 <= x <= 432 and 238 <= y <= 270:
                r, g, b = (252, 252, 250)
            if 444 <= x <= 532 and 240 <= y <= 268:
                r, g, b = (250, 248, 243)

            # Velador y lámpara.
            if 246 <= x <= 292 and 250 <= y <= 300:
                r, g, b = madera
            if 262 <= x <= 276 and 208 <= y <= 250:
                r, g, b = (90, 86, 80)
            if 248 <= x <= 290 and 184 <= y <= 208:
                r, g, b = _mezclar((250, 233, 190), inicio, 0.25)

            # Alfombra ovalada.
            if ((x - 456) / 138) ** 2 + ((y - 360) / 30) ** 2 <= 1:
                r, g, b = _mezclar(colcha, (255, 255, 255), 0.35)

            filas.extend((max(r, 0), max(g, 0), max(b, 0)))

    def bloque(tipo: bytes, datos: bytes) -> bytes:
        return (
            struct.pack(">I", len(datos))
            + tipo
            + datos
            + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)
        )

    cabecera = struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + bloque(b"IHDR", cabecera)
        + bloque(b"IDAT", zlib.compress(bytes(filas), 6))
        + bloque(b"IEND", b"")
    )


def _png_avatar(tam: int, inicio: tuple[int, int, int], fin: tuple[int, int, int]) -> bytes:
    """Avatar abstracto (fondo degradado + silueta) para la demo."""
    centro = tam / 2
    cabeza_y = tam * 0.40
    cabeza_r = tam * 0.16
    filas = bytearray()

    for y in range(tam):
        filas.append(0)  # filtro None de PNG
        for x in range(tam):
            t = (x + y) / (2 * (tam - 1))
            color = _mezclar(inicio, fin, t)

            # Halo suave detrás de la silueta.
            halo = ((x - centro) ** 2 + (y - tam * 0.56) ** 2) ** 0.5
            if halo <= tam * 0.40:
                color = _mezclar(color, (255, 255, 255), 0.10)

            # Cabeza.
            en_cabeza = (x - centro) ** 2 + (y - cabeza_y) ** 2 <= cabeza_r**2
            # Hombros (elipse que se recorta en el borde inferior).
            en_hombros = (
                (x - centro) ** 2 / (tam * 0.33) ** 2
                + (y - tam * 0.98) ** 2 / (tam * 0.32) ** 2
                <= 1
            )
            if en_cabeza or en_hombros:
                color = _mezclar((255, 255, 255), color, 0.12)

            filas.extend(color)

    def bloque(tipo: bytes, datos: bytes) -> bytes:
        return (
            struct.pack(">I", len(datos))
            + tipo
            + datos
            + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)
        )

    cabecera = struct.pack(">IIBBBBB", tam, tam, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + bloque(b"IHDR", cabecera)
        + bloque(b"IDAT", zlib.compress(bytes(filas), 6))
        + bloque(b"IEND", b"")
    )


def _sincronizar_avatar(usuario, datos) -> None:
    """Genera el avatar de demostración y lo asigna si el usuario no tiene uno."""
    colores = datos.get("colores")
    if not colores:
        return
    carpeta = Path("publicos") / "perfiles" / str(usuario.usuario_id)
    destino = settings.archivos_dir / carpeta / "perfil.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(_png_avatar(320, *colores))
    usuario.foto_perfil = (carpeta / "perfil.png").as_posix()


def _crear_usuario(db, repo, datos, rol, ruc=None, estado="verificada"):
    usuario = repo.por_correo(datos["correo"])
    if usuario is None:
        usuario = Usuario(
            nombre_completo=datos["nombre_completo"],
            correo=datos["correo"],
            clave_hash=hash_clave(CLAVE_DEMO),
            rol=rol,
            estado_cuenta=estado,
            telefono=datos["telefono"],
            tipo_documento="DNI",
            numero_documento=datos["numero_documento"],
        )
        repo.agregar(usuario)
        if rol == "arrendador":
            repo.agregar_arrendador(usuario.usuario_id, ruc)
        else:
            repo.agregar_buscador(usuario.usuario_id)
        print(f"Creado {rol}: {datos['correo']}")
    else:
        print(f"Ya existe {rol}: {datos['correo']}")
    _sincronizar_avatar(usuario, datos)
    return usuario


def _crear_perfil(db, usuario, datos):
    perfil = db.scalar(
        select(PerfilCompanero).where(PerfilCompanero.buscador_id == usuario.usuario_id)
    )
    if perfil is None:
        perfil = PerfilCompanero(buscador_id=usuario.usuario_id, **datos)
        db.add(perfil)
        db.flush()
        print(f"  Perfil de convivencia creado para {usuario.nombre_completo}")
    elif any(getattr(perfil, clave) != valor for clave, valor in datos.items()):
        for clave, valor in datos.items():
            setattr(perfil, clave, valor)
        print(f"  Perfil de convivencia restaurado para {usuario.nombre_completo}")
    return perfil


def _sincronizar_fotos(db, publicacion, datos):
    """Genera/actualiza las ilustraciones y registra las imágenes que falten."""
    carpeta = Path("publicos") / "alojamientos" / str(publicacion.alojamiento_id)
    destino_dir = settings.archivos_dir / carpeta
    destino_dir.mkdir(parents=True, exist_ok=True)
    existentes = {
        imagen.orden
        for imagen in db.scalars(
            select(ImagenAlojamiento).where(
                ImagenAlojamiento.alojamiento_id == publicacion.alojamiento_id
            )
        )
    }
    inicio, fin = datos["colores"]
    for orden in range(1, 3):
        nombre = f"foto-{orden}.png"
        colores = (inicio, fin) if orden == 1 else (fin, inicio)
        (destino_dir / nombre).write_bytes(_png_habitacion(640, 420, *colores))
        if orden not in existentes:
            db.add(
                ImagenAlojamiento(
                    alojamiento_id=publicacion.alojamiento_id,
                    ruta_archivo=(carpeta / nombre).as_posix(),
                    orden=orden,
                )
            )
    db.flush()


def _crear_publicacion(db, arrendador, datos):
    publicacion = db.scalar(
        select(Alojamiento).where(
            Alojamiento.arrendador_id == arrendador.usuario_id,
            Alojamiento.titulo == datos["titulo"],
        )
    )
    if publicacion is not None:
        _sincronizar_fotos(db, publicacion, datos)
        print(f"Publicación ya existente, fotos actualizadas: {datos['titulo']}")
        return publicacion

    publicacion = Alojamiento(
        arrendador_id=arrendador.usuario_id,
        titulo=datos["titulo"],
        descripcion=datos["descripcion"],
        precio=datos["precio"],
        direccion=datos["direccion"],
        distrito=datos["distrito"],
        tipo=datos["tipo"],
        estado="activo",
        destacado=False,
    )
    db.add(publicacion)
    db.flush()
    _sincronizar_fotos(db, publicacion, datos)
    print(f"Publicación creada con 2 fotos: {datos['titulo']}")
    return publicacion


def main() -> None:
    with SessionLocal() as db:
        repo = RepositorioUsuariosSQLAlchemy(db)
        arrendador = _crear_usuario(db, repo, ARRENDADOR, "arrendador", ruc=ARRENDADOR["ruc"])
        for datos in PUBLICACIONES:
            _crear_publicacion(db, arrendador, datos)

        for datos in BUSCADORES:
            usuario = _crear_usuario(db, repo, datos, "buscador")
            _crear_perfil(db, usuario, datos["perfil"])

        db.commit()

    print("\nDatos de demostración listos:")
    print(f"  Arrendador: {ARRENDADOR['correo']} / {CLAVE_DEMO}")
    for datos in BUSCADORES:
        print(f"  Buscador:   {datos['correo']} / {CLAVE_DEMO}")
    print(
        "\nIngresa con buscador.demo@example.com y entra a 'Compartir vivienda' "
        "para ver las coincidencias y los botones de WhatsApp."
    )


if __name__ == "__main__":
    main()
