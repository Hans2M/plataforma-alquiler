from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # SQLAlchemy URL.create codifica correctamente contraseñas especiales.
    database_url: str | None = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "alquiler_app"
    db_password: str = ""
    db_name: str = "alquiler_db"
    secret_key: str = "CAMBIAR-solo-para-pruebas-no-usar-en-produccion"
    access_token_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 5
    archivos_dir: Path = Path("/data/archivos")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
