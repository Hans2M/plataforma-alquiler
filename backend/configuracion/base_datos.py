from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from configuracion.configuracion import settings

url = settings.database_url or URL.create(
    "postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)
engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)
# expire_on_commit=False permite serializar la respuesta después del commit
# sin recargar cada atributo (y sin depender de una sesión ya cerrada).
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def obtener_db():
    """Unidad de trabajo por petición.

    Los servicios hacen flush pero NO commit. El límite transaccional vive
    aquí: se confirma al terminar sin errores y se revierte si algo falla.
    """
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
