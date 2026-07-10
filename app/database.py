"""Camada de infraestrutura do banco de dados.

O codigo original abria e fechava conexão manualmente em toda função:
se uma exceção acontecesse no meio, a conexão vazava e a alteração
podia ficar sem commit nem rollback. Aqui, `Database.conexao()` é um
context manager: garante commit em caso de sucesso, rollback em caso
de erro, e fechamento da conexão sempre — não importa o que aconteça.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class Database:
    def __init__(self, caminho_db: str = "dados/tarefas.db"):
        self.caminho_db = caminho_db
        Path(self.caminho_db).parent.mkdir(parents=True, exist_ok=True)
        self._criar_schema()

    @contextmanager
    def conexao(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.caminho_db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _criar_schema(self) -> None:
        with self.conexao() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    prioridade TEXT NOT NULL,
                    data_vencimento TEXT,
                    concluida INTEGER NOT NULL DEFAULT 0,
                    data_criacao TEXT NOT NULL
                )
                """
            )
