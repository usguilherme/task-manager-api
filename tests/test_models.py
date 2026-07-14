import pytest
from app.models import Prioridade, Tarefa


def test_criar_tarefa_valida():
    tarefa = Tarefa(titulo="Estudar", prioridade=Prioridade.ALTA)
    assert tarefa.titulo == "Estudar"
    assert tarefa.concluida is False


def test_titulo_vazio_levanta_erro():
    with pytest.raises(ValueError):
        Tarefa(titulo="   ")


def test_data_vencimento_invalida_levanta_erro():
    with pytest.raises(ValueError):
        Tarefa(titulo="X", data_vencimento="10/07/2026")


def test_marcar_concluida_e_reabrir():
    tarefa = Tarefa(titulo="X")
    tarefa.marcar_concluida()
    assert tarefa.concluida is True
    tarefa.reabrir()
    assert tarefa.concluida is False


def test_prioridade_invalida_levanta_erro():
    with pytest.raises(ValueError):
        Tarefa(titulo="X", prioridade="Urgente")
