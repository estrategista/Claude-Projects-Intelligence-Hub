#!/bin/bash
# Setup inicial do Claude Projects Intelligence Hub

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║    CLAUDE PROJECTS INTELLIGENCE HUB - SETUP INICIAL          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Verificar Python 3
echo "📦 Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION encontrado"
echo ""

# 2. Instalar dependências
echo "📦 Instalando dependências Python..."
pip3 install -r requirements.txt
echo "✓ Dependências instaladas"
echo ""

# 3. Criar banco de dados SQLite
echo "🗄️  Inicializando banco de dados..."
if [ -f "index/projects.db" ]; then
    echo "⚠️  Banco de dados já existe: index/projects.db"
    read -p "Deseja recriar? (isso apagará todos os dados) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f index/projects.db
        echo "✓ Banco antigo removido"
    else
        echo "✓ Mantendo banco existente"
    fi
fi

if [ ! -f "index/projects.db" ]; then
    sqlite3 index/projects.db < index/schema.sql
    echo "✓ Banco de dados criado: index/projects.db"
fi
echo ""

# 4. Criar estrutura de pastas
echo "📁 Criando estrutura de pastas..."
mkdir -p docs/reports
mkdir -p scripts
mkdir -p analysis
mkdir -p memory
mkdir -p dashboard
echo "✓ Estrutura criada"
echo ""

# 5. Tornar scripts executáveis
echo "🔧 Configurando permissões..."
chmod +x index/scanner.py
[ -f scripts/scan-all.sh ] && chmod +x scripts/scan-all.sh
[ -f scripts/update-index.sh ] && chmod +x scripts/update-index.sh
[ -f scripts/get-next-task.sh ] && chmod +x scripts/get-next-task.sh
echo "✓ Permissões configuradas"
echo ""

# 6. Verificar localização da memória central
echo "🧠 Verificando Memory Ultimate V3.0..."
MEMORY_PATH="/Users/victorvilanova/Downloads/Master-claude/memory/core"
if [ -d "$MEMORY_PATH" ]; then
    if [ -f "$MEMORY_PATH/claude_memory_ultimate.db" ]; then
        echo "✓ Memory Ultimate encontrado: $MEMORY_PATH"
    else
        echo "⚠️  Diretório existe mas banco não encontrado"
    fi
else
    echo "⚠️  Memory Ultimate não encontrado em: $MEMORY_PATH"
    echo "   Verifique se o path está correto no CLAUDE.md global"
fi
echo ""

# 7. Status final
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    SETUP CONCLUÍDO!                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Implementar scanner:"
echo "   vim index/scanner.py"
echo ""
echo "2. Fazer primeiro scan (quando scanner estiver pronto):"
echo "   python3 index/scanner.py full-scan"
echo ""
echo "3. Ver inventário atualizado:"
echo "   cat docs/INVENTORY.md"
echo ""
echo "4. Ler documentação completa:"
echo "   cat CLAUDE.md"
echo ""
echo "✨ Sistema pronto para desenvolvimento!"
