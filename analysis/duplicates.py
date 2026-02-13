#!/usr/bin/env python3
"""
Análise de Duplicatas - Claude Projects Intelligence Hub

Detecta projetos duplicados, forks e versões antigas.

Uso:
    python3 duplicates.py find
    python3 duplicates.py suggest-consolidation
    python3 duplicates.py report
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import json
import os


class DuplicateAnalyzer:
    """Analisador de projetos duplicados e redundantes."""

    # Sufixos que indicam cópias/versões
    COPY_SUFFIXES = ['-temp', '-backup', '-old', '-bak', '-copy', '-v2', '-v3', '-v4',
                     '-intel', '-new', '-novo', '-antigo', '-legacy']

    # Padrões de nomes que indicam relação
    RELATION_PATTERNS = [
        ('sisconect', 'ERP/CRM/COMEX'),
        ('ponyo', 'Ponto Eletrônico'),
        ('rifa', 'Sistema de Rifas'),
        ('fechamento', 'Fechamento Fiscal'),
        ('cordoba', 'Projeto Cordoba'),
        ('tab-pro', 'Tab Pro'),
        ('bill-of-lading', 'Bill of Lading'),
        ('vilanova-ai', 'AI Lab'),
    ]

    def __init__(self, db_path: str = None):
        if db_path is None:
            script_dir = Path(__file__).parent.parent
            db_path = script_dir / "index" / "projects.db"

        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def find_duplicates(self) -> List[Dict]:
        """
        Encontra grupos de projetos duplicados.

        Critérios:
        1. Mesmo nome em localizações diferentes
        2. Nomes com sufixos de cópia (-temp, -backup, etc.)
        3. Mesmo git remote URL

        Returns:
            Lista de grupos de duplicatas
        """
        groups = []

        # 1. Projetos com exatamente o mesmo nome
        groups.extend(self._find_same_name())

        # 2. Projetos com nomes similares (sufixos de cópia)
        groups.extend(self._find_similar_names())

        # 3. Projetos com mesmo git remote
        groups.extend(self._find_same_remote())

        # Deduplicar grupos
        return self._deduplicate_groups(groups)

    def _find_same_name(self) -> List[Dict]:
        """Encontra projetos com o mesmo nome em localizações diferentes."""
        cursor = self.conn.execute("""
            SELECT name, COUNT(*) as cnt,
                   GROUP_CONCAT(path, '||') as paths,
                   GROUP_CONCAT(id, ',') as ids
            FROM projects
            WHERE parent_project_id IS NULL
            GROUP BY name
            HAVING cnt > 1
            ORDER BY cnt DESC
        """)

        groups = []
        for row in cursor.fetchall():
            row = dict(row)
            paths = row['paths'].split('||')
            ids = [int(x) for x in row['ids'].split(',')]

            # Determinar qual é o "principal" (mais recente, mais documentado)
            members = self._get_projects_by_ids(ids)
            primary = self._select_primary(members)

            groups.append({
                'type': 'same_name',
                'name': row['name'],
                'count': row['cnt'],
                'members': members,
                'primary_id': primary['id'] if primary else None,
                'action': 'consolidar - manter o mais completo',
            })

        return groups

    def _find_similar_names(self) -> List[Dict]:
        """Encontra projetos com nomes que indicam cópia/versão."""
        cursor = self.conn.execute(
            "SELECT id, name, path, has_git, git_last_commit_date, has_claude_md "
            "FROM projects WHERE parent_project_id IS NULL ORDER BY name"
        )
        projects = [dict(row) for row in cursor.fetchall()]

        groups = []
        seen = set()

        for p in projects:
            if p['id'] in seen:
                continue

            base_name = p['name'].lower()
            related = [p]

            for suffix in self.COPY_SUFFIXES:
                if base_name.endswith(suffix):
                    base_name = base_name[:base_name.rfind(suffix)]
                    break

            for other in projects:
                if other['id'] == p['id'] or other['id'] in seen:
                    continue

                other_name = other['name'].lower()
                other_base = other_name
                for suffix in self.COPY_SUFFIXES:
                    if other_name.endswith(suffix):
                        other_base = other_name[:other_name.rfind(suffix)]
                        break

                if base_name == other_base and base_name != other_name:
                    related.append(other)

            if len(related) > 1:
                for r in related:
                    seen.add(r['id'])

                primary = self._select_primary(related)
                groups.append({
                    'type': 'similar_name',
                    'name': base_name,
                    'count': len(related),
                    'members': related,
                    'primary_id': primary['id'] if primary else None,
                    'action': 'verificar se são versões diferentes e consolidar',
                })

        return groups

    def _find_same_remote(self) -> List[Dict]:
        """Encontra projetos que apontam para o mesmo repositório remoto."""
        cursor = self.conn.execute("""
            SELECT git_remote, COUNT(*) as cnt,
                   GROUP_CONCAT(id, ',') as ids
            FROM projects
            WHERE git_remote IS NOT NULL
              AND git_remote != ''
              AND parent_project_id IS NULL
            GROUP BY git_remote
            HAVING cnt > 1
        """)

        groups = []
        for row in cursor.fetchall():
            row = dict(row)
            ids = [int(x) for x in row['ids'].split(',')]
            members = self._get_projects_by_ids(ids)

            primary = self._select_primary(members)
            groups.append({
                'type': 'same_remote',
                'name': row['git_remote'].split('/')[-1].replace('.git', ''),
                'count': row['cnt'],
                'members': members,
                'primary_id': primary['id'] if primary else None,
                'action': 'clones do mesmo repositório - manter apenas um',
            })

        return groups

    def _get_projects_by_ids(self, ids: List[int]) -> List[Dict]:
        """Busca projetos por lista de IDs."""
        placeholders = ','.join(['?' for _ in ids])
        cursor = self.conn.execute(
            f"SELECT id, name, path, has_git, git_last_commit_date, has_claude_md, "
            f"has_memory_system, is_monorepo, framework, type "
            f"FROM projects WHERE id IN ({placeholders})", ids
        )
        return [dict(row) for row in cursor.fetchall()]

    def _select_primary(self, members: List[Dict]) -> Dict:
        """Seleciona o projeto principal de um grupo (mais completo/recente)."""
        if not members:
            return None

        def score(p):
            s = 0
            if p.get('has_claude_md'):
                s += 3
            if p.get('has_memory_system'):
                s += 2
            if p.get('is_monorepo'):
                s += 1
            if p.get('framework'):
                s += 1
            if p.get('git_last_commit_date'):
                try:
                    dt = datetime.fromisoformat(p['git_last_commit_date'].split()[0])
                    days = (datetime.now() - dt).days
                    if days <= 30:
                        s += 3
                    elif days <= 90:
                        s += 2
                    elif days <= 180:
                        s += 1
                except:
                    pass
            return s

        return max(members, key=score)

    def _deduplicate_groups(self, groups: List[Dict]) -> List[Dict]:
        """Remove grupos duplicados (mesmo conjunto de projetos)."""
        seen_sets = []
        unique = []

        for g in groups:
            member_ids = frozenset(m['id'] for m in g['members'])
            if member_ids not in seen_sets:
                seen_sets.append(member_ids)
                unique.append(g)

        return unique

    def suggest_consolidation(self) -> List[Dict]:
        """Sugere ações de consolidação para cada grupo de duplicatas."""
        groups = self.find_duplicates()
        suggestions = []

        for group in groups:
            primary = next((m for m in group['members'] if m['id'] == group['primary_id']), None)
            others = [m for m in group['members'] if m['id'] != group['primary_id']]

            suggestion = {
                'group': group['name'],
                'type': group['type'],
                'keep': {
                    'name': primary['name'] if primary else 'N/A',
                    'path': primary['path'] if primary else 'N/A',
                },
                'archive': [{'name': o['name'], 'path': o['path']} for o in others],
                'action': group['action'],
                'disk_savings_estimate': self._estimate_disk_savings(others),
            }
            suggestions.append(suggestion)

        return suggestions

    def _estimate_disk_savings(self, projects: List[Dict]) -> str:
        """Estima economia de disco ao consolidar."""
        total_size = 0
        for p in projects:
            path = Path(p['path'])
            if path.exists():
                try:
                    for f in path.rglob('*'):
                        if f.is_file() and 'node_modules' not in str(f):
                            total_size += f.stat().st_size
                except:
                    pass

        if total_size > 1_000_000_000:
            return f"{total_size / 1_000_000_000:.1f} GB"
        elif total_size > 1_000_000:
            return f"{total_size / 1_000_000:.1f} MB"
        elif total_size > 1_000:
            return f"{total_size / 1_000:.1f} KB"
        return "desconhecido"

    def generate_report(self) -> str:
        """Gera relatório Markdown de duplicatas."""
        groups = self.find_duplicates()

        lines = [
            "# Relatório de Duplicatas",
            f"\n**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Grupos encontrados**: {len(groups)}",
            "",
        ]

        if not groups:
            lines.append("Nenhuma duplicata encontrada.")
            return "\n".join(lines)

        total_dups = sum(g['count'] - 1 for g in groups)
        lines.append(f"**Total de projetos redundantes**: {total_dups}")
        lines.append("")

        for i, group in enumerate(groups, 1):
            lines.append(f"## {i}. {group['name']} ({group['type']})")
            lines.append(f"**Projetos**: {group['count']}")
            lines.append(f"**Ação**: {group['action']}")
            lines.append("")

            for m in group['members']:
                is_primary = " **(MANTER)**" if m['id'] == group['primary_id'] else " _(candidato a remoção)_"
                lines.append(f"- `{m['path']}`{is_primary}")

            lines.append("")

        return "\n".join(lines)

    def close(self):
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Análise de Duplicatas - Claude Projects Intelligence Hub'
    )

    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('find', help='Encontrar duplicatas')
    subparsers.add_parser('suggest-consolidation', help='Sugerir consolidação')
    subparsers.add_parser('report', help='Gerar relatório Markdown')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    analyzer = DuplicateAnalyzer()

    try:
        if args.command == 'find':
            groups = analyzer.find_duplicates()
            print(f"\n{'='*60}")
            print(f"DUPLICATAS ENCONTRADAS: {len(groups)} grupos")
            print(f"{'='*60}\n")

            for i, group in enumerate(groups, 1):
                print(f"{i}. {group['name']} ({group['type']})")
                print(f"   Projetos: {group['count']}")
                for m in group['members']:
                    marker = " [PRINCIPAL]" if m['id'] == group['primary_id'] else ""
                    print(f"   - {m['name']} ({m['path']}){marker}")
                print()

        elif args.command == 'suggest-consolidation':
            suggestions = analyzer.suggest_consolidation()
            print(f"\n{'='*60}")
            print(f"SUGESTÕES DE CONSOLIDAÇÃO")
            print(f"{'='*60}\n")

            for s in suggestions:
                print(f"Grupo: {s['group']} ({s['type']})")
                print(f"  Manter: {s['keep']['name']} ({s['keep']['path']})")
                for a in s['archive']:
                    print(f"  Arquivar: {a['name']} ({a['path']})")
                print(f"  Economia estimada: {s['disk_savings_estimate']}")
                print(f"  Ação: {s['action']}")
                print()

        elif args.command == 'report':
            print(analyzer.generate_report())

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
