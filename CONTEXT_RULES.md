# CONTEXT_RULES — Governança de Contexto para Agentes de IA

Regras fornecidas como contexto obrigatório a qualquer assistente de IA que gere código para o TaskAnalyzer.

## Diretrizes Arquiteturais (Obrigatórias)

- Python 3.11+ como versão mínima.
- Type hints em 100% das funções, métodos e parâmetros.
- Princípio de Responsabilidade Única (SRP) e código limpo (PEP 8).
- Docstrings no padrão Google style para módulos, classes, funções e parâmetros.
- Funções pequenas, coesas e com um único propósito.
- Tratamento de exceções específico, com mensagens claras (`TaskValidationError`).
- Prevenção explícita de divisão por zero (médias de listas vazias retornam `0.0`).
- Logs estruturados com o módulo padrão `logging`.
- Código legível e manutenível, com nomes descritivos de variáveis e funções.

## Proibições Explícitas

- Não utilizar bibliotecas externas não autorizadas (somente biblioteca padrão e `pytest`).
- Não alterar, remover ou adaptar os cenários de teste definidos na especificação.
- Não modificar a estrutura de pastas do repositório.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar a assinatura (nome e parâmetros) das funções públicas sem autorização.
- Não gerar código sem testes correspondentes para as novas funcionalidades.
- Não inserir código duplicado ou desnecessário.
- Não assumir comportamentos não especificados no contrato de negócio.
