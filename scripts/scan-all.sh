#!/bin/bash
# Script de scan completo - Claude Projects Intelligence Hub
# Escaneia todas as localizações e atualiza INVENTORY.md

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║    CLAUDE PROJECTS INTELLIGENCE HUB - SCAN COMPLETO         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Navegar para diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "📁 Diretório do projeto: $PROJECT_DIR"
echo ""

# Verificar se scanner existe
if [ ! -f "index/scanner.py" ]; then
    echo "❌ Erro: scanner.py não encontrado!"
    echo "   Esperado em: index/scanner.py"
    exit 1
fi

# Executar scan completo
echo "🔍 Iniciando scan recursivo completo..."
echo "   Localizações:"
echo "   - /Users/victorvilanova/projetos/"
echo "   - /Users/victorvilanova/Downloads/"
echo ""

python3 index/scanner.py full-scan --verbose

echo ""
echo "✅ Scan completo finalizado!"
echo ""

# Atualizar prioridades
echo "📊 Atualizando prioridades de todos os projetos..."
python3 analysis/priority.py update-all

echo ""
echo "📈 Analisando status de todos os projetos..."
python3 analysis/status.py analyze-all

echo ""

# Gerar dashboard
echo "📋 Gerando relatório..."
REPORT_FILE="docs/reports/status-$(date +%Y-%m-%d).md"
python3 dashboard/cli.py --export-md > "$REPORT_FILE"

echo "✅ Relatório gerado: $REPORT_FILE"
echo ""

# Exibir dashboard
echo "📊 Dashboard:"
python3 dashboard/cli.py

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    SCAN COMPLETO!                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Próximos passos:"
echo "  - Ver relatório: cat $REPORT_FILE"
echo "  - Ver banco: sqlite3 index/projects.db"
echo "  - Próxima tarefa: ./scripts/get-next-task.sh"
echo ""
