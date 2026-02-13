#!/usr/bin/env python3
"""
Análise de Prioridade - Claude Projects Intelligence Hub

Calcula prioridade de projetos baseado em múltiplos fatores.

Uso:
    python3 priority.py calculate --project nome-do-projeto
    python3 priority.py list --top 10
    python3 priority.py suggest
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class PriorityAnalyzer:
    """Analisador de prioridade de projetos."""

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

    def calculate_priority(self, project_name: str) -> Dict:
        """
        Calcula prioridade de um projeto específico.

        Fatores (score 0-4, 0 = máxima prioridade):
        - Documentação completa: -1.0
        - Memory system: -0.5
        - Git recente (gradual): -1.0 a 0
        - Monorepo com subprojetos: -0.5 a -1.0
        - Framework produção: -0.5
        - Subprojetos (complexidade): -0.5
        - Duplicatas: +0.5

        Returns:
            Dicionário com score e breakdown
        """
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE name = ? AND parent_project_id IS NULL",
            (project_name,)
        )
        project = cursor.fetchone()

        if not project:
            return {'error': f'Projeto não encontrado: {project_name}'}

        project = dict(project)

        score = 4.0  # Começa com prioridade mínima, fatores reduzem
        breakdown = {}

        # 1. Documentação completa (-1.0 max)
        doc_score = 0
        if project['has_claude_md']:
            doc_score += 0.5
        if project['has_context_md']:
            doc_score += 0.25
        if project['has_readme']:
            doc_score += 0.25
        score -= doc_score
        breakdown['documentation'] = f'{doc_score:.1f} pontos (-{doc_score:.1f})'

        # 2. Sistema de memória (-0.5)
        if project['has_memory_system']:
            score -= 0.5
            breakdown['memory_system'] = 'Presente (-0.5)'
        else:
            breakdown['memory_system'] = 'Ausente (+0)'

        # 3. Atividade Git recente (gradual: -1.0 a 0)
        git_reduction = 0
        if project['git_last_commit_date']:
            try:
                last_commit = datetime.fromisoformat(project['git_last_commit_date'].split()[0])
                days_ago = (datetime.now() - last_commit).days

                if days_ago <= 3:
                    git_reduction = 1.0
                elif days_ago <= 7:
                    git_reduction = 0.8
                elif days_ago <= 14:
                    git_reduction = 0.6
                elif days_ago <= 30:
                    git_reduction = 0.4
                elif days_ago <= 90:
                    git_reduction = 0.2
                else:
                    git_reduction = 0

                score -= git_reduction
                breakdown['git_activity'] = f'{days_ago}d atrás (-{git_reduction:.1f})'
            except:
                breakdown['git_activity'] = 'Indeterminada (+0)'
        else:
            breakdown['git_activity'] = 'Sem commits (+0)'

        # 4. Monorepo com subprojetos (-0.5 a -1.0)
        subproject_count = 0
        if project['is_monorepo']:
            cursor2 = self.conn.execute(
                "SELECT COUNT(*) as cnt FROM projects WHERE parent_project_id = ?",
                (project['id'],)
            )
            subproject_count = cursor2.fetchone()['cnt']

            if subproject_count > 5:
                score -= 1.0
                breakdown['monorepo'] = f'Sim, {subproject_count} subprojetos (-1.0)'
            elif subproject_count > 0:
                score -= 0.5
                breakdown['monorepo'] = f'Sim, {subproject_count} subprojetos (-0.5)'
            else:
                score -= 0.3
                breakdown['monorepo'] = 'Sim, sem subprojetos detectados (-0.3)'
        else:
            breakdown['monorepo'] = 'Não (+0)'

        # 5. Framework de produção (-0.5)
        if project['framework'] in ['nextjs', 'nestjs', 'laravel']:
            score -= 0.5
            breakdown['framework'] = f"{project['framework']} (-0.5)"
        elif project['framework'] in ['express', 'vite']:
            score -= 0.25
            breakdown['framework'] = f"{project['framework']} (-0.25)"
        else:
            breakdown['framework'] = f"{project['framework'] or 'nenhum'} (+0)"

        # 6. Duplicatas (penalizar projetos duplicados: +0.5)
        cursor3 = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM projects WHERE name = ? AND parent_project_id IS NULL",
            (project_name,)
        )
        dup_count = cursor3.fetchone()['cnt']
        if dup_count > 1:
            score += 0.5
            breakdown['duplicates'] = f'{dup_count} cópias (+0.5)'
        else:
            breakdown['duplicates'] = 'Único (+0)'

        score = max(0, min(4, round(score, 1)))

        return {
            'project': project_name,
            'score': score,
            'breakdown': breakdown,
            'final_priority': self._score_to_label(score),
            'subproject_count': subproject_count,
        }

    def _score_to_label(self, score: float) -> str:
        """Converte score numérico em label."""
        if score <= 0.5:
            return 'P0 - MÁXIMA'
        elif score <= 1.5:
            return 'P1 - ALTA'
        elif score <= 2.5:
            return 'P2 - MÉDIA'
        elif score <= 3.5:
            return 'P3 - BAIXA'
        else:
            return 'P4 - MÍNIMA'

    def update_priority(self, project_name: str) -> bool:
        """Calcula e atualiza prioridade no banco."""
        result = self.calculate_priority(project_name)

        if 'error' in result:
            print(f"Erro: {result['error']}")
            return False

        score = result['score']
        priority = int(round(score))

        self.conn.execute(
            "UPDATE projects SET priority = ? WHERE name = ? AND parent_project_id IS NULL",
            (priority, project_name)
        )
        self.conn.commit()

        print(f"✓ {project_name}: Prioridade atualizada para {priority} ({result['final_priority']})")
        return True

    def list_projects_by_priority(self, top_n: int = None) -> List[Dict]:
        """
        Lista projetos ordenados por prioridade.

        Args:
            top_n: Número de projetos a retornar (None = todos)

        Returns:
            Lista de dicionários com informações de projeto
        """
        query = """
            SELECT
                name,
                type,
                priority,
                has_claude_md,
                has_memory_system,
                is_monorepo,
                framework,
                git_last_commit_date,
                (SELECT COUNT(*) FROM projects sub WHERE sub.parent_project_id = projects.id) as subproject_count
            FROM projects
            WHERE parent_project_id IS NULL
            ORDER BY priority ASC, name ASC
        """

        if top_n:
            query += f" LIMIT {top_n}"

        cursor = self.conn.execute(query)
        projects = [dict(row) for row in cursor.fetchall()]

        return projects

    def suggest_next_task(self) -> Optional[Dict]:
        """Sugere próximo projeto para trabalhar."""
        projects = self.list_projects_by_priority(top_n=5)

        if not projects:
            return None

        # Pegar projeto com maior prioridade (menor número)
        top_project = projects[0]

        # Verificar se há tarefas pendentes
        cursor = self.conn.execute("""
            SELECT COUNT(*) as pending_tasks
            FROM project_tasks t
            JOIN projects p ON p.id = t.project_id
            WHERE p.name = ? AND t.status = 'pending'
        """, (top_project['name'],))

        result = cursor.fetchone()
        pending_tasks = result['pending_tasks'] if result else 0

        return {
            'project': top_project['name'],
            'priority': self._score_to_label(top_project['priority']),
            'type': top_project['type'],
            'framework': top_project['framework'],
            'has_claude_md': bool(top_project['has_claude_md']),
            'is_monorepo': bool(top_project['is_monorepo']),
            'subproject_count': top_project['subproject_count'],
            'pending_tasks': pending_tasks,
            'reason': self._suggest_reason(top_project),
        }

    def _suggest_reason(self, project: Dict) -> str:
        """Gera razão para sugestão."""
        reasons = []

        if project['priority'] == 0:
            reasons.append("Prioridade máxima")

        if project['has_memory_system']:
            reasons.append("Tem sistema de memória")

        if project['is_monorepo']:
            reasons.append(f"Monorepo com {project['subproject_count']} subprojetos")

        if project['has_claude_md']:
            reasons.append("Documentação completa")

        if project['git_last_commit_date']:
            try:
                last_commit = datetime.fromisoformat(project['git_last_commit_date'].split()[0])
                days_ago = (datetime.now() - last_commit).days
                if days_ago <= 7:
                    reasons.append(f"Commit recente ({days_ago}d)")
            except:
                pass

        return "; ".join(reasons) if reasons else "Próximo na fila"

    def update_all_priorities(self) -> int:
        """Atualiza prioridade de todos os projetos raiz."""
        cursor = self.conn.execute(
            "SELECT name FROM projects WHERE parent_project_id IS NULL"
        )
        projects = cursor.fetchall()

        updated = 0
        for row in projects:
            if self.update_priority(row['name']):
                updated += 1

        return updated

    def close(self):
        """Fecha conexão com banco."""
        if self.conn:
            self.conn.close()


def main():
    """CLI principal."""
    parser = argparse.ArgumentParser(
        description='Análise de Prioridade - Claude Projects Intelligence Hub'
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando: calculate
    calc_parser = subparsers.add_parser('calculate', help='Calcular prioridade de projeto')
    calc_parser.add_argument('--project', required=True, help='Nome do projeto')
    calc_parser.add_argument('--update', action='store_true', help='Atualizar no banco')

    # Comando: list
    list_parser = subparsers.add_parser('list', help='Listar projetos por prioridade')
    list_parser.add_argument('--top', type=int, help='Número de projetos (padrão: todos)')

    # Comando: suggest
    suggest_parser = subparsers.add_parser('suggest', help='Sugerir próximo projeto')
    suggest_parser.add_argument('--output-name', action='store_true', help='Retornar apenas nome')

    # Comando: update-all
    update_all_parser = subparsers.add_parser('update-all', help='Atualizar prioridade de todos')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    analyzer = PriorityAnalyzer()

    try:
        if args.command == 'calculate':
            result = analyzer.calculate_priority(args.project)

            if 'error' in result:
                print(f"Erro: {result['error']}")
                exit(1)

            print(f"\n{'='*60}")
            print(f"Projeto: {result['project']}")
            print(f"Score: {result['score']} ({result['final_priority']})")
            print(f"{'='*60}")
            print("\nBreakdown:")
            for factor, value in result['breakdown'].items():
                print(f"  {factor}: {value}")
            print(f"{'='*60}\n")

            if args.update:
                analyzer.update_priority(args.project)

        elif args.command == 'list':
            projects = analyzer.list_projects_by_priority(top_n=args.top)

            print(f"\n{'='*60}")
            print(f"PROJETOS POR PRIORIDADE")
            print(f"{'='*60}\n")

            for i, proj in enumerate(projects, 1):
                pri_label = analyzer._score_to_label(proj['priority'])
                monorepo_marker = " [MONOREPO]" if proj['is_monorepo'] else ""
                doc_marker = " 📄" if proj['has_claude_md'] else ""
                memory_marker = " 🧠" if proj['has_memory_system'] else ""

                print(f"{i}. {proj['name']}{monorepo_marker}{doc_marker}{memory_marker}")
                print(f"   Prioridade: {pri_label} ({proj['priority']})")
                print(f"   Tipo: {proj['type']}")
                if proj['framework']:
                    print(f"   Framework: {proj['framework']}")
                if proj['subproject_count'] > 0:
                    print(f"   Subprojetos: {proj['subproject_count']}")
                print()

            print(f"{'='*60}\n")

        elif args.command == 'suggest':
            suggestion = analyzer.suggest_next_task()

            if not suggestion:
                print("Nenhum projeto encontrado.")
                exit(1)

            if args.output_name:
                print(suggestion['project'])
            else:
                print(f"\n{'='*60}")
                print(f"PRÓXIMO PROJETO SUGERIDO")
                print(f"{'='*60}\n")
                print(f"Projeto: {suggestion['project']}")
                print(f"Prioridade: {suggestion['priority']}")
                print(f"Tipo: {suggestion['type']}")
                if suggestion['framework']:
                    print(f"Framework: {suggestion['framework']}")
                if suggestion['is_monorepo']:
                    print(f"Monorepo: {suggestion['subproject_count']} subprojetos")
                if suggestion['pending_tasks'] > 0:
                    print(f"Tarefas pendentes: {suggestion['pending_tasks']}")
                print(f"\nRazão: {suggestion['reason']}")
                print(f"{'='*60}\n")

        elif args.command == 'update-all':
            print("Atualizando prioridade de todos os projetos...")
            updated = analyzer.update_all_priorities()
            print(f"\n✓ {updated} projetos atualizados\n")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
