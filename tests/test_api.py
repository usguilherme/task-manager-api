import pytest
from fastapi.testclient import TestClient
from app.api import create_app

@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "api_teste.db"))
    return TestClient(app)


def test_info(client):
    resposta = client.get("/api")
    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "Gerenciador de Tarefas API"


def test_frontend_servido_na_raiz(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "text/html" in resposta.headers["content-type"]


def test_criar_e_listar_tarefa(client):
    resposta = client.post("/tarefas", json={"titulo": "Estudar FastAPI"})
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["titulo"] == "Estudar FastAPI"
    assert corpo["prioridade"] == "Normal"

    resposta = client.get("/tarefas")
    corpo_lista = resposta.json()
    assert corpo_lista["total"] == 1
    assert len(corpo_lista["itens"]) == 1


def test_busca_por_titulo(client):
    client.post("/tarefas", json={"titulo": "Estudar FastAPI"})
    client.post("/tarefas", json={"titulo": "Comprar leite"})

    resposta = client.get("/tarefas", params={"busca": "fastapi"})
    corpo = resposta.json()
    assert corpo["total"] == 1
    assert corpo["itens"][0]["titulo"] == "Estudar FastAPI"


def test_paginacao(client):
    for i in range(5):
        client.post("/tarefas", json={"titulo": f"Tarefa {i}"})

    resposta = client.get("/tarefas", params={"pagina": 1, "tamanho_pagina": 2})
    corpo = resposta.json()
    assert corpo["total"] == 5
    assert len(corpo["itens"]) == 2


def test_criar_tarefa_titulo_vazio_retorna_422(client):
    resposta = client.post("/tarefas", json={"titulo": ""})
    assert resposta.status_code == 422


def test_obter_tarefa_inexistente_retorna_404(client):
    resposta = client.get("/tarefas/999")
    assert resposta.status_code == 404


def test_concluir_tarefa(client):
    criada = client.post("/tarefas", json={"titulo": "X"}).json()
    resposta = client.post(f"/tarefas/{criada['id']}/concluir")
    assert resposta.status_code == 200
    assert resposta.json()["concluida"] is True


def test_editar_tarefa(client):
    criada = client.post("/tarefas", json={"titulo": "Antigo"}).json()
    resposta = client.patch(f"/tarefas/{criada['id']}", json={"titulo": "Novo"})
    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Novo"


def test_deletar_tarefa(client):
    criada = client.post("/tarefas", json={"titulo": "X"}).json()
    resposta = client.delete(f"/tarefas/{criada['id']}")
    assert resposta.status_code == 204
    assert client.get(f"/tarefas/{criada['id']}").status_code == 404


def test_estatisticas(client):
    client.post("/tarefas", json={"titulo": "A"})
    resposta = client.get("/tarefas/resumo/estatisticas")
    assert resposta.json()["total"] == 1
