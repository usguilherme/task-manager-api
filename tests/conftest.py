import pytest

from app.database import Database
from app.repository import TarefaRepository
from app.service import GerenciadorTarefas


@pytest.fixture
def db(tmp_path):
    return Database(str(tmp_path / "teste.db"))


@pytest.fixture
def repository(db):
    return TarefaRepository(db)


@pytest.fixture
def gerenciador(repository):
    return GerenciadorTarefas(repository)
