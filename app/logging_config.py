"""Configuração de logging da aplicação.

Substitui os `print()` espalhados pelo código original por logs de
verdade — com nível, timestamp e origem —, que podem ser filtrados,
redirecionados para um arquivo ou coletados por uma ferramenta de
observabilidade em produção.
"""
from __future__ import annotations

import logging

from .config import settings


def configurar_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(nome: str) -> logging.Logger:
    return logging.getLogger(nome)
