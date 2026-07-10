"""API REST do gerenciador de tarefas.

Usa `create_app()` como factory (em vez de um único `app` global) para
que os testes possam instanciar a aplicação apontando para um banco
de dados temporário, sem interferir no banco real.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .database import Database
from .exceptions import TarefaNotFoundError
from .logging_config import configurar_logging, get_logger
from .repository import TarefaRepository
from .service import GerenciadorTarefas

logger = get_logger(__name__)


class TarefaCreate(BaseModel):
    titulo: str = Field(..., min_length=1, examples=["Estudar FastAPI"])
    descricao: str = ""
    prioridade: str = Field("Normal", pattern="^(Baixa|Normal|Alta)$")
    data_vencimento: str | None = None


class TarefaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    prioridade: str | None = Field(None, pattern="^(Baixa|Normal|Alta)$")
    data_vencimento: str | None = None


class TarefaOut(BaseModel):
    id: int
    titulo: str
    descricao: str
    prioridade: str
    data_vencimento: str | None
    concluida: bool
    data_criacao: str


class TarefasPaginadas(BaseModel):
    itens: list[TarefaOut]
    total: int
    pagina: int
    tamanho_pagina: int


def create_app(caminho_db: str | None = None) -> FastAPI:
    configurar_logging()
    app = FastAPI(
        title="Gerenciador de Tarefas API",
        description="API REST para gerenciamento de tarefas com persistência em SQLite.",
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    db = Database(caminho_db or settings.database_path)
    repository = TarefaRepository(db)
    gerenciador = GerenciadorTarefas(repository)
    logger.info("Aplicação iniciada (banco: %s)", db.caminho_db)

    @app.get("/api", tags=["Info"])
    def info():
        return {"mensagem": "Gerenciador de Tarefas API", "docs": "/docs"}

    @app.get("/tarefas", response_model=TarefasPaginadas, tags=["Tarefas"])
    def listar_tarefas(
        filtro: str = "todas",
        busca: str | None = None,
        pagina: int = 1,
        tamanho_pagina: int = 20,
    ):
        tarefas = gerenciador.listar(filtro, busca, pagina, tamanho_pagina)
        total = gerenciador.contar(filtro, busca)
        return {
            "itens": [t.to_dict() for t in tarefas],
            "total": total,
            "pagina": pagina,
            "tamanho_pagina": tamanho_pagina,
        }

    @app.post("/tarefas", response_model=TarefaOut, status_code=201, tags=["Tarefas"])
    def criar_tarefa(dados: TarefaCreate):
        try:
            tarefa = gerenciador.adicionar_tarefa(**dados.model_dump())
        except ValueError as erro:
            raise HTTPException(status_code=422, detail=str(erro)) from erro
        return tarefa.to_dict()

    @app.get("/tarefas/{tarefa_id}", response_model=TarefaOut, tags=["Tarefas"])
    def obter_tarefa(tarefa_id: int):
        try:
            return gerenciador.buscar(tarefa_id).to_dict()
        except TarefaNotFoundError as erro:
            raise HTTPException(status_code=404, detail=str(erro)) from erro

    @app.patch("/tarefas/{tarefa_id}", response_model=TarefaOut, tags=["Tarefas"])
    def editar_tarefa(tarefa_id: int, dados: TarefaUpdate):
        try:
            tarefa = gerenciador.editar(tarefa_id, **dados.model_dump(exclude_unset=True))
        except TarefaNotFoundError as erro:
            raise HTTPException(status_code=404, detail=str(erro)) from erro
        except ValueError as erro:
            raise HTTPException(status_code=422, detail=str(erro)) from erro
        return tarefa.to_dict()

    @app.post("/tarefas/{tarefa_id}/concluir", response_model=TarefaOut, tags=["Tarefas"])
    def concluir_tarefa(tarefa_id: int):
        try:
            tarefa = gerenciador.concluir(tarefa_id)
            logger.info("Tarefa concluída (id=%s)", tarefa_id)
            return tarefa.to_dict()
        except TarefaNotFoundError as erro:
            raise HTTPException(status_code=404, detail=str(erro)) from erro

    @app.post("/tarefas/{tarefa_id}/reabrir", response_model=TarefaOut, tags=["Tarefas"])
    def reabrir_tarefa(tarefa_id: int):
        try:
            return gerenciador.reabrir(tarefa_id).to_dict()
        except TarefaNotFoundError as erro:
            raise HTTPException(status_code=404, detail=str(erro)) from erro

    @app.delete("/tarefas/{tarefa_id}", status_code=204, tags=["Tarefas"])
    def deletar_tarefa(tarefa_id: int):
        try:
            gerenciador.deletar(tarefa_id)
            logger.info("Tarefa removida (id=%s)", tarefa_id)
        except TarefaNotFoundError as erro:
            raise HTTPException(status_code=404, detail=str(erro)) from erro

    @app.delete("/tarefas/concluidas/limpar", tags=["Tarefas"])
    def limpar_concluidas():
        removidas = gerenciador.limpar_concluidas()
        logger.info("Tarefas concluídas removidas em lote (quantidade=%s)", removidas)
        return {"removidas": removidas}

    @app.get("/tarefas/resumo/estatisticas", tags=["Estatísticas"])
    def estatisticas():
        return gerenciador.resumo()

    # serve o frontend estático (static/index.html) na raiz "/".
    # montado por último: rotas da API acima têm prioridade sobre este mount.
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")

    return app


app = create_app()
