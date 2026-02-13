# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📍 VISÃO GERAL

Este é o **Claude Projects Intelligence Hub** - um sistema central de inteligência para **unificar, analisar e evoluir todos os projetos** do Victor Vilanova.

**Objetivo**: Manter um índice vivo de todos os projetos em todas as localizações, com análise de status, priorização automática e integração com o sistema de memória perpétua.

**Path**: `/Users/victorvilanova/projetos/Claude-Projetos`

---

## 🎯 WORKFLOW PRINCIPAL

### 1. Iniciar Sessão

```bash
# Ver inventário atualizado
cat docs/INVENTORY.md

# Ver status de próximas tarefas
./scripts/get-next-task.sh  # (a criar)

# Carregar contexto da memória central
cd /Users/victorvilanova/Downloads/Master-claude/memory/core
python3 memory_ultimate.py search "Claude-Projetos" --limit 5
```

### 2. Escanear/Atualizar Projetos

```bash
# Escanear todos os projetos
./scripts/scan-all.sh  # (a criar)

# Atualizar apenas um projeto específico
python3 index/scanner.py update --path /caminho/para/projeto

# Atualizar índice completo
./scripts/update-index.sh  # (a criar)
```

### 3. Análise e Priorização

```bash
# Ver projetos por prioridade
python3 analysis/priority.py list

# Analisar status de um projeto
python3 analysis/status.py check --name sisconect-v4-multi-tenant

# Sugerir próximos passos
python3 analysis/priority.py suggest
```

### 4. Finalizar Sessão

```bash
# Criar checkpoint na memória central
cd /Users/victorvilanova/Downloads/Master-claude/memory/core
python3 memory_ultimate.py checkpoint \
  "Claude-Projetos" \
  "O que foi feito nesta sessão" \
  "Próximos passos"
```

---

## 🗄️ ARQUITETURA

### Banco de Dados Central (`index/projects.db`)

SQLite database que mantém:

```sql
-- Tabela principal de projetos
projects (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  path TEXT UNIQUE,
  type TEXT,  -- 'nodejs', 'python', 'storage', 'git-only'
  status TEXT,  -- 'active', 'archived', 'legacy', 'unknown'
  priority INTEGER,  -- 0 (max) a 4 (min)
  has_git BOOLEAN,
  has_claude_md BOOLEAN,
  has_memory_system BOOLEAN,
  git_remote TEXT,
  git_branch TEXT,
  last_scanned TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Documentação por projeto
project_docs (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,
  doc_type TEXT,  -- 'README', 'CLAUDE.md', 'CONTEXT.md', etc.
  path TEXT,
  line_count INTEGER,
  last_modified TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
)

-- Dependências entre projetos
project_dependencies (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,
  depends_on_project_id INTEGER,
  dependency_type TEXT,  -- 'monorepo', 'shared-lib', 'related'
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (depends_on_project_id) REFERENCES projects(id)
)

-- Tarefas/TODOs por projeto
project_tasks (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,
  description TEXT,
  status TEXT,  -- 'pending', 'in_progress', 'done'
  priority INTEGER,
  created_at TIMESTAMP,
  completed_at TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
)

-- Histórico de análises
analysis_history (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,
  analysis_type TEXT,  -- 'status', 'priority', 'health'
  result TEXT,
  suggestions TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
)
```

### Scanner (`index/scanner.py`)

Responsável por:
1. Varrer diretórios configurados (`/projetos/`, `/Downloads/`)
2. Identificar tipo de projeto (Node.js, Python, storage)
3. Extrair metadados (git status, documentação, dependencies)
4. Atualizar banco de dados
5. Detectar mudanças desde último scan

**Comandos**:
```bash
python3 index/scanner.py scan --location /Users/victorvilanova/projetos
python3 index/scanner.py update --path /caminho/para/projeto/específico
python3 index/scanner.py full-scan  # Escaneia todas as localizações
```

### Analisador de Prioridade (`analysis/priority.py`)

Calcula prioridade baseado em:
- **Completude**: Quanto está completo (README.md analysis)
- **Atividade Git**: Commits recentes, branch ativa
- **Documentação**: Presença de CLAUDE.md, CONTEXT.md
- **Tipo**: Produção > Desenvolvimento > Legado
- **Dependências**: Projetos que bloqueiam outros
- **Valor de negócio**: Tags/categorias (manual ou inferido)

**Output**: Score 0-4 (0 = máxima prioridade)

**Comandos**:
```bash
python3 analysis/priority.py calculate --project sisconect-v4-multi-tenant
python3 analysis/priority.py list --top 10
python3 analysis/priority.py suggest  # Sugere qual projeto trabalhar
```

### Analisador de Status (`analysis/status.py`)

Determina status de um projeto:
- **Active**: Em desenvolvimento ativo, commits recentes
- **Maintained**: Funcional, sem mudanças recentes
- **Legacy**: Código antigo, sem git ou doc
- **Archived**: Marcado explicitamente para arquivamento
- **Unknown**: Precisa de análise manual

**Comandos**:
```bash
python3 analysis/status.py check --name sisconect-v4-multi-tenant
python3 analysis/status.py analyze-all
python3 analysis/status.py suggest-archive  # Sugere projetos para arquivar
```

### Integração com Memory Ultimate (`memory/integration.py`)

Ponte entre este sistema e `/Users/victorvilanova/Downloads/Master-claude/memory/core/`:

```bash
# Buscar contexto histórico de um projeto
python3 memory/integration.py search "sisconect-v4" --limit 10

# Salvar checkpoint de sessão
python3 memory/integration.py checkpoint \
  "Projeto trabalhado" \
  "O que foi feito" \
  "Próximos passos"

# Recuperar último estado de um projeto
python3 memory/integration.py get-last-state --project sisconect-v4-multi-tenant
```

**Internamente chama**:
```bash
cd /Users/victorvilanova/Downloads/Master-claude/memory/core
python3 memory_ultimate.py [comando]
```

---

## 📊 DASHBOARD CLI (`dashboard/cli.py`)

Interface interativa para visualizar status:

```bash
# Dashboard principal
python3 dashboard/cli.py

# Modo interativo
python3 dashboard/cli.py --interactive

# Exportar relatório
python3 dashboard/cli.py --export-md > reports/status-$(date +%Y-%m-%d).md
```

**Output esperado**:
```
╔══════════════════════════════════════════════════════════════╗
║         CLAUDE PROJECTS INTELLIGENCE HUB v1.0                ║
╚══════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS
   Total de projetos: 15 ativos, 29 storage
   Repositórios Git: 14
   Com Memory System: 3
   Última atualização: 2026-02-13 10:30:00

🎯 TOP 5 PRIORIDADES
   P0 [95%] sisconect-v4-multi-tenant - ERP/CRM/COMEX
   P0 [80%] Master-claude - Sistema JARVIS
   P1 [70%] Ponyo-Digital - Sistema de ponto
   P1 [40%] vilanova-ai-lab - Laboratório IA
   P1 [60%] TowerControl_Core - Sistema de controle

⚡ AÇÃO SUGERIDA
   → Finalizar sisconect-v4-multi-tenant (5% restante)
     Sprint 21: Otimizações finais de performance
```

---

## 🔧 SCRIPTS PRINCIPAIS

### `scripts/scan-all.sh`

Escaneia todas as localizações configuradas:

```bash
#!/bin/bash
# Escanear /projetos/
python3 index/scanner.py scan --location /Users/victorvilanova/projetos

# Escanear /Downloads/
python3 index/scanner.py scan --location /Users/victorvilanova/Downloads

# Gerar relatório
python3 dashboard/cli.py --export-md > docs/INVENTORY.md

echo "✓ Scan completo! Ver docs/INVENTORY.md"
```

### `scripts/update-index.sh`

Atualiza apenas projetos que mudaram:

```bash
#!/bin/bash
# Atualiza apenas projetos com mudanças git nos últimos 7 dias
python3 index/scanner.py update --changed-since 7d

echo "✓ Índice atualizado!"
```

### `scripts/get-next-task.sh`

Sugere próxima tarefa baseado em prioridade:

```bash
#!/bin/bash
# Pega próxima tarefa de maior prioridade
python3 analysis/priority.py suggest

# Recupera contexto do projeto sugerido
PROJECT=$(python3 analysis/priority.py suggest --output-name)
python3 memory/integration.py get-last-state --project "$PROJECT"
```

---

## 📁 ESTRUTURA DE ARQUIVOS

```
Claude-Projetos/
├── CLAUDE.md                    # Este arquivo
├── README.md                    # Overview do projeto
├── setup.sh                     # Setup inicial automatizado
│
├── index/                       # Sistema de indexação
│   ├── projects.db              # SQLite database (criado automaticamente)
│   ├── scanner.py               # Scanner recursivo de projetos
│   └── schema.sql               # Schema v2.0 com suporte a hierarquia
│
├── analysis/                    # Análise e inteligência
│   ├── priority.py              # Cálculo de prioridade
│   ├── status.py                # Análise de status
│   └── suggestions.py           # Geração de sugestões
│
├── memory/                      # Integração memória
│   ├── integration.py           # Bridge para Memory Ultimate
│   └── config.py                # Configurações de memória
│
├── dashboard/                   # Interfaces
│   ├── cli.py                   # Dashboard CLI
│   └── web.html                 # Dashboard web (futuro)
│
├── scripts/                     # Automação
│   ├── scan-all.sh              # Scan completo recursivo
│   ├── update-index.sh          # Atualização incremental
│   └── get-next-task.sh         # Próxima tarefa
│
└── docs/                        # Documentação
    ├── INVENTORY.md             # Inventário básico (gerado)
    ├── INVENTORY_DEEP.md        # Inventário profundo com hierarquia ⭐
    ├── ARCHITECTURE.md          # Arquitetura detalhada (a criar)
    └── reports/                 # Relatórios históricos
        └── status-YYYY-MM-DD.md
```

---

## 🔗 INTEGRAÇÃO COM PROJETOS EXISTENTES

### Projetos com Memory System

Três projetos já têm sistema de memória próprio:

1. **sisconect-v4-multi-tenant** - `.memory/sisconect_memory.py`
   ```bash
   cd /Users/victorvilanova/projetos/sisconect-v4-multi-tenant
   .memory/quick_context.sh  # Recuperar contexto
   python3 .memory/sisconect_memory.py checkpoint "msg" "status" "next"
   ```

2. **tab-pro-claude** - `.memory/` custom
3. **Master-claude** - `memory/` central

**Integração**: `memory/integration.py` deve saber chamar cada sistema específico quando trabalhar com esses projetos.

### Projetos com CLAUDE.md

Três projetos têm instruções específicas:

1. **sisconect-v4-multi-tenant** - `.claude/CLAUDE.md` (895 linhas)
2. **Ponyo-Digital** - `.claude/CLAUDE.md` (168 linhas)
3. **tab-pro-claude** - `.claude/CLAUDE.md`

**Regra**: Sempre ler `.claude/CLAUDE.md` do projeto antes de trabalhar nele.

---

## 🚨 REGRAS IMPORTANTES

### 1. Não Modificar Projetos Diretamente

Este sistema é **read-only** por padrão. Apenas:
- Indexa projetos
- Analisa status
- Sugere ações
- Mantém metadados

**Não deve**:
- Modificar código de outros projetos
- Criar commits automáticos
- Alterar configurações

### 2. Respeitar Sistemas de Memória Existentes

Projetos com `.memory/` próprio devem usar seu sistema interno, não o central.

### 3. Atualizar INVENTORY.md Regularmente

Sempre que rodar scan completo, atualizar `docs/INVENTORY.md`:
```bash
./scripts/scan-all.sh  # Já atualiza automaticamente
```

### 4. Path Absolutos

Sempre usar paths absolutos no banco de dados e scripts:
- ✅ `/Users/victorvilanova/projetos/sisconect-v4-multi-tenant`
- ❌ `~/projetos/sisconect-v4-multi-tenant`
- ❌ `../sisconect-v4-multi-tenant`

### 5. Integração com Memory Ultimate

**SEMPRE** executar comandos do diretório correto:
```bash
cd /Users/victorvilanova/Downloads/Master-claude/memory/core
python3 memory_ultimate.py [comando]
```

Ou usar o wrapper:
```bash
python3 memory/integration.py [comando]  # Já navega para path correto
```

---

## 📚 COMANDOS RÁPIDOS

### Scan e Indexação

```bash
# Scan completo de todas as localizações
./scripts/scan-all.sh

# Atualizar apenas projetos modificados
./scripts/update-index.sh

# Escanear localização específica
python3 index/scanner.py scan --location /Users/victorvilanova/projetos

# Atualizar projeto específico
python3 index/scanner.py update --path /Users/victorvilanova/projetos/sisconect-v4-multi-tenant
```

### Análise

```bash
# Ver prioridades
python3 analysis/priority.py list

# Calcular prioridade de projeto
python3 analysis/priority.py calculate --project sisconect-v4-multi-tenant

# Analisar status
python3 analysis/status.py check --name sisconect-v4-multi-tenant

# Sugerir próxima tarefa
python3 analysis/priority.py suggest
```

### Dashboard

```bash
# Ver dashboard
python3 dashboard/cli.py

# Exportar relatório
python3 dashboard/cli.py --export-md > docs/reports/status-$(date +%Y-%m-%d).md
```

### Memória

```bash
# Buscar contexto histórico
python3 memory/integration.py search "sisconect-v4" --limit 10

# Checkpoint de sessão
python3 memory/integration.py checkpoint \
  "Claude-Projetos scan" \
  "Atualizou índice de 15 projetos" \
  "Implementar análise de prioridade"

# Recuperar último estado
python3 memory/integration.py get-last-state --project sisconect-v4-multi-tenant
```

### Verificação de Integridade

```bash
# Verificar banco de dados
sqlite3 index/projects.db "SELECT COUNT(*) FROM projects;"

# Ver projetos sem documentação
sqlite3 index/projects.db "SELECT name FROM projects WHERE has_claude_md = 0 AND has_git = 1;"

# Ver projetos de alta prioridade
sqlite3 index/projects.db "SELECT name, priority, status FROM projects WHERE priority <= 1 ORDER BY priority;"
```

---

## 🎯 PRÓXIMOS PASSOS (IMPLEMENTAÇÃO)

### Fase 1: Core System (Prioridade Máxima)
- [ ] Criar `index/scanner.py` - Scanner de projetos
- [ ] Criar `index/schema.sql` - Schema do banco
- [ ] Criar `analysis/priority.py` - Cálculo de prioridade
- [ ] Criar `analysis/status.py` - Análise de status
- [ ] Criar `scripts/scan-all.sh` - Script de scan

### Fase 2: Integração (Prioridade Alta)
- [ ] Criar `memory/integration.py` - Bridge para Memory Ultimate
- [ ] Criar `dashboard/cli.py` - Dashboard CLI básico
- [ ] Criar `scripts/update-index.sh` - Update incremental
- [ ] Criar `scripts/get-next-task.sh` - Sugestão de tarefa

### Fase 3: Inteligência Avançada (Prioridade Média)
- [ ] `analysis/suggestions.py` - IA para sugerir melhorias
- [ ] Dashboard web (`dashboard/web.html`)
- [ ] Sistema de tags/categorias
- [ ] Análise de dependências entre projetos
- [ ] Geração automática de relatórios

### Fase 4: Automação (Prioridade Baixa)
- [ ] Cron job para scan diário
- [ ] Notificações de mudanças importantes
- [ ] Backup automático do banco
- [ ] Exportação para outros formatos (JSON, CSV)

---

## 💡 FILOSOFIA DO SISTEMA

1. **Centralizado mas Não Invasivo**: Indexa sem modificar
2. **Inteligente mas Transparente**: IA sugere, humano decide
3. **Perpétuo mas Leve**: Usa memória existente, não duplica
4. **Completo mas Focado**: Conhece tudo, prioriza o importante
5. **Automatizado mas Controlado**: Scans automáticos, ações manuais

---

**Criado**: 2026-02-13
**Versão**: 1.0.0
**Status**: Initial Documentation
**Próximo**: Implementar Fase 1 (Core System)
