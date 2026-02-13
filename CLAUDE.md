# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## VISAO GERAL

**Claude Projects Intelligence Hub** - sistema central para unificar, analisar e evoluir todos os projetos do Victor Vilanova.

- **326 projetos indexados** (65 raiz, 261 subprojetos)
- **9 dominios de negocio** classificados
- **5 monorepos** com hierarquia completa
- **Path**: `/Users/victorvilanova/projetos/Claude-Projetos`
- **Banco**: `index/projects.db` (SQLite)

---

## COMANDOS ESSENCIAIS

```bash
# Scan completo (todas as localizacoes)
python3 index/scanner.py full-scan --verbose

# Dashboard + relatorio
python3 dashboard/cli.py
python3 dashboard/cli.py --export-md > docs/reports/status-$(date +%Y-%m-%d).md

# Prioridades
python3 analysis/priority.py list --top 10
python3 analysis/priority.py suggest
python3 analysis/priority.py update-all

# Status
python3 analysis/status.py analyze-all
python3 analysis/status.py suggest-archive

# Duplicatas
python3 analysis/duplicates.py find
python3 analysis/duplicates.py suggest-consolidation

# Dominios de negocio
python3 analysis/domains.py stats
python3 analysis/domains.py integrations
python3 analysis/domains.py update-tags

# Memoria (bridge para Memory Ultimate)
python3 memory/integration.py search "query" --limit 10
python3 memory/integration.py checkpoint "projeto" "status" "proximo"

# Scripts automatizados
./scripts/scan-all.sh         # Scan + analise + relatorio
./scripts/update-index.sh     # Update incremental (ultimos 7 dias)
./scripts/get-next-task.sh    # Sugere proximo projeto
```

---

## ARQUITETURA

### Banco de Dados (`index/projects.db`)

Schema v2.0 com hierarquia pai/filho:
- `projects` - Tabela principal com parent_project_id, depth_level, is_monorepo
- `project_docs` - Documentacao por projeto
- `project_dependencies` - Dependencias entre projetos
- `project_tasks` - Tarefas/TODOs
- `analysis_history` - Historico de analises
- `scan_history` - Historico de scans

Views: `v_priority_projects`, `v_monorepos`, `v_project_hierarchy` (recursive CTE)

### Scanner (`index/scanner.py`)

Scan recursivo ate 10 niveis de profundidade. Usa abordagem de 2 passes:
1. Passe 1: Insere todos os projetos com parent_project_id=NULL
2. Passe 2: Resolve hierarquia pai/filho com IDs reais do banco

Detecta: 8 tipos de projeto, monorepos (pnpm/lerna/nx/turbo), git info, documentacao, memory system.

### Analise de Prioridade (`analysis/priority.py`)

Score 0-4 (0=maxima). Fatores:
- Documentacao (-1.0 max)
- Memory system (-0.5)
- Git recente (gradual: -1.0 a 0)
- Monorepo com subprojetos (-0.5 a -1.0)
- Framework producao (-0.5)
- Duplicatas (+0.5 penalidade)

### Analise de Status (`analysis/status.py`)

- active: commits <= 30 dias
- maintained: commits <= 180 dias
- legacy: sem mudancas recentes
- archived: marcado para arquivamento

### Analise de Duplicatas (`analysis/duplicates.py`)

Detecta: mesmo nome, nomes similares (sufixos -temp, -backup), mesmo git remote.

### Analise de Dominios (`analysis/domains.py`)

9 dominios: ERP/CRM/COMEX, Ponto Eletronico, Financeiro, Marketing/Sites, AI/ML, Gaming, Educacao, Logistica, Infraestrutura.

### Integracao Memory (`memory/integration.py`)

Bridge para Memory Ultimate V3.0 em `/Downloads/Master-claude/memory/core/`.

### Dashboard (`dashboard/cli.py`)

CLI com Rich (fallback texto). Exporta Markdown.

---

## ESTRUTURA DE ARQUIVOS

```
Claude-Projetos/
├── index/
│   ├── scanner.py          # Scanner recursivo 2-pass
│   ├── schema.sql          # Schema v2.0 hierarquico
│   └── projects.db         # Banco SQLite
├── analysis/
│   ├── priority.py         # Priorizacao multi-fator
│   ├── status.py           # Classificacao de status
│   ├── duplicates.py       # Deteccao de duplicatas
│   └── domains.py          # Dominios de negocio
├── memory/
│   └── integration.py      # Bridge Memory Ultimate
├── dashboard/
│   └── cli.py              # Dashboard interativo
├── scripts/
│   ├── scan-all.sh         # Scan completo
│   ├── update-index.sh     # Update incremental
│   └── get-next-task.sh    # Proxima tarefa
└── docs/
    ├── INVENTORY.md         # Inventario basico
    ├── INVENTORY_DEEP.md    # Inventario profundo
    └── reports/             # Relatorios historicos
```

---

## REGRAS

1. **Read-only**: Este sistema indexa e analisa, nao modifica outros projetos
2. **Paths absolutos**: Sempre usar paths absolutos no banco e scripts
3. **Respeitar memoria existente**: Projetos com `.memory/` usam seu sistema proprio
4. **Ler CLAUDE.md do projeto**: Antes de trabalhar em qualquer projeto, ler seu `.claude/CLAUDE.md`
5. **Memory Ultimate**: Sempre executar do diretorio correto ou usar o wrapper

---

**Versao**: 2.0.0
**Atualizado**: 2026-02-13
**Status**: Totalmente implementado
