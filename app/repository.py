#Repositório de tarefas.
from __future__ import annotations
from .database import Database
from .exceptions import TarefaNotFoundError
from .logging_config import get_logger
from .models import Prioridade, Tarefa

logger = get_logger(__name__)


class TarefaRepository:
    def __init__(self, db: Database):
        self.db = db

    def adicionar(self, tarefa: Tarefa) -> Tarefa:
        with self.db.conexao() as conn:
            cursor = conn.execute(
                """INSERT INTO tarefas
                   (titulo, descricao, prioridade, data_vencimento, concluida, data_criacao)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    tarefa.titulo,
                    tarefa.descricao,
                    tarefa.prioridade.value,
                    tarefa.data_vencimento,
                    int(tarefa.concluida),
                    tarefa.data_criacao,
                ),
            )
            tarefa.id = cursor.lastrowid
        logger.info("Tarefa criada (id=%s, titulo=%r)", tarefa.id, tarefa.titulo)
        return tarefa

    def listar_todas(
        self,
        busca: str | None = None,
        limite: int | None = None,
        offset: int = 0,
    ) -> list[Tarefa]:
        query = "SELECT * FROM tarefas"
        parametros: list = []

        if busca:
            query += " WHERE titulo LIKE ? OR descricao LIKE ?"
            termo = f"%{busca}%"
            parametros.extend([termo, termo])

        query += " ORDER BY id"

        if limite is not None:
            query += " LIMIT ? OFFSET ?"
            parametros.extend([limite, offset])

        with self.db.conexao() as conn:
            linhas = conn.execute(query, parametros).fetchall()
        return [self._linha_para_tarefa(linha) for linha in linhas]

    def contar(self, busca: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM tarefas"
        parametros: list = []
        if busca:
            query += " WHERE titulo LIKE ? OR descricao LIKE ?"
            termo = f"%{busca}%"
            parametros.extend([termo, termo])
        with self.db.conexao() as conn:
            return conn.execute(query, parametros).fetchone()[0]

    def buscar_por_id(self, tarefa_id: int) -> Tarefa | None:
        with self.db.conexao() as conn:
            linha = conn.execute(
                "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
            ).fetchone()
        return self._linha_para_tarefa(linha) if linha else None

    def atualizar(self, tarefa: Tarefa) -> None:
        with self.db.conexao() as conn:
            resultado = conn.execute(
                """UPDATE tarefas
                   SET titulo = ?, descricao = ?, prioridade = ?,
                       data_vencimento = ?, concluida = ?
                   WHERE id = ?""",
                (
                    tarefa.titulo,
                    tarefa.descricao,
                    tarefa.prioridade.value,
                    tarefa.data_vencimento,
                    int(tarefa.concluida),
                    tarefa.id,
                ),
            )
            if resultado.rowcount == 0:
                raise TarefaNotFoundError(tarefa.id)

    def deletar(self, tarefa_id: int) -> None:
        with self.db.conexao() as conn:
            resultado = conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
            if resultado.rowcount == 0:
                raise TarefaNotFoundError(tarefa_id)

    def deletar_concluidas(self) -> int:
        with self.db.conexao() as conn:
            resultado = conn.execute("DELETE FROM tarefas WHERE concluida = 1")
            return resultado.rowcount

    @staticmethod
    def _linha_para_tarefa(linha) -> Tarefa:
        tarefa = Tarefa(
            titulo=linha["titulo"],
            descricao=linha["descricao"] or "",
            prioridade=Prioridade(linha["prioridade"]),
            data_vencimento=linha["data_vencimento"],
        )
        tarefa.id = linha["id"]
        tarefa.concluida = bool(linha["concluida"])
        tarefa.data_criacao = linha["data_criacao"]
        return tarefa
