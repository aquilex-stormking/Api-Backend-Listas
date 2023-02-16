from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DB_UID: str
    DB_PWD: str
    DB_SERVER: str
    DB_NAME: str
    DB_PORT: int
    NAME_ARCHIVO_CARGUE:str
    EMAIL:str
    CONTRASEÑA_EMAIL:str
    NAME_ARCHIVO_REPORTE:str
    URLOFAC:str
    URLONU:str
    URLFBI:str
    ENCRYPT:str
    class Config:
        env_file = ".env.sample"

# New decorator for cache
@lru_cache()
def get_settings():
    return Settings()