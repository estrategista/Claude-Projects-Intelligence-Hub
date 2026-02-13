#!/usr/bin/env python3
"""
Análise de Status - Claude Projects Intelligence Hub

Determina status de projetos: active, maintained, legacy, archived.

Uso:
    python3 status.py check --name nome-do-projeto
    python3 status.py analyze-all
    python3 status.py suggest-archive
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import json

class StatusAnalyzer:
    """Analisador de status de projetos."""

    def __init__(self, db_path: str = None):
        """
        Inicializa o analisador.

        Args:
            db_path: Path para o banco de dados SQLite.
        """
        if db_path is None:
            script_dir = Path(__file__).parent.parent
            db_path = script_dir / "index" / "projects.db"

        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def analyze_status(self, project_name: str) -> Dict:
        """
        Analisa e determina status de um projeto.

        Status possíveis:
        - active: Em desenvolvimento ativo (commits recentes)
        - maintained: Funcional, sem mudanças recentes
        - legacy: Código antigo, sem git ou documentação
        - archived: Marcado para arquivamento

        Returns:
            Dicionário com status e razões
        """
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE name = ?",
            (project_name,)
        )
        project = cursor.fetchone()

        if not project:
            return {'error': f'Projeto não encontrado: {project_name}'}

        project = dict(project)

        # Determinar status
        status = 'unknown'
        reasons = []

        # 1. Active: commits nos últimos 30 dias
        if project['has_git'] and project['git_last_commit_date']:
            try:
                last_commit = datetime.fromisoformat(project['git_last_commit_date'].split()[0])
                days_ago = (datetime.now() - last_commit).days

                if days_ago <= 30:
                    status = 'active'
                    reasons.append(f'Commit recente ({days_ago} dias atrás)')
                elif days_ago <= 180:  # 6 meses
                    status = 'maintained'
                    reasons.append(f'Commit há {days_ago} dias')
                else:
                    status = 'legacy'
                    reasons.append(f'Última mudança há {days_ago} dias')
            except:
                status = 'legacy'
                reasons.append('Data de commit inválida')

        # 2. Se não tem git mas tem documentação moderna
        elif not project['has_git']:
            if project['has_claude_md'] or project['has_context_md']:
                status = 'maintained'
                reasons.append('Sem git, mas documentado')
            else:
                status = 'legacy'
                reasons.append('Sem git e sem documentação')

        # 3. Fatores adicionais
        if project['has_memory_system']:
            reasons.append('Tem sistema de memória (provavelmente ativo)')
            if status == 'legacy':
                status = 'maintained'

        if project['is_monorepo']:
            reasons.append(f'Monorepo (projeto complexo)')

        if project['type'] == 'storage':
            status = 'archived'
            reasons.append('Pasta de armazenamento/documentos')

        return {
            'project': project_name,
            'current_status': project['status'],
            'suggested_status': status,
            'reasons': reasons,
            'should_update': project['status'] != status,
        }

    def update_status(self, project_name: str) -> bool:
        """Analisa e atualiza status de um projeto."""
        result = self.analyze_status(project_name)

        if 'error' in result:
            print(f"Erro: {result['error']}")
            return False

        if not result['should_update']:
            print(f"✓ {project_name}: Status já correto ({result['current_status']})")
            return True

        self.conn.execute(
            "UPDATE projects SET status = ? WHERE name = ?",
            (result['suggested_status'], project_name)
        )
        self.conn.commit()

        print(f"✓ {project_name}: Status atualizado de '{result['current_status']}' para '{result['suggested_status']}'")
        return True

    def analyze_all(self) -> Dict:
        """Analisa status de todos os projetos."""
        cursor = self.conn.execute("SELECT name FROM projects")
        projects = [row['name'] for row in cursor.fetchall()]

        results = {
            'total': len(projects),
            'updated': 0,
            'unchanged': 0,
            'errors': 0,
            'status_counts': {
                'active': 0,
                'maintained': 0,
                'legacy': 0,
                'archived': 0,
                'unknown': 0,
            }
        }

        for project_name in projects:
            result = self.analyze_status(project_name)

            if 'error' in result:
                results['errors'] += 1
                continue

            status = result['suggested_status']
            results['status_counts'][status] += 1

            if result['should_update']:
                self.update_status(project_name)
                results['updated'] += 1
            else:
                results['unchanged'] += 1

        return results

    def suggest_archive(self) -> List[Dict]:
        """Sugere projetos para arquivamento."""
        cursor = self.conn.execute("""
            SELECT
                name,
                type,
                has_git,
                git_last_commit_date,
                has_readme,
                has_claude_md,
                parent_project_id
            FROM projects
            WHERE status = 'legacy'
              AND parent_project_id IS NULL
            ORDER BY name
        """)

        candidates = []

        for row in cursor.fetchall():
            project = dict(row)

            # Calcular score de arquivamento (quanto maior, mais candidato)
            archive_score = 0
            reasons = []

            # 1. Sem git
            if not project['has_git']:
                archive_score += 3
                reasons.append('Sem controle de versão')

            # 2. Commit muito antigo
            if project['git_last_commit_date']:
                try:
                    last_commit = datetime.fromisoformat(project['git_last_commit_date'].split()[0])
                    days_ago = (datetime.now() - last_commit).days

                    if days_ago > 365:
                        archive_score += 2
                        reasons.append(f'Última mudança há {days_ago} dias')
                except:
                    pass

            # 3. Sem documentação
            if not project['has_readme'] and not project['has_claude_md']:
                archive_score += 1
                reasons.append('Sem documentação')

            # 4. Tipo storage
            if project['type'] == 'storage':
                archive_score += 2
                reasons.append('Tipo: armazenamento')

            if archive_score >= 3:
                candidates.append({
                    'name': project['name'],
                    'score': archive_score,
                    'reasons': reasons,
                })

        # Ordenar por score (maior primeiro)
        candidates.sort(key=lambda x: x['score'], reverse=True)

        return candidates

    def close(self):
        """Fecha conexão com banco."""
        if self.conn:
            self.conn.close()


def main():
    """CLI principal."""
    parser = argparse.ArgumentParser(
        description='Análise de Status - Claude Projects Intelligence Hub'
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando: check
    check_parser = subparsers.add_parser('check', help='Verificar status de projeto')
    check_parser.add_argument('--name', required=True, help='Nome do projeto')
    check_parser.add_argument('--update', action='store_true', help='Atualizar status')

    # Comando: analyze-all
    analyze_parser = subparsers.add_parser('analyze-all', help='Analisar todos os projetos')

    # Comando: suggest-archive
    archive_parser = subparsers.add_parser('suggest-archive', help='Sugerir projetos para arquivar')
    archive_parser.add_argument('--min-score', type=int, default=3, help='Score mínimo')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    analyzer = StatusAnalyzer()

    try:
        if args.command == 'check':
            result = analyzer.analyze_status(args.name)

            if 'error' in result:
                print(f"Erro: {result['error']}")
                exit(1)

            print(f"\n{'='*60}")
            print(f"Projeto: {result['project']}")
            print(f"{'='*60}")
            print(f"Status atual: {result['current_status']}")
            print(f"Status sugerido: {result['suggested_status']}")
            print(f"\nRazões:")
            for reason in result['reasons']:
                print(f"  - {reason}")
            print(f"{'='*60}\n")

            if args.update and result['should_update']:
                analyzer.update_status(args.name)

        elif args.command == 'analyze-all':
            print("Analisando status de todos os projetos...\n")
            results = analyzer.analyze_all()

            print(f"\n{'='*60}")
            print("ANÁLISE COMPLETA")
            print(f"{'='*60}")
            print(f"Total de projetos: {results['total']}")
            print(f"Atualizados: {results['updated']}")
            print(f"Sem mudanças: {results['unchanged']}")
            print(f"Erros: {results['errors']}")
            print(f"\nDistribuição por status:")
            for status, count in results['status_counts'].items():
                print(f"  {status}: {count}")
            print(f"{'='*60}\n")

        elif args.command == 'suggest-archive':
            candidates = analyzer.suggest_archive()

            print(f"\n{'='*60}")
            print(f"CANDIDATOS A ARQUIVAMENTO")
            print(f"{'='*60}\n")

            if not candidates:
                print("Nenhum candidato encontrado.\n")
            else:
                for i, cand in enumerate(candidates, 1):
                    if cand['score'] >= args.min_score:
                        print(f"{i}. {cand['name']} (score: {cand['score']})")
                        for reason in cand['reasons']:
                            print(f"   - {reason}")
                        print()

            print(f"{'='*60}\n")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
