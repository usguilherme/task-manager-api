from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GERENCIADOR_")

    database_path: str = "dados/tarefas.db"
    log_level: str = "INFO"


settings = Settings()
