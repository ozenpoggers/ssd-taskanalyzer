"""Test Harness do TaskAnalyzer (Cenários de aceite 1 e 2 + casos de borda)."""

from datetime import datetime, timedelta

import pytest

from src.task_analyzer import Task, TaskValidationError, analyze_tasks

BASE = datetime(2026, 1, 1, 8, 0)
REFERENCIA = datetime(2026, 1, 10, 8, 0)


def _tarefa(
    id_: str,
    prioridade: str,
    horas_conclusao: float | None,
    horas_prazo: float,
) -> Task:
    """Cria uma tarefa a partir de offsets em horas relativos a BASE."""
    conclusao = BASE + timedelta(hours=horas_conclusao) if horas_conclusao is not None else None
    return Task(
        id=id_,
        prioridade=prioridade,
        data_criacao=BASE,
        data_prazo=BASE + timedelta(hours=horas_prazo),
        data_conclusao=conclusao,
    )


def test_cenario_1_sucesso_calcula_metricas_corretas() -> None:
    """Cenário 1: tarefas válidas geram as métricas corretas."""
    tarefas = [
        _tarefa("T1", "alta", 10, 12),         # concluída no prazo, 10h
        _tarefa("T2", "alta", 30, 24),         # concluída atrasada, 30h
        _tarefa("T3", "baixa", 20, 48),        # concluída no prazo, 20h
        _tarefa("T4", "media", None, 24),      # pendente com prazo vencido (atrasada)
        _tarefa("T5", "urgente", None, 1000),  # pendente dentro do prazo
    ]

    r = analyze_tasks(tarefas, REFERENCIA)

    assert r.total_tarefas == 5
    assert r.total_concluidas == 3
    assert r.total_pendentes == 2
    assert r.tempo_medio_conclusao_horas == pytest.approx(20.0)
    assert r.tempo_medio_conclusao_horas_por_prioridade == {
        "alta": pytest.approx(20.0),
        "baixa": pytest.approx(20.0),
    }
    # atrasadas: T2 e T4 -> 2/5 = 40%
    assert r.taxa_atraso_percentual == pytest.approx(40.0)


def test_cenario_2_data_conclusao_anterior_a_criacao_dispara_erro() -> None:
    """Cenário 2: data_conclusao < data_criacao dispara TaskValidationError."""
    invalida = Task(
        id="T-X",
        prioridade="alta",
        data_criacao=BASE,
        data_prazo=BASE + timedelta(hours=10),
        data_conclusao=BASE - timedelta(hours=1),
    )

    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([invalida], REFERENCIA)


def test_prazo_anterior_a_criacao_dispara_erro() -> None:
    """data_prazo < data_criacao também é inconsistente."""
    invalida = Task("T-Y", "baixa", BASE, BASE - timedelta(hours=2))

    with pytest.raises(TaskValidationError, match="data_prazo"):
        analyze_tasks([invalida], REFERENCIA)


def test_prioridade_invalida_dispara_erro() -> None:
    """Prioridade fora do conjunto permitido dispara TaskValidationError."""
    invalida = Task("T-Z", "critica", BASE, BASE + timedelta(hours=5))

    with pytest.raises(TaskValidationError, match="prioridade"):
        analyze_tasks([invalida], REFERENCIA)


def test_borda_lista_vazia_retorna_zeros_sem_excecao() -> None:
    """Borda: lista vazia retorna 0.0 nas médias, sem exceção."""
    r = analyze_tasks([], REFERENCIA)

    assert r.total_tarefas == 0
    assert r.total_concluidas == 0
    assert r.total_pendentes == 0
    assert r.tempo_medio_conclusao_horas == 0.0
    assert r.tempo_medio_conclusao_horas_por_prioridade == {}
    assert r.taxa_atraso_percentual == 0.0


def test_borda_apenas_pendentes_retorna_media_zero() -> None:
    """Borda: só tarefas pendentes -> média 0.0 e sem divisão por zero."""
    tarefas = [
        _tarefa("T1", "alta", None, 1000),
        _tarefa("T2", "baixa", None, 1000),
    ]

    r = analyze_tasks(tarefas, REFERENCIA)

    assert r.total_concluidas == 0
    assert r.total_pendentes == 2
    assert r.tempo_medio_conclusao_horas == 0.0
    assert r.tempo_medio_conclusao_horas_por_prioridade == {}
    assert r.taxa_atraso_percentual == 0.0


def test_borda_conclusao_exatamente_no_prazo_nao_e_atraso() -> None:
    """Borda: concluída exatamente no prazo não conta como atrasada."""
    r = analyze_tasks([_tarefa("T1", "media", 10, 10)], REFERENCIA)

    assert r.taxa_atraso_percentual == 0.0
