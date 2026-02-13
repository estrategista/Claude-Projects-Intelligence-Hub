#!/usr/bin/env python3
"""
Integração com Memory Ultimate - Claude Projects Intelligence Hub

Bridge para o sistema Memory Ultimate V3.0 em /Downloads/Master-claude/memory/core/

Uso:
    python3 integration.py search "query" --limit 10
    python3 integration.py checkpoint "tarefa" "status" "próximo"
    python3 integration.py get-last-state --project nome-do-projeto
"""

import subprocess
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

class MemoryIntegration:
    """Bridge para Memory Ultimate V3.0."""

    MEMORY_PATH = Path("/Users/victorvilanova/Downloads/Master-claude/memory/core")
    MEMORY_SCRIPT = "memory_ultimate.py"

    def __init__(self):
        """Inicializa integração."""
        self.memory_dir = self.MEMORY_PATH
        self.memory_script = self.memory_dir / self.MEMORY_SCRIPT

        if not self.memory_dir.exists():
            raise FileNotFoundError(
                f"Memory Ultimate não encontrado: {self.memory_dir}\n"
                f"Verifique se o path está correto no CLAUDE.md global"
            )

        if not self.memory_script.exists():
            raise FileNotFoundError(
                f"Script não encontrado: {self.memory_script}"
            )

    def _run_memory_command(self, args: List[str]) -> Dict:
        """
        Executa comando no Memory Ultimate.

        Args:
            args: Lista de argumentos para memory_ultimate.py

        Returns:
            Resultado do comando
        """
        try:
            result = subprocess.run(
                ['python3', str(self.memory_script)] + args,
                cwd=str(self.memory_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr or result.stdout,
                }

            return {
                'success': True,
                'output': result.stdout,
                'raw': result,
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout ao executar comando (30s)',
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def search(self, query: str, limit: int = 5) -> Dict:
        """
        Busca memórias relacionadas.

        Args:
            query: Texto de busca
            limit: Número máximo de resultados

        Returns:
            Resultados da busca
        """
        result = self._run_memory_command([
            'search',
            query,
            '--limit', str(limit)
        ])

        return result

    def checkpoint(self, task: str, status: str, next_step: str) -> Dict:
        """
        Cria checkpoint de progresso.

        Args:
            task: Nome da tarefa/projeto
            status: Status atual
            next_step: Próximo passo

        Returns:
            Resultado do checkpoint
        """
        result = self._run_memory_command([
            'checkpoint',
            task,
            status,
            next_step
        ])

        return result

    def remember(self, category: str, content: str) -> Dict:
        """
        Adiciona nova memória.

        Args:
            category: Categoria da memória
            content: Conteúdo da memória

        Returns:
            Resultado da operação
        """
        result = self._run_memory_command([
            'remember',
            category,
            content
        ])

        return result

    def stats(self) -> Dict:
        """Retorna estatísticas do banco de memória."""
        result = self._run_memory_command(['stats'])
        return result

    def health(self) -> Dict:
        """Verifica saúde do sistema de memória."""
        result = self._run_memory_command(['health'])
        return result

    def get_last_state(self, project: str) -> Dict:
        """
        Recupera último estado de um projeto.

        Args:
            project: Nome do projeto

        Returns:
            Último estado encontrado
        """
        # Buscar checkpoints do projeto
        result = self.search(f"{project} checkpoint", limit=3)

        if not result['success']:
            return result

        return {
            'success': True,
            'project': project,
            'output': result['output'],
        }


def main():
    """CLI principal."""
    parser = argparse.ArgumentParser(
        description='Integração Memory Ultimate - Claude Projects Intelligence Hub'
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando: search
    search_parser = subparsers.add_parser('search', help='Buscar memórias')
    search_parser.add_argument('query', help='Texto de busca')
    search_parser.add_argument('--limit', type=int, default=5, help='Número de resultados')

    # Comando: checkpoint
    checkpoint_parser = subparsers.add_parser('checkpoint', help='Criar checkpoint')
    checkpoint_parser.add_argument('task', help='Nome da tarefa/projeto')
    checkpoint_parser.add_argument('status', help='Status atual')
    checkpoint_parser.add_argument('next_step', help='Próximo passo')

    # Comando: remember
    remember_parser = subparsers.add_parser('remember', help='Adicionar memória')
    remember_parser.add_argument('category', help='Categoria')
    remember_parser.add_argument('content', help='Conteúdo')

    # Comando: stats
    stats_parser = subparsers.add_parser('stats', help='Estatísticas')

    # Comando: health
    health_parser = subparsers.add_parser('health', help='Health check')

    # Comando: get-last-state
    state_parser = subparsers.add_parser('get-last-state', help='Recuperar último estado')
    state_parser.add_argument('--project', required=True, help='Nome do projeto')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        integration = MemoryIntegration()

        if args.command == 'search':
            result = integration.search(args.query, args.limit)

        elif args.command == 'checkpoint':
            result = integration.checkpoint(args.task, args.status, args.next_step)

        elif args.command == 'remember':
            result = integration.remember(args.category, args.content)

        elif args.command == 'stats':
            result = integration.stats()

        elif args.command == 'health':
            result = integration.health()

        elif args.command == 'get-last-state':
            result = integration.get_last_state(args.project)

        # Imprimir resultado
        if result['success']:
            print(result['output'])
        else:
            print(f"Erro: {result['error']}", file=sys.stderr)
            exit(1)

    except FileNotFoundError as e:
        print(f"Erro: {e}", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
