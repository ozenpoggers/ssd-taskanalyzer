"""Módulo TaskAnalyzer: métricas de produtividade a partir de uma lista de tarefas.

Gerado via assistente de IA seguindo CONTEXT_RULES.md e specs/task_analyzer_spec.md
e homologado por revisão humana.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: tuple[str, ...] = ("baixa", "media", "alta", "urgente")
SEGUNDOS_POR_HORA: float = 3600.0


class TaskValidationError(ValueError):
    """Erro disparado quando uma tarefa contém dados inválidos ou inconsistentes."""


@dataclass(frozen=True)
class Task:
    """Representa uma tarefa a ser analisada.

    Attributes:
        id: Identificador único da tarefa.
        prioridade: Uma de "baixa", "media", "alta" ou "urgente".
        data_criacao: Momento de criação da tarefa.
        data_prazo: Momento limite para conclusão.
        data_conclusao: Momento de conclusão, ou None se ainda pendente.
    """

    id: str
    prioridade: str
    data_criacao: datetime
    data_prazo: datetime
    data_conclusao: datetime | None = None


@dataclass(frozen=True)
class TaskAnalysisReport:
    """Resultado da análise de tarefas.

    Attributes:
        total_tarefas: Quantidade total de tarefas analisadas.
        total_concluidas: Quantidade de tarefas concluídas.
        total_pendentes: Quantidade de tarefas pendentes.
        tempo_medio_conclusao_horas: Média geral de horas até a conclusão.
        tempo_medio_conclusao_horas_por_prioridade: Média de horas por prioridade.
        taxa_atraso_percentual: Percentual de tarefas atrasadas sobre o total.
    """

    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    tempo_medio_conclusao_horas: float
    tempo_medio_conclusao_horas_por_prioridade: dict[str, float] = field(default_factory=dict)
    taxa_atraso_percentual: float = 0.0


def _validar_tarefa(tarefa: Task) -> None:
    """Valida consistência de uma tarefa.

    Args:
        tarefa: Tarefa a ser validada.

    Raises:
        TaskValidationError: Se a prioridade for inválida ou as datas forem inconsistentes.
    """
    if tarefa.prioridade not in PRIORIDADES_VALIDAS:
        raise TaskValidationError(
            f"Tarefa {tarefa.id}: prioridade inválida '{tarefa.prioridade}'."
        )
    if tarefa.data_prazo < tarefa.data_criacao:
        raise TaskValidationError(
            f"Tarefa {tarefa.id}: data_prazo anterior a data_criacao."
        )
    if tarefa.data_conclusao is not None and tarefa.data_conclusao < tarefa.data_criacao:
        raise TaskValidationError(
            f"Tarefa {tarefa.id}: data_conclusao anterior a data_criacao."
        )


def _horas_ate_conclusao(tarefa: Task, data_conclusao: datetime) -> float:
    """Calcula as horas entre a criação da tarefa e a conclusão informada.

    Args:
        tarefa: Tarefa analisada.
        data_conclusao: Momento de conclusão da tarefa.

    Returns:
        Duração em horas.
    """
    return (data_conclusao - tarefa.data_criacao).total_seconds() / SEGUNDOS_POR_HORA


def _media(valores: list[float]) -> float:
    """Calcula a média de uma lista, retornando 0.0 se estiver vazia.

    Args:
        valores: Valores numéricos.

    Returns:
        Média aritmética ou 0.0 para lista vazia (evita divisão por zero).
    """
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


def _esta_atrasada(tarefa: Task, data_referencia: datetime) -> bool:
    """Indica se a tarefa está atrasada.

    Args:
        tarefa: Tarefa a verificar.
        data_referencia: Data usada para avaliar tarefas ainda pendentes.

    Returns:
        True se concluída após o prazo ou pendente com prazo vencido.
    """
    if tarefa.data_conclusao is not None:
        return tarefa.data_conclusao > tarefa.data_prazo
    return data_referencia > tarefa.data_prazo


def analyze_tasks(
    tarefas: list[Task],
    data_referencia: datetime | None = None,
) -> TaskAnalysisReport:
    """Analisa uma lista de tarefas e retorna métricas de produtividade.

    Args:
        tarefas: Lista de tarefas a analisar. Pode ser vazia.
        data_referencia: Data para avaliar atraso de tarefas pendentes.
            Se None, usa o momento atual.

    Returns:
        Relatório com totais, tempos médios (geral e por prioridade) e taxa de atraso.

    Raises:
        TaskValidationError: Se alguma tarefa for inválida ou inconsistente.
    """
    referencia = data_referencia or datetime.now()
    logger.info("Iniciando análise de %d tarefas.", len(tarefas))

    for tarefa in tarefas:
        _validar_tarefa(tarefa)

    horas_gerais: list[float] = []
    horas_por_prioridade: dict[str, list[float]] = {}
    for tarefa in tarefas:
        if tarefa.data_conclusao is None:
            continue
        horas = _horas_ate_conclusao(tarefa, tarefa.data_conclusao)
        horas_gerais.append(horas)
        horas_por_prioridade.setdefault(tarefa.prioridade, []).append(horas)

    total_tarefas = len(tarefas)
    total_concluidas = len(horas_gerais)
    atrasadas = sum(1 for t in tarefas if _esta_atrasada(t, referencia))
    taxa_atraso = (atrasadas / total_tarefas * 100.0) if total_tarefas else 0.0

    relatorio = TaskAnalysisReport(
        total_tarefas=total_tarefas,
        total_concluidas=total_concluidas,
        total_pendentes=total_tarefas - total_concluidas,
        tempo_medio_conclusao_horas=_media(horas_gerais),
        tempo_medio_conclusao_horas_por_prioridade={
            prioridade: _media(horas) for prioridade, horas in horas_por_prioridade.items()
        },
        taxa_atraso_percentual=round(taxa_atraso, 2),
    )
    logger.info("Análise concluída: %s", relatorio)
    return relatorio
