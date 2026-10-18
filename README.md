# sdd-taskanalyzer

Módulo **TaskAnalyzer** desenvolvido com *Spec-Driven Development* (SDD) e assistentes de IA,
guiado por `CONTEXT_RULES.md` e `specs/task_analyzer_spec.md`. Projeto da disciplina Bootcamp III (CEUB EAD).

## Estrutura

```
sdd-taskanalyzer/
├── README.md
├── CONTEXT_RULES.md
├── .gitignore
├── requirements.txt
├── pytest.ini
├── specs/task_analyzer_spec.md
├── tests/test_harness.py
└── src/task_analyzer.py
```

## Como executar

Requer Python 3.11+.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Exemplo de uso

```python
from datetime import datetime
from src.task_analyzer import Task, analyze_tasks

tarefas = [
    Task("T1", "alta", datetime(2026, 1, 1, 8), datetime(2026, 1, 2, 8), datetime(2026, 1, 1, 18)),
]
print(analyze_tasks(tarefas, datetime(2026, 1, 10)))
```

## Status

Fase 2: implementação via IA, test harness (pytest) e versionamento. Fase 3: CI/CD e Docker.
