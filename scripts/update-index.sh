#!/bin/bash
# Script de atualização incremental - Claude Projects Intelligence Hub
# Atualiza apenas projetos modificados recentemente

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      CLAUDE PROJECTS - ATUALIZAÇÃO INCREMENTAL              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Navegar para diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Parâmetros
DAYS=${1:-7}  # Padrão: últimos 7 dias

echo "🔍 Atualizando projetos modificados nos últimos $DAYS dias..."
echo ""

# Buscar projetos git modificados nos últimos N dias
LOCATIONS=(
    "/Users/victorvilanova/projetos/"
    "/Users/victorvilanova/Downloads/"
)

UPDATED=0

for LOCATION in "${LOCATIONS[@]}"; do
    if [ ! -d "$LOCATION" ]; then
        echo "⚠️  Localização não existe: $LOCATION"
        continue
    fi

    echo "📂 Escaneando: $LOCATION"

    # Encontrar repositórios git com commits recentes
    while IFS= read -r -d '' GIT_DIR; do
        PROJECT_DIR_PATH="$(dirname "$GIT_DIR")"
        PROJECT_NAME="$(basename "$PROJECT_DIR_PATH")"

        # Verificar se há commits nos últimos N dias
        cd "$PROJECT_DIR_PATH"
        RECENT_COMMITS=$(git log --since="$DAYS days ago" --oneline 2>/dev/null | wc -l)

        if [ "$RECENT_COMMITS" -gt 0 ]; then
            echo "  ✓ $PROJECT_NAME ($RECENT_COMMITS commits)"

            # Atualizar no banco
            cd "$PROJECT_DIR"
            python3 index/scanner.py update --path "$PROJECT_DIR_PATH" 2>/dev/null
            UPDATED=$((UPDATED + 1))
        fi
    done < <(find "$LOCATION" -name ".git" -type d -maxdepth 5 -print0 2>/dev/null)
done

echo ""
echo "✅ Atualização completa!"
echo "   Projetos atualizados: $UPDATED"
echo ""

# Atualizar prioridades apenas dos projetos atualizados
if [ $UPDATED -gt 0 ]; then
    echo "📊 Recalculando prioridades..."
    python3 analysis/priority.py update-all
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ATUALIZAÇÃO INCREMENTAL COMPLETA                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
