from __future__ import annotations
from .exceptions import TarefaNotFoundError
from .models import Prioridade, Tarefa
from .repository import TarefaRepository


class GerenciadorTarefas:
    def __init__(self, repository: TarefaRepository):
        self.repository = repository

    def adicionar_tarefa(
        self,
        titulo: str,
        descricao: str = "",
        prioridade: str = "Normal",
        data_vencimento: str | None = None,
    ) -> Tarefa:
        tarefa = Tarefa(
            titulo=titulo,
            descricao=descricao,
            prioridade=Prioridade(prioridade),
            data_vencimento=data_vencimento,
        )
        return self.repository.adicionar(tarefa)

    def listar(
        self,
        filtro: str = "todas",
        busca: str | None = None,
        pagina: int = 1,
        tamanho_pagina: int | None = None,
    ) -> list[Tarefa]:
        # Busca (LIKE) é delegada ao SQL, que é mais eficiente para isso.
        # Filtro por status e paginação acontecem em memória, DEPOIS da busca,
        # para não paginar antes de saber quais itens realmente pertencem
        # ao filtro pedido (senão a página 1 poderia vir incompleta).
        tarefas = self.repository.listar_todas(busca=busca)

        if filtro == "pendentes":
            tarefas = [t for t in tarefas if not t.concluida]
        elif filtro == "concluidas":
            tarefas = [t for t in tarefas if t.concluida]

        if tamanho_pagina:
            inicio = (pagina - 1) * tamanho_pagina
            tarefas = tarefas[inicio : inicio + tamanho_pagina]

        return tarefas

    def contar(self, filtro: str = "todas", busca: str | None = None) -> int:
        tarefas = self.repository.listar_todas(busca=busca)
        if filtro == "pendentes":
            return sum(1 for t in tarefas if not t.concluida)
        if filtro == "concluidas":
            return sum(1 for t in tarefas if t.concluida)
        return len(tarefas)

    def buscar(self, tarefa_id: int) -> Tarefa:
        tarefa = self.repository.buscar_por_id(tarefa_id)
        if tarefa is None:
            raise TarefaNotFoundError(tarefa_id)
        return tarefa

    def concluir(self, tarefa_id: int) -> Tarefa:
        tarefa = self.buscar(tarefa_id)
        tarefa.marcar_concluida()
        self.repository.atualizar(tarefa)
        return tarefa

    def reabrir(self, tarefa_id: int) -> Tarefa:
        tarefa = self.buscar(tarefa_id)
        tarefa.reabrir()
        self.repository.atualizar(tarefa)
        return tarefa

    def editar(self, tarefa_id: int, **campos) -> Tarefa:
        tarefa = self.buscar(tarefa_id)
        for campo, valor in campos.items():
            if valor is None:
                continue
            if campo == "prioridade":
                valor = Prioridade(valor)
            setattr(tarefa, campo, valor)
        self.repository.atualizar(tarefa)
        return tarefa

    def deletar(self, tarefa_id: int) -> None:
        self.repository.deletar(tarefa_id)

    def limpar_concluidas(self) -> int:
        return self.repository.deletar_concluidas()

    def ordenar_por_data(self) -> list[Tarefa]:
        tarefas = self.repository.listar_todas()
        return sorted(
            tarefas, key=lambda t: (t.data_vencimento is None, t.data_vencimento)
        )

    def resumo(self) -> dict:
        tarefas = self.repository.listar_todas()
        total = len(tarefas)
        concluidas = sum(1 for t in tarefas if t.concluida)
        pendentes = total - concluidas
        taxa = round((concluidas / total) * 100, 1) if total else 0.0
        return {
            "total": total,
            "concluidas": concluidas,
            "pendentes": pendentes,
            "taxa_conclusao": taxa,
        }
