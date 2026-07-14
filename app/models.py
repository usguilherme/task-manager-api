#Modelo de domínio: Tarefa.
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Prioridade(str, Enum):
    BAIXA = "Baixa"
    NORMAL = "Normal"
    ALTA = "Alta"


@dataclass
class Tarefa:
    titulo: str
    descricao: str = ""
    prioridade: Prioridade = Prioridade.NORMAL
    data_vencimento: str | None = None
    id: int | None = None
    concluida: bool = False
    data_criacao: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def __post_init__(self) -> None:
        if not self.titulo or not self.titulo.strip():
            raise ValueError("O título da tarefa não pode ser vazio.")

        if isinstance(self.prioridade, str):
            self.prioridade = Prioridade(self.prioridade)

        if self.data_vencimento:
            try:
                datetime.strptime(self.data_vencimento, "%Y-%m-%d")
            except ValueError as erro:
                raise ValueError(
                    "data_vencimento deve estar no formato YYYY-MM-DD."
                ) from erro

    def marcar_concluida(self) -> None:
        self.concluida = True

    def reabrir(self) -> None:
        self.concluida = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prioridade": self.prioridade.value,
            "data_vencimento": self.data_vencimento,
            "concluida": self.concluida,
            "data_criacao": self.data_criacao,
        }

    def __str__(self) -> str:
        status = "✓" if self.concluida else "○"
        return f"{status} [{self.prioridade.value}] {self.titulo}"
