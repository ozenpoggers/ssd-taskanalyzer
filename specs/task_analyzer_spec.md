# Especificação SDD — TaskAnalyzer

Contrato de negócio transposto da Fase 1 (Google Docs: *Especificação SSD TaskAnalyzer*).

## 1. Propósito

Analisar uma lista de tarefas e produzir métricas de produtividade: totais, tempo médio de
conclusão (geral e por prioridade) e taxa de atraso.

## 2. Contrato de Interface

```python
class TaskValidationError(ValueError): ...

@dataclass(frozen=True)
class Task:
    id: str
    prioridade: str              # "baixa" | "media" | "alta" | "urgente"
    data_criacao: datetime
    data_prazo: datetime
    data_conclusao: datetime | None = None   # None => pendente

@dataclass(frozen=True)
class TaskAnalysisReport:
    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    tempo_medio_conclusao_horas: float
    tempo_medio_conclusao_horas_por_prioridade: dict[str, float]
    taxa_atraso_percentual: float

def analyze_tasks(tarefas: list[Task], data_referencia: datetime | None = None) -> TaskAnalysisReport
```

## 3. Regras de Negócio

- `tempo_medio_conclusao_horas`: média de `(data_conclusao - data_criacao)` em horas, apenas tarefas concluídas.
- Por prioridade: mesma regra, agrupada por prioridade (só aparecem prioridades com tarefas concluídas).
- Tarefa atrasada: concluída com `data_conclusao > data_prazo`, ou pendente com `data_referencia > data_prazo`.
- `taxa_atraso_percentual = atrasadas / total_tarefas * 100`, arredondada a 2 casas.
- Lista vazia ou sem tarefas concluídas: médias `0.0` e taxa `0.0`, **sem exceção**.

## 4. Cenários de Aceite (Dado / Quando / Então)

**Cenário 1 — Sucesso:** dado um conjunto de tarefas válidas, quando `analyze_tasks` é executada,
então retorna `total_tarefas`, `total_concluidas`, `total_pendentes`, tempos médios (geral e por
prioridade) e `taxa_atraso_percentual` corretos.

**Cenário 2 — Exceção:** dado uma tarefa com `data_conclusao < data_criacao` (ou `data_prazo <
data_criacao`, ou prioridade inválida), quando `analyze_tasks` é executada, então dispara
`TaskValidationError` com mensagem clara.

**Casos de borda:** lista vazia ou apenas tarefas pendentes retornam `0.0` nas médias sem lançar
exceções; conclusão exatamente no prazo não é atraso.
