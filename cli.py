"""Interface de linha de comando.

Note que este arquivo não sabe nada sobre SQL: ele só chama métodos de
`GerenciadorTarefas`. A mesma lógica de negócio que roda aqui também
roda por trás da API REST em `app/api.py`.
"""
from __future__ import annotations

import os

from app.database import Database
from app.exceptions import TarefaNotFoundError
from app.repository import TarefaRepository
from app.service import GerenciadorTarefas


def limpar_tela() -> None:
    os.system("clear" if os.name == "posix" else "cls")


def pausar() -> None:
    input("\nPressione ENTER para continuar...")


def exibir_menu() -> None:
    print("=" * 60)
    print("📋 GERENCIADOR DE TAREFAS")
    print("=" * 60)
    print("1. Adicionar tarefa")
    print("2. Listar tarefas")
    print("3. Concluir tarefa")
    print("4. Editar tarefa")
    print("5. Deletar tarefa")
    print("6. Ver estatísticas")
    print("0. Sair")
    print("=" * 60)


def adicionar_tarefa_menu(gerenciador: GerenciadorTarefas) -> None:
    print("\n📝 ADICIONAR TAREFA")
    print("-" * 60)
    titulo = input("Título da tarefa: ").strip()
    descricao = input("Descrição: ").strip()

    print("\nPrioridade:")
    print("1. Baixa  2. Normal  3. Alta")
    opcao = input("Escolha (1/2/3): ").strip()
    prioridades = {"1": "Baixa", "2": "Normal", "3": "Alta"}
    prioridade = prioridades.get(opcao, "Normal")

    data = input("Data de vencimento (YYYY-MM-DD) [opcional]: ").strip()
    data_vencimento = data or None

    try:
        tarefa = gerenciador.adicionar_tarefa(titulo, descricao, prioridade, data_vencimento)
        print(f"✓ Tarefa '{tarefa.titulo}' adicionada com ID {tarefa.id}!")
    except ValueError as erro:
        print(f"❌ {erro}")


def listar_tarefas_menu(gerenciador: GerenciadorTarefas) -> None:
    print("\n📋 LISTAR TAREFAS")
    print("-" * 60)
    print("1. Todas  2. Pendentes  3. Concluídas")
    opcao = input("Escolha um filtro (1/2/3): ").strip()
    filtros = {"1": "todas", "2": "pendentes", "3": "concluidas"}
    filtro = filtros.get(opcao, "todas")

    print("\n" + "=" * 60)
    print(f"TAREFAS - FILTRO: {filtro.upper()}")
    print("=" * 60)
    tarefas = gerenciador.listar(filtro)
    if not tarefas:
        print("(nenhuma tarefa encontrada)")
    for tarefa in tarefas:
        print(f"#{tarefa.id} {tarefa}")
    print("=" * 60)


def concluir_tarefa_menu(gerenciador: GerenciadorTarefas) -> None:
    print("\n✓ CONCLUIR TAREFA")
    print("-" * 60)
    for tarefa in gerenciador.listar("pendentes"):
        print(f"#{tarefa.id} {tarefa}")
    try:
        tarefa_id = int(input("\nDigite o ID da tarefa: "))
        gerenciador.concluir(tarefa_id)
        print(f"✓ Tarefa {tarefa_id} concluída!")
    except ValueError:
        print("❌ ID inválido!")
    except TarefaNotFoundError as erro:
        print(f"❌ {erro}")


def editar_tarefa_menu(gerenciador: GerenciadorTarefas) -> None:
    print("\n✏️ EDITAR TAREFA")
    print("-" * 60)
    try:
        tarefa_id = int(input("Digite o ID da tarefa: "))
        novo_titulo = input("Novo título (ENTER para manter): ").strip() or None
        gerenciador.editar(tarefa_id, titulo=novo_titulo)
        print(f"✓ Tarefa {tarefa_id} atualizada!")
    except ValueError:
        print("❌ ID inválido!")
    except TarefaNotFoundError as erro:
        print(f"❌ {erro}")


def deletar_tarefa_menu(gerenciador: GerenciadorTarefas) -> None:
    print("\n🗑️ DELETAR TAREFA")
    print("-" * 60)
    for tarefa in gerenciador.listar("todas"):
        print(f"#{tarefa.id} {tarefa}")
    try:
        tarefa_id = int(input("\nDigite o ID da tarefa: "))
        if input("Tem certeza? (s/n): ").lower() == "s":
            gerenciador.deletar(tarefa_id)
            print(f"✓ Tarefa {tarefa_id} removida!")
        else:
            print("Operação cancelada.")
    except ValueError:
        print("❌ ID inválido!")
    except TarefaNotFoundError as erro:
        print(f"❌ {erro}")


def ver_estatisticas(gerenciador: GerenciadorTarefas) -> None:
    resumo = gerenciador.resumo()
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS")
    print("=" * 60)
    print(f"Total: {resumo['total']}")
    print(f"✓ Concluídas: {resumo['concluidas']}")
    print(f"○ Pendentes: {resumo['pendentes']}")
    print(f"Taxa de conclusão: {resumo['taxa_conclusao']}%")
    print("=" * 60)


def main() -> None:
    db = Database()
    gerenciador = GerenciadorTarefas(TarefaRepository(db))

    acoes = {
        "1": adicionar_tarefa_menu,
        "2": listar_tarefas_menu,
        "3": concluir_tarefa_menu,
        "4": editar_tarefa_menu,
        "5": deletar_tarefa_menu,
        "6": ver_estatisticas,
    }

    while True:
        limpar_tela()
        exibir_menu()
        opcao = input("\nEscolha uma opção: ").strip()
        limpar_tela()

        if opcao == "0":
            print("\n👋 Até logo!")
            break

        acao = acoes.get(opcao)
        if acao:
            acao(gerenciador)
        else:
            print("❌ Opção inválida!")
        pausar()


if __name__ == "__main__":
    main()
