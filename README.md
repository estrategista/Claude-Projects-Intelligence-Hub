# Claude Projects Intelligence Hub

**Sistema central de inteligência unificada para todos os projetos Victor Vilanova**

## 🎯 Objetivo

Unificar a gestão, análise e evolução de **todos os projetos** em todos os locais:
- `/Users/victorvilanova/projetos/` - 17 projetos
- `/Users/victorvilanova/Downloads/` - 39 projetos/pastas
- Drives externos e HD externo (quando conectados)

## 🧠 Inteligência Central

Este sistema:
1. **Indexa** todos os projetos existentes
2. **Analisa** status, dependências e próximos passos
3. **Prioriza** trabalho baseado em valor e urgência
4. **Integra** com Memory Ultimate V3.0 para contexto perpétuo
5. **Sugere** melhorias, conclusões e otimizações
6. **Rastreia** progresso ao longo do tempo

## 📊 Estatísticas Atuais (Scan Profundo 2026-02-13)

| Métrica | Quantidade |
|---------|-----------|
| **Projetos Node.js (package.json)** | **156+** |
| **Repositórios Git (.git/)** | **45+** |
| **Monorepos (pnpm workspaces)** | **7** |
| **Projetos Python** | **8-10** |
| **Projetos PHP (Laravel)** | **1** |
| **Com Memory System** | 3 |
| **Com CLAUDE.md personalizado** | 3 |
| **Profundidade máxima encontrada** | **5 níveis** |
| **Localizações escaneadas** | 2 principais |

## 🚀 Quick Start

```bash
# Escanear todos os projetos
./scripts/scan-all.sh

# Ver próxima tarefa prioritária
./scripts/get-next-task.sh

# Atualizar índice
./scripts/update-index.sh

# Checkpoint de progresso
python3 memory/integration.py checkpoint "o que foi feito" "status" "próximo"
```

## 📁 Estrutura

```
Claude-Projetos/
├── index/              # Banco de dados SQLite com todos os projetos
├── analysis/           # Scripts de análise e priorização
├── memory/             # Integração com Memory Ultimate V3.0
├── dashboard/          # Interface CLI e web (opcional)
├── scripts/            # Scripts de automação
└── docs/               # Documentação e relatórios
```

## 🔗 Integração com Memory Ultimate

Usa o sistema existente em `/Users/victorvilanova/Downloads/Master-claude/memory/core/`:
- **claude_memory_ultimate.db** - 248 memórias, embeddings, busca semântica
- **Comandos disponíveis**: search, remember, checkpoint, stats, health

## 📋 Projetos Principais Rastreados

### ⭐ Top Priority (Projetos Raiz Principais)
1. **sisconect-v4-multi-tenant** - ERP/CRM/COMEX MONOREPO (95% completo, 7 subprojetos)
2. **Ponyo-Digital** - Sistema de ponto eletrônico (funcional)
3. **Master-claude** - Central de comando JARVIS (memória perpétua)

### 🏗️ Monorepos Complexos
- **Novo-Sisconect** - 21+ packages em 3 níveis (maior monorepo)
- **TabPro/alphatab** - 14+ packages multi-linguagem
- **Hybrid-Neural-System** - Node.js + Python híbrido
- **Sisconect-Enterprise** - Versão enterprise
- **Cordoba** - Webapp com backend separado
- **tab-pro-codex** - Editor de tabs

### 🔧 Em Desenvolvimento
- vilanova-ai-lab - Laboratório IA (3 níveis de profundidade)
- TowerControl_Core - Sistema de controle (Python + Node)
- aprova-saas - SaaS de aprovação

### 📊 Famílias de Projetos Identificadas
- **Sisconect** - 8 versões/variações diferentes
- **TabPro** - 3 projetos relacionados
- **VVN Digital** - 5+ sites e backups
- **Rifas** - 2 versões (normal + Gemini AI)

### 📦 Para Organizar
- Múltiplas versões do Sisconect (consolidar)
- Backups antigos (Vivax-BACKUP-2026-02-10)
- Projetos sem git em /projetos/ (inicializar)
- Documentação de monorepos (adicionar CLAUDE.md)

## 🎯 Próximos Passos

1. [x] Inventário completo de projetos
2. [x] Inventário profundo recursivo (156+ projetos encontrados!)
3. [x] Schema v2.0 com suporte a hierarquia
4. [ ] Implementar scanner.py recursivo funcional
5. [ ] Criar banco de dados SQLite com índice
6. [ ] Sistema de análise de prioridade
7. [ ] Dashboard CLI
8. [ ] Integração com Memory Ultimate
9. [ ] Sistema de sugestões automáticas

## 📚 Documentação

- `CLAUDE.md` - Instruções completas para Claude Code ⭐
- `docs/INVENTORY.md` - Inventário básico
- `docs/INVENTORY_DEEP.md` - Inventário profundo com hierarquia completa ⭐
- `docs/ARCHITECTURE.md` - Arquitetura do sistema (a criar)
- `index/schema.sql` - Schema v2.0 do banco de dados

---

**Criado**: 2026-02-13
**Versão**: 1.0.0
**Status**: Initial Setup
**Projetos Rastreados**: 15+ ativos, 29+ storage
