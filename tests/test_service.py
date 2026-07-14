import pytest
from app.exceptions import TarefaNotFoundError

def test_adicionar_tarefa(gerenciador):
    tarefa = gerenciador.adicionar_tarefa("Estudar", prioridade="Alta")
    assert tarefa.id == 1
    assert tarefa.prioridade.value == "Alta"


def test_listar_filtro_pendentes(gerenciador):
    gerenciador.adicionar_tarefa("A")
    b = gerenciador.adicionar_tarefa("B")
    gerenciador.concluir(b.id)

    pendentes = gerenciador.listar("pendentes")
    assert len(pendentes) == 1
    assert pendentes[0].titulo == "A"


def test_buscar_inexistente_levanta_erro(gerenciador):
    with pytest.raises(TarefaNotFoundError):
        gerenciador.buscar(999)


def test_concluir_e_reabrir(gerenciador):
    tarefa = gerenciador.adicionar_tarefa("X")
    gerenciador.concluir(tarefa.id)
    assert gerenciador.buscar(tarefa.id).concluida is True

    gerenciador.reabrir(tarefa.id)
    assert gerenciador.buscar(tarefa.id).concluida is False


def test_editar_tarefa(gerenciador):
    tarefa = gerenciador.adicionar_tarefa("Antigo", prioridade="Baixa")
    gerenciador.editar(tarefa.id, titulo="Novo", prioridade="Alta")

    atualizada = gerenciador.buscar(tarefa.id)
    assert atualizada.titulo == "Novo"
    assert atualizada.prioridade.value == "Alta"


def test_limpar_concluidas(gerenciador):
    a = gerenciador.adicionar_tarefa("A")
    gerenciador.adicionar_tarefa("B")
    gerenciador.concluir(a.id)

    removidas = gerenciador.limpar_concluidas()
    assert removidas == 1
    assert len(gerenciador.listar()) == 1


def test_ordenar_por_data(gerenciador):
    gerenciador.adicionar_tarefa("Segunda", data_vencimento="2026-07-10")
    gerenciador.adicionar_tarefa("Primeira", data_vencimento="2026-07-01")

    ordenadas = gerenciador.ordenar_por_data()
    assert ordenadas[0].titulo == "Primeira"


def test_busca_por_titulo_ou_descricao(gerenciador):
    gerenciador.adicionar_tarefa("Estudar FastAPI", descricao="Revisar rotas")
    gerenciador.adicionar_tarefa("Comprar leite")

    encontradas = gerenciador.listar(busca="fastapi")
    assert len(encontradas) == 1
    assert encontradas[0].titulo == "Estudar FastAPI"


def test_paginacao(gerenciador):
    for i in range(5):
        gerenciador.adicionar_tarefa(f"Tarefa {i}")

    pagina_1 = gerenciador.listar(pagina=1, tamanho_pagina=2)
    pagina_2 = gerenciador.listar(pagina=2, tamanho_pagina=2)

    assert len(pagina_1) == 2
    assert len(pagina_2) == 2
    assert pagina_1[0].titulo != pagina_2[0].titulo


def test_contar_respeita_filtro(gerenciador):
    a = gerenciador.adicionar_tarefa("A")
    gerenciador.adicionar_tarefa("B")
    gerenciador.concluir(a.id)

    assert gerenciador.contar() == 2
    assert gerenciador.contar(filtro="concluidas") == 1
    assert gerenciador.contar(filtro="pendentes") == 1


def test_resumo(gerenciador):
    a = gerenciador.adicionar_tarefa("A")
    gerenciador.adicionar_tarefa("B")
    gerenciador.concluir(a.id)

    resumo = gerenciador.resumo()
    assert resumo == {
        "total": 2,
        "concluidas": 1,
        "pendentes": 1,
        "taxa_conclusao": 50.0,
    }
