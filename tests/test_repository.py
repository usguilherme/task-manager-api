import pytest

from app.exceptions import TarefaNotFoundError
from app.models import Tarefa


def test_adicionar_e_listar(repository):
    repository.adicionar(Tarefa(titulo="Comprar leite"))
    tarefas = repository.listar_todas()
    assert len(tarefas) == 1
    assert tarefas[0].titulo == "Comprar leite"


def test_buscar_por_id(repository):
    tarefa = repository.adicionar(Tarefa(titulo="X"))
    encontrada = repository.buscar_por_id(tarefa.id)
    assert encontrada.id == tarefa.id


def test_buscar_id_inexistente_retorna_none(repository):
    assert repository.buscar_por_id(999) is None


def test_atualizar_tarefa_inexistente_levanta_erro(repository):
    fantasma = Tarefa(titulo="X")
    fantasma.id = 999
    with pytest.raises(TarefaNotFoundError):
        repository.atualizar(fantasma)


def test_deletar_tarefa(repository):
    tarefa = repository.adicionar(Tarefa(titulo="X"))
    repository.deletar(tarefa.id)
    assert repository.buscar_por_id(tarefa.id) is None


def test_deletar_inexistente_levanta_erro(repository):
    with pytest.raises(TarefaNotFoundError):
        repository.deletar(999)


def test_deletar_concluidas(repository):
    t1 = repository.adicionar(Tarefa(titulo="A"))
    repository.adicionar(Tarefa(titulo="B"))
    t1.marcar_concluida()
    repository.atualizar(t1)

    removidas = repository.deletar_concluidas()
    assert removidas == 1
    assert len(repository.listar_todas()) == 1


def test_persistencia_entre_instancias(db, repository):
    repository.adicionar(Tarefa(titulo="Persistente"))

    from app.repository import TarefaRepository
    novo_repository = TarefaRepository(db)
    assert len(novo_repository.listar_todas()) == 1
