class TarefaNotFoundError(Exception):
    #Levantada quando uma tarefa não é encontrada pelo ID

    def __init__(self, tarefa_id: int):
        self.tarefa_id = tarefa_id
        super().__init__(f"Tarefa com ID {tarefa_id} não encontrada.")


class TarefaValidationError(Exception):
    """Levantada quando os dados fornecidos para uma tarefa são inválidos."""
