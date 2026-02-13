#!/bin/bash
# Script para sugerir próxima tarefa - Claude Projects Intelligence Hub

set -e

# Navegar para diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              PRÓXIMA TAREFA SUGERIDA                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Sugerir próximo projeto
python3 analysis/priority.py suggest

# Obter nome do projeto
PROJECT_NAME=$(python3 analysis/priority.py suggest --output-name 2>/dev/null)

if [ -n "$PROJECT_NAME" ]; then
    echo ""
    echo "🧠 Recuperando contexto da memória..."
    echo ""

    # Tentar recuperar último estado da memória
    python3 memory/integration.py get-last-state --project "$PROJECT_NAME" 2>/dev/null || true

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  COMANDOS ÚTEIS                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Ver detalhes do projeto:"
    echo "  sqlite3 index/projects.db \"SELECT * FROM projects WHERE name='$PROJECT_NAME'\""
    echo ""
    echo "Navegar para projeto:"
    echo "  cd \$(sqlite3 index/projects.db \"SELECT path FROM projects WHERE name='$PROJECT_NAME' LIMIT 1\")"
    echo ""
    echo "Criar checkpoint após trabalhar:"
    echo "  python3 memory/integration.py checkpoint '$PROJECT_NAME' 'status' 'próximo passo'"
    echo ""
fi

echo ""
