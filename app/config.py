"""Configuração da aplicação via variáveis de ambiente.

Antes, o caminho do banco de dados estava hardcoded em vários lugares
(`dados/tarefas.db`). Com `Settings`, ele pode ser sobrescrito por uma
variável de ambiente (ex: em produção, Docker, ou nos testes) sem
tocar em nenhuma linha de código.

Uso:
    export GERENCIADOR_DATABASE_PATH=/var/data/tarefas.db
    export GERENCIADOR_LOG_LEVEL=DEBUG
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GERENCIADOR_")

    database_path: str = "dados/tarefas.db"
    log_level: str = "INFO"


settings = Settings()
