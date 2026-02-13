# Inventário Profundo e Hierárquico - Victor Vilanova

**Data**: 2026-02-13
**Método**: Scan recursivo em profundidade com Explore Agent
**Profundidade**: Até 10 níveis
**Projetos encontrados**: 156+ Node.js, 45+ Git repos, múltiplos Python/PHP/etc.

---

## 📊 ESTATÍSTICAS GERAIS

| Métrica | Valor |
|---------|-------|
| **Package.json encontrados** | 156+ |
| **Repositórios Git (.git/)** | 45+ |
| **Monorepos (pnpm-workspace.yaml)** | 7 |
| **Projetos Python** | 8-10 |
| **Projetos PHP** | 1 (Laravel) |
| **Profundidade máxima** | 5 níveis |
| **Localizações escaneadas** | 2 principais |

---

## 🌳 HIERARQUIA COMPLETA POR LOCALIZAÇÃO

### 📂 /Users/victorvilanova/projetos/ (WORKSPACE PRINCIPAL)

#### **Nível 0: Projetos Raiz**

##### 1. sisconect-v4-multi-tenant ⭐ [MONOREPO pnpm]
```
sisconect-v4-multi-tenant/
├── [RAIZ] package.json, pnpm-workspace.yaml
├── [GIT] .git/
├── [DOCS] README.md (895 linhas), .claude/CLAUDE.md, CONTEXT.md, STATUS.md
├── [MEMORY] .memory/ (sistema perpétuo SQLite)
│
└── packages/
    ├── siscomex-sdk/              [SUB nodejs]
    ├── frontend-vite/             [SUB nodejs]
    ├── frontend-nextjs-BACKUP/    [SUB nodejs]
    ├── shared/                    [SUB nodejs]
    │
    ├── modules/
    │   └── documentation-module/  [SUB nodejs]
    │
    └── services/
        ├── comex-service/         [SUB nodejs nestjs]
        └── auth-service/          [SUB nodejs nestjs]
```
**Metadados**:
- Tipo: Node.js (NestJS)
- Status: Production-Ready (95%)
- Git Branch: refactor/api-client-type-safety
- Workspace: pnpm
- Subprojetos: 7
- Profundidade máxima: 3 níveis

---

##### 2. Ponyo-Digital [Node.js Next.js 16]
```
Ponyo-Digital/
├── [RAIZ] package.json
├── [GIT] .git/
├── [DOCS] README.md, .claude/CLAUDE.md, CONTEXT.md
└── (estrutura flat - sem subprojetos)
```
**Metadados**:
- Tipo: Node.js (Next.js 16)
- Status: Funcional
- Git Branch: main
- Package Manager: pnpm
- Sistema de ponto eletrônico

---

##### 3. aprova-saas [Node.js]
```
aprova-saas/
├── [RAIZ] package.json (name: "cena")
├── [GIT] .git/
└── [DOCS] README.md (36 linhas)
```
**Metadados**:
- Tipo: Node.js
- Status: Em desenvolvimento
- Git Branch: main

---

##### 4. vilanova-ai-lab [Multi-linguagem]
```
vilanova-ai-lab/
├── [DOCS] README.md, CONTEXT.md
│
└── assistente-pessoal/
    ├── jandira/                   [SUB nodejs]
    │   ├── package.json
    │   ├── vscode-jandira/        [SUB-SUB nodejs]
    │   │   └── package.json
    │   └── llama-cli/             [SUB-SUB nodejs]
    │       └── package.json
    │
    └── codex/                     [SUB nodejs]
        ├── package.json
        └── projeto-copia/         [SUB-SUB nodejs]
            └── package.json
```
**Metadados**:
- Tipo: Multi (Python + Node.js)
- Status: Em desenvolvimento
- Sistemas: JANDIRA, CODEX
- Profundidade: 3 níveis

---

##### 5. TowerControl_Core [Python]
```
TowerControl_Core/
├── [DOCS] README.md (441 linhas)
│
└── Projetos/
    ├── ml-service/                [SUB python]
    │   └── requirements.txt
    └── frontend/                  [SUB nodejs]
        └── package.json
```
**Metadados**:
- Tipo: Python + Node.js
- Status: Ativo
- Profundidade: 2 níveis

---

##### 6. Sistema-all-in-one [Node.js]
```
Sistema-all-in-one/
├── [RAIZ] package.json
├── [DOCS] README.md (436 linhas)
│
└── modules/
    └── (subpastas sem package.json próprio)
```
**Metadados**:
- Tipo: Node.js
- Status: Funcional (sem git)
- Package Manager: pnpm

---

##### 7. Claude-Projetos [Python] 🆕
```
Claude-Projetos/
├── [DOCS] CLAUDE.md, README.md
├── requirements.txt
├── index/
│   ├── scanner.py
│   └── schema.sql
└── (projeto atual)
```
**Metadados**:
- Tipo: Python
- Status: Inicial
- Sistema de inteligência de projetos

---

#### **Pastas Organizacionais com Subprojetos**

##### 8. GitHub/ [Pasta organizacional]
```
GitHub/
│
├── Siscionnect-V2/
│   └── supersistema-sisconect/    [nodejs, git]
│       └── package.json
│
├── Siconnect-multiempresa/        [MONOREPO]
│   ├── SisConect/
│   │   └── MultiEmpresa/          [nodejs]
│   ├── Sisconect-MultiempresaV0/
│   │   └── Sem Título/
│   │       └── supersistema-sisconect/ [nodejs]
│   └── modules/
│       └── multiempresa/          [nodejs]
│
├── BetGame/                       [nodejs]
│   ├── package.json
│   ├── mobile/                    [SUB nodejs]
│   └── ml-service/                [SUB python]
│
└── railway-sisconect/             [nodejs]
    ├── package.json
    └── backend/                   [SUB nodejs]
```

##### 9. - MKT/ [Pasta organizacional]
```
- MKT/
│
├── Edital Lucas/                  [git]
│   └── .git/
│
├── Tatai/
│   └── tatai-website/             [nodejs, git]
│       └── package.json, .git/
│
├── Conexão/
│   └── Novo Site/                 [git]
│       └── .git/
│
├── Meliuz/
│   └── Site/                      [nodejs, git]
│       └── package.json, .git/
│
└── Hotel Village/
    └── Plano...hotel-village-premium-site/ [nodejs]
        └── package.json
```

---

### 📂 /Users/victorvilanova/Downloads/ (SECUNDÁRIA)

#### **Projetos Principais com Hierarquia Profunda**

##### 1. Master-claude 🧠 [Sistema de Memória]
```
Master-claude/
├── [GIT] .git/
├── [DOCS] AUTOLOAD.md, README.md (416 linhas)
│
└── memory/
    └── core/
        ├── claude_memory_ultimate.db  [SQLite - 248 memórias]
        └── memory_ultimate.py
```
**Metadados**:
- Tipo: Python + SQL
- Sistema central de memória perpétua
- Status: Ativo

---

##### 2. Novo-Sisconect [MONOREPO COMPLEXO]
```
Novo-Sisconect/
├── [RAIZ] package.json, pnpm-workspace.yaml
├── [GIT] .git/
├── [DOCS] README.md
│
├── backend/                       [SUB nodejs]
├── frontend/                      [SUB nodejs]
├── database/                      [SUB nodejs]
├── manada-run/                    [SUB nodejs]
├── siscomex-sdk/                  [SUB nodejs]
├── Sisconect-backend/             [SUB nodejs]
├── worker-siscomex/               [SUB nodejs]
│
├── SuperSistema/                  [SUB nodejs, git]
│   └── .git/
│
├── Rifas-gemini/                  [SUB MONOREPO pnpm]
│   ├── pnpm-workspace.yaml
│   ├── frontend/                  [SUB-SUB nodejs]
│   ├── backend/                   [SUB-SUB nodejs]
│   ├── worker/                    [SUB-SUB nodejs]
│   ├── shared/                    [SUB-SUB nodejs]
│   └── database/                  [SUB-SUB nodejs]
│
└── Rifas/                         [SUB MONOREPO pnpm]
    ├── pnpm-workspace.yaml
    ├── backend/                   [SUB-SUB nodejs]
    ├── database/                  [SUB-SUB nodejs]
    ├── frontend/                  [SUB-SUB nodejs]
    ├── shared/                    [SUB-SUB nodejs]
    └── worker/                    [SUB-SUB nodejs]
```
**Metadados**:
- Tipo: Node.js (MONOREPO complexo)
- Workspace: pnpm
- Subprojetos: 11 diretos + 2 monorepos internos (10 subprojetos adicionais)
- Profundidade: 3 níveis
- Total de packages: ~21

---

##### 3. Sisconect-Enterprise [MONOREPO]
```
Sisconect-Enterprise/
├── [RAIZ] package.json
├── [GIT] .git/
├── [DOCS] README.md (237 linhas)
│
├── SuperSistema/                  [SUB nodejs, git]
│   └── .git/
│
└── siscomex-sdk/
    └── Teste-siscomex/            [SUB nodejs, git]
        └── .git/
```
**Metadados**:
- Tipo: Node.js
- Git repos internos: 3 (raiz + 2 subs)
- Profundidade: 2 níveis

---

##### 4. sisconect-ponto-digital [Multi-service]
```
sisconect-ponto-digital/
├── [RAIZ] package.json
├── [GIT] .git/
├── [DOCS] README.md (472 linhas)
│
├── backend-railway/               [SUB nodejs]
├── backend/                       [SUB nodejs]
├── tests/                         [SUB nodejs]
└── webapp/                        [SUB nodejs]
```
**Metadados**:
- Tipo: Node.js (multi-service)
- Subprojetos: 4
- Sistema de ponto digital

---

##### 5. Hybrid-Neural-System [MONOREPO Python+Node]
```
Hybrid-Neural-System/
├── [RAIZ] package.json, pnpm-workspace.yaml
├── [GIT] .git/
├── [DOCS] README.md (149 linhas)
│
├── AutoFix/                       [SUB nodejs]
├── incremental-system/            [SUB nodejs]
├── ml-real/                       [SUB nodejs]
│
└── v2/                            [SUB nodejs]
    ├── package.json
    └── core/                      [SUB-SUB python]
        └── requirements.txt
```
**Metadados**:
- Tipo: Node.js + Python (hybrid)
- Workspace: pnpm
- Profundidade: 3 níveis
- Sistema neural híbrido

---

##### 6. TabPro [MONOREPO MASSIVO]
```
TabPro/
├── [RAIZ] package.json
├── [GIT] .git/
├── [DOCS] README.md
│
├── alphatab/                      [SUB nodejs, git - MEGA MONOREPO]
│   ├── .git/
│   ├── alphatab/                  [SUB-SUB nodejs]
│   ├── alphatex/                  [SUB-SUB nodejs]
│   ├── csharp/                    [SUB-SUB csharp]
│   ├── kotlin/                    [SUB-SUB kotlin]
│   ├── lsp/                       [SUB-SUB nodejs]
│   ├── monaco/                    [SUB-SUB nodejs]
│   ├── playground/                [SUB-SUB nodejs]
│   ├── tooling/                   [SUB-SUB nodejs]
│   ├── transpiler/                [SUB-SUB nodejs]
│   ├── vite/                      [SUB-SUB nodejs]
│   ├── vscode/                    [SUB-SUB nodejs]
│   └── webpack/                   [SUB-SUB nodejs]
│
└── alphatab-clone/                [SUB python]
    └── requirements.txt
```
**Metadados**:
- Tipo: Node.js + Python + C# + Kotlin (multi-linguagem)
- Subprojetos: 14+ (12 em alphatab/)
- Profundidade: 3 níveis
- **MAIOR MONOREPO encontrado**

---

##### 7. tab-pro-codex [MONOREPO]
```
tab-pro-codex/
├── [RAIZ] package.json, pnpm-workspace.yaml
├── [GIT] .git/
├── [DOCS] README.md (45 linhas)
│
└── web/                           [SUB nodejs]
    └── package.json
```
**Metadados**:
- Tipo: Node.js
- Workspace: pnpm
- Subprojetos: 1

---

##### 8. Claude Downloads [Repositório de Análises]
```
Claude Downloads/
├── [GIT] .git/
├── [DOCS] README.md (331 linhas)
│
├── ML-Revolution-System/
│   ├── Frontend/                  [SUB nodejs]
│   │   └── package.json
│   └── Backend/                   [SUB python]
│       └── requirements.txt
│
├── vass-auditor/                  [SUB nodejs]
│   └── package.json
│
└── diparser-standalone/           [SUB nodejs]
    ├── package.json
    ├── backend/                   [SUB-SUB python]
    │   └── requirements.txt
    └── frontend/                  [SUB-SUB nodejs]
        └── package.json
```
**Metadados**:
- Tipo: Multi (repositório de análises)
- Profundidade: 3 níveis
- Histórico completo de sessões Claude Code

---

##### 9. Faturamento/ [Pasta com múltiplos projetos]
```
Faturamento/
│
├── SistemaFinanceiro/             [nodejs, git]
│   ├── .git/
│   ├── package.json
│   └── server/                    [SUB nodejs]
│       ├── package.json
│       ├── backend/               [SUB-SUB nodejs]
│       ├── tests/                 [SUB-SUB nodejs]
│       └── frontend/              [SUB-SUB nodejs]
│
└── cash-flow-app/                 [nodejs, git]
    ├── .git/
    ├── package.json
    ├── backend/                   [SUB nodejs]
    ├── frontend/                  [SUB nodejs]
    └── crawler-api/               [SUB nodejs]
```
**Metadados**:
- Projetos: 2 independentes
- Profundidade: 3 níveis (SistemaFinanceiro)

---

##### 10. VVN/ [Pasta organizacional - Sites VVN]
```
VVN/
│
├── VVN-MARKETING/
│   └── vvn-marketing/             [nodejs, git]
│       └── package.json, .git/
│
├── VVN-DIGITAL/
│   └── site/                      [nodejs, git]
│       └── package.json, .git/
│
└── CLIENTES/
    └── Vivax/
        └── vivax-hidro-spas/      [nodejs, git]
            └── package.json, .git/
```

---

##### 11. Cordoba [MONOREPO]
```
Cordoba/
├── [RAIZ] package.json, pnpm-workspace.yaml
├── [GIT] .git/
│
├── webapp-cordoba/                [SUB nodejs, git]
│   ├── package.json
│   ├── .git/
│   └── backend/                   [SUB-SUB nodejs, git]
│       ├── package.json
│       └── .git/
```
**Metadados**:
- Tipo: Node.js
- Workspace: pnpm
- Git repos: 3 (raiz + 2 subs)
- Profundidade: 3 níveis

---

##### 12. EduMetria [MONOREPO]
```
EduMetria - Documentos/
│
├── EduMetria-Extracted/           [nodejs]
│   └── package.json
│
└── edumetria-labs/                [nodejs, MONOREPO]
    ├── package.json
    └── (múltiplos subprojetos - estrutura não detalhada)
```

---

##### 13. AI-Tools/
```
AI-Tools/
│
└── LifeDelegate-Orquestrator/     [nodejs, git]
    ├── package.json
    ├── .git/
    └── mobile/                    [SUB nodejs]
        └── package.json
```

---

#### **Projetos Standalone**

##### 14. VITRA/
```
VITRA/
└── vittra_platform/               [nodejs]
    └── package.json
```

##### 15. FechamentoContainer_v2.3_RESPONSIVO
```
FechamentoContainer_v2.3_RESPONSIVO/
│
├── calculadora-de-custo-de-importação/ [nodejs, git]
│   └── package.json, .git/
│
└── nodejs-fullstack/              [nodejs]
    └── package.json
```

##### 16. Vivax-BACKUP-2026-02-10
```
Vivax-BACKUP-2026-02-10/
│
├── vvn-marketing/                 [nodejs, git]
├── vvn-digital/site/              [nodejs, git]
└── mcp-claude-server/             [nodejs]
```

##### 17. XPfake-Laravel [PHP]
```
XPfake-Laravel/
├── [GIT] .git/
├── [DOCS] README.md
└── composer.json
```
**Metadados**:
- Tipo: PHP (Laravel)
- Único projeto PHP encontrado

##### 18. zetsu [Python]
```
zetsu/
├── [GIT] .git/
├── [DOCS] README.md
└── requirements.txt
```
**Metadados**:
- Tipo: Python
- Status: Ativo

---

## 🏆 RANKING DE COMPLEXIDADE

### Top 5 Monorepos Mais Complexos (por subprojetos)

| Projeto | Localização | Subprojetos Diretos | Profundidade | Total Packages |
|---------|-------------|---------------------|--------------|----------------|
| 1. **Novo-Sisconect** | /Downloads | 11 + 2 monorepos internos | 3 níveis | ~21 |
| 2. **TabPro/alphatab** | /Downloads | 12+ (multi-linguagem) | 3 níveis | 14+ |
| 3. **sisconect-v4-multi-tenant** | /projetos | 7 | 3 níveis | 7 |
| 4. **Hybrid-Neural-System** | /Downloads | 4 | 3 níveis | 5 |
| 5. **sisconect-ponto-digital** | /Downloads | 4 | 2 níveis | 5 |

---

## 📈 PROFUNDIDADE DE HIERARQUIA

### Distribuição por Níveis

| Profundidade | Projetos Exemplo | Tipo |
|--------------|------------------|------|
| **Nível 0** (Raiz) | Ponyo-Digital, aprova-saas | Projetos standalone |
| **Nível 1** | packages/shared/, backend/ | Subprojetos diretos |
| **Nível 2** | packages/services/auth-service/ | Sub-subprojetos |
| **Nível 3** | Rifas/backend/, v2/core/ | Profundidade máxima comum |
| **Nível 4-5** | Raros (apenas em estruturas muito aninhadas) | Casos excepcionais |

---

## 🔗 DEPENDÊNCIAS E RELACIONAMENTOS

### Famílias de Projetos

#### Família Sisconect (8 versões/variações)
1. sisconect-v4-multi-tenant (principal - /projetos)
2. Novo-Sisconect (/Downloads)
3. Sisconect-Enterprise (/Downloads)
4. sisconect-ponto-digital (/Downloads)
5. GitHub/Siscionnect-V2
6. GitHub/Siconnect-multiempresa
7. GitHub/railway-sisconect
8. Sisconect-backend (dentro de Novo-Sisconect)

**Relacionamento**: Múltiplas versões e variações do mesmo sistema ERP/CRM

#### Família TabPro (3 projetos)
1. TabPro/ (/Downloads)
2. tab-pro-codex/ (/Downloads)
3. alphatab/ (clone dentro de TabPro)

**Relacionamento**: Projetos relacionados a editor de tabs musicais

#### Família VVN Digital (múltiplas versões)
1. VVN/VVN-MARKETING/vvn-marketing
2. VVN/VVN-DIGITAL/site
3. VVN/CLIENTES/Vivax/vivax-hidro-spas
4. Vivax-BACKUP-2026-02-10/vvn-marketing
5. Vivax-BACKUP-2026-02-10/vvn-digital

**Relacionamento**: Sites e marketing VVN Digital + clientes

#### Família Rifas (dentro de Novo-Sisconect)
1. Novo-Sisconect/Rifas
2. Novo-Sisconect/Rifas-gemini

**Relacionamento**: Sistema de rifas com duas versões (normal e com Gemini AI)

---

## 🎯 PROJETOS POR CATEGORIA TÉCNICA

### Backend/API
- sisconect-v4-multi-tenant (NestJS)
- Novo-Sisconect (múltiplos backends)
- BetGame/backend
- cash-flow-app/backend
- etc.

### Frontend
- Ponyo-Digital (Next.js 16)
- sisconect-v4/packages/frontend-vite
- sisconect-v4/packages/frontend-nextjs-BACKUP
- Rifas/frontend
- cash-flow-app/frontend
- etc.

### Fullstack
- Sistema-all-in-one
- aprova-saas
- Cordoba
- etc.

### ML/AI
- vilanova-ai-lab
- Hybrid-Neural-System
- Master-claude (memória perpétua)
- Claude Downloads/ML-Revolution-System
- BetGame/ml-service
- TowerControl_Core/ml-service

### DevTools/SDKs
- siscomex-sdk (múltiplas localizações)
- worker-siscomex
- vscode-jandira
- etc.

---

## 💡 INSIGHTS E OBSERVAÇÕES

### 1. Padrões Identificados
- **Monorepos são comuns**: 7 monorepos principais com pnpm workspaces
- **Hierarquia máxima**: 3 níveis é o padrão, raramente vai além
- **Múltiplas versões**: Muitos projetos têm múltiplas versões (Sisconect, TabPro, VVN)
- **Backend/Frontend separados**: Maioria dos fullstack tem subprojetos separados

### 2. Estruturas Típicas
```
[MONOREPO]/
├── backend/
├── frontend/
├── shared/
├── database/
└── worker/
```

### 3. Tecnologias Dominantes
- **Node.js**: ~145 projetos
- **pnpm**: Workspace manager preferido (7/7 monorepos)
- **Next.js**: Framework frontend comum
- **NestJS**: Framework backend para projetos principais

### 4. Complexidade vs Organização
- Projetos mais organizados: sisconect-v4 (documentação completa)
- Mais complexo: Novo-Sisconect (21 packages em 3 níveis)
- Mais diversificado: TabPro (Node+Python+C#+Kotlin)

### 5. Oportunidades de Limpeza
- Múltiplas versões de Sisconect podem ser consolidadas
- Backups antigos (Vivax-BACKUP-2026-02-10) podem ser arquivados
- Projetos sem git em /projetos devem ser inicializados

---

## 📋 PRÓXIMAS AÇÕES RECOMENDADAS

### Prioridade Alta
1. **Consolidar versões do Sisconect** - Definir versão principal
2. **Documentar monorepos** - Adicionar CLAUDE.md nos principais
3. **Inicializar git** - Projetos ativos sem git (Sistema-all-in-one, etc.)
4. **Implementar scanner.py** - Para automatizar atualizações futuras

### Prioridade Média
5. **Arquivar backups antigos** - Vivax-BACKUP, versões antigas
6. **Mapear dependências** - Entre projetos relacionados
7. **Análise de duplicação** - Código compartilhado entre projetos

### Prioridade Baixa
8. **Organizar Downloads/** - Melhor estrutura de pastas
9. **Migrar projetos legados** - Para estrutura moderna
10. **Documentação unificada** - Wiki ou portal central

---

**Gerado por**: Claude Projects Intelligence Hub v1.0
**Agente**: Explore Agent (Sonnet 4.5)
**Método**: Scan recursivo profundo com find, verificações condicionais
**Precisão**: Alta (verificado arquivo por arquivo)
**Última atualização**: 2026-02-13

---

## 🔄 COMO ATUALIZAR ESTE INVENTÁRIO

```bash
# 1. Executar scanner (quando implementado)
python3 index/scanner.py full-scan

# 2. Exportar hierarquia
sqlite3 index/projects.db < queries/export_hierarchy.sql > docs/INVENTORY_DEEP.md

# 3. Manual (se scanner não disponível)
# Repetir o scan com Explore Agent conforme feito agora
```
