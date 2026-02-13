#!/usr/bin/env python3
"""
Dashboard CLI - Claude Projects Intelligence Hub

Interface interativa para visualizar status dos projetos.

Uso:
    python3 cli.py
    python3 cli.py --export-md
    python3 cli.py --interactive
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Dashboard:
    """Dashboard CLI para visualização de projetos."""

    def __init__(self, db_path: str = None, use_rich: bool = True):
        """
        Inicializa dashboard.

        Args:
            db_path: Path para o banco de dados SQLite.
            use_rich: Usar rich para formatação (se disponível)
        """
        if db_path is None:
            script_dir = Path(__file__).parent.parent
            db_path = script_dir / "index" / "projects.db"

        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        self.use_rich = use_rich and RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()

    def get_statistics(self) -> Dict:
        """Retorna estatísticas gerais."""
        stats = {}

        # Total de projetos
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM projects")
        stats['total_projects'] = cursor.fetchone()['count']

        # Projetos raiz
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM projects WHERE parent_project_id IS NULL"
        )
        stats['root_projects'] = cursor.fetchone()['count']

        # Repositórios git
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM projects WHERE has_git = 1")
        stats['with_git'] = cursor.fetchone()['count']

        # Monorepos
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM projects WHERE is_monorepo = 1")
        stats['monorepos'] = cursor.fetchone()['count']

        # Com memory system
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM projects WHERE has_memory_system = 1")
        stats['with_memory'] = cursor.fetchone()['count']

        # Com CLAUDE.md
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM projects WHERE has_claude_md = 1")
        stats['with_claude_md'] = cursor.fetchone()['count']

        # Por tipo
        cursor = self.conn.execute("""
            SELECT type, COUNT(*) as count
            FROM projects
            GROUP BY type
            ORDER BY count DESC
        """)
        stats['by_type'] = {row['type']: row['count'] for row in cursor.fetchall()}

        # Por status
        cursor = self.conn.execute("""
            SELECT status, COUNT(*) as count
            FROM projects
            GROUP BY status
            ORDER BY count DESC
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

        # Último scan
        cursor = self.conn.execute("""
            SELECT created_at, projects_found, scan_duration_seconds
            FROM scan_history
            ORDER BY created_at DESC
            LIMIT 1
        """)
        last_scan = cursor.fetchone()
        if last_scan:
            stats['last_scan'] = dict(last_scan)

        return stats

    def get_top_priorities(self, limit: int = 5) -> List[Dict]:
        """Retorna projetos de maior prioridade."""
        cursor = self.conn.execute("""
            SELECT
                name,
                type,
                priority,
                framework,
                is_monorepo,
                has_claude_md,
                has_memory_system,
                (SELECT COUNT(*) FROM projects sub WHERE sub.parent_project_id = projects.id) as subproject_count
            FROM projects
            WHERE parent_project_id IS NULL
            ORDER BY priority ASC, name ASC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_monorepos(self) -> List[Dict]:
        """Retorna todos os monorepos."""
        cursor = self.conn.execute("""
            SELECT
                name,
                path,
                workspace_type,
                (SELECT COUNT(*) FROM projects sub WHERE sub.parent_project_id = projects.id) as subproject_count
            FROM projects
            WHERE is_monorepo = 1
            ORDER BY subproject_count DESC, name ASC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def display(self):
        """Exibe dashboard principal."""
        if self.use_rich:
            self._display_rich()
        else:
            self._display_plain()

    def _display_rich(self):
        """Exibe dashboard usando rich."""
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]CLAUDE PROJECTS INTELLIGENCE HUB[/bold cyan]\n"
            "[dim]Sistema de Inteligência Unificada de Projetos[/dim]",
            border_style="cyan"
        ))
        self.console.print()

        # Estatísticas
        stats = self.get_statistics()

        stats_table = Table(title="📊 Estatísticas Gerais", show_header=False)
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", style="bold green")

        stats_table.add_row("Total de projetos", str(stats['total_projects']))
        stats_table.add_row("Projetos raiz", str(stats['root_projects']))
        stats_table.add_row("Repositórios Git", str(stats['with_git']))
        stats_table.add_row("Monorepos", str(stats['monorepos']))
        stats_table.add_row("Com Memory System", str(stats['with_memory']))
        stats_table.add_row("Com CLAUDE.md", str(stats['with_claude_md']))

        if stats.get('last_scan'):
            last_scan = stats['last_scan']
            scan_time = datetime.fromisoformat(last_scan['created_at'])
            stats_table.add_row(
                "Último scan",
                f"{scan_time.strftime('%Y-%m-%d %H:%M')} ({last_scan['projects_found']} projetos)"
            )

        self.console.print(stats_table)
        self.console.print()

        # Por tipo
        type_table = Table(title="📦 Por Tipo de Projeto")
        type_table.add_column("Tipo", style="cyan")
        type_table.add_column("Quantidade", style="bold")

        for proj_type, count in stats['by_type'].items():
            type_table.add_row(proj_type, str(count))

        self.console.print(type_table)
        self.console.print()

        # Top prioridades
        priorities = self.get_top_priorities()

        priority_table = Table(title="🎯 Top 5 Prioridades")
        priority_table.add_column("Projeto", style="bold cyan")
        priority_table.add_column("Pri", style="yellow")
        priority_table.add_column("Tipo", style="green")
        priority_table.add_column("Info", style="dim")

        for proj in priorities:
            priority_label = f"P{proj['priority']}"
            info_parts = []

            if proj['framework']:
                info_parts.append(proj['framework'])
            if proj['is_monorepo']:
                info_parts.append(f"mono:{proj['subproject_count']}")
            if proj['has_claude_md']:
                info_parts.append("📄")
            if proj['has_memory_system']:
                info_parts.append("🧠")

            priority_table.add_row(
                proj['name'],
                priority_label,
                proj['type'],
                " ".join(info_parts)
            )

        self.console.print(priority_table)
        self.console.print()

        # Monorepos
        monorepos = self.get_monorepos()

        if monorepos:
            mono_table = Table(title="🏗️  Monorepos")
            mono_table.add_column("Nome", style="bold cyan")
            mono_table.add_column("Workspace", style="green")
            mono_table.add_column("Subprojetos", style="yellow")

            for mono in monorepos:
                mono_table.add_row(
                    mono['name'],
                    mono['workspace_type'] or 'unknown',
                    str(mono['subproject_count'])
                )

            self.console.print(mono_table)
            self.console.print()

    def _display_plain(self):
        """Exibe dashboard em texto simples."""
        print("\n" + "="*60)
        print("CLAUDE PROJECTS INTELLIGENCE HUB")
        print("="*60 + "\n")

        stats = self.get_statistics()

        print("📊 ESTATÍSTICAS GERAIS\n")
        print(f"  Total de projetos: {stats['total_projects']}")
        print(f"  Projetos raiz: {stats['root_projects']}")
        print(f"  Repositórios Git: {stats['with_git']}")
        print(f"  Monorepos: {stats['monorepos']}")
        print(f"  Com Memory System: {stats['with_memory']}")
        print(f"  Com CLAUDE.md: {stats['with_claude_md']}")

        if stats.get('last_scan'):
            last_scan = stats['last_scan']
            scan_time = datetime.fromisoformat(last_scan['created_at'])
            print(f"  Último scan: {scan_time.strftime('%Y-%m-%d %H:%M')}")

        print("\n📦 POR TIPO\n")
        for proj_type, count in stats['by_type'].items():
            print(f"  {proj_type}: {count}")

        print("\n🎯 TOP 5 PRIORIDADES\n")
        priorities = self.get_top_priorities()

        for i, proj in enumerate(priorities, 1):
            markers = []
            if proj['is_monorepo']:
                markers.append(f"MONOREPO ({proj['subproject_count']})")
            if proj['has_claude_md']:
                markers.append("DOCS")
            if proj['has_memory_system']:
                markers.append("MEMORY")

            marker_str = f" [{', '.join(markers)}]" if markers else ""

            print(f"  {i}. {proj['name']} (P{proj['priority']}) - {proj['type']}{marker_str}")
            if proj['framework']:
                print(f"     Framework: {proj['framework']}")

        print("\n" + "="*60 + "\n")

    def export_markdown(self) -> str:
        """Exporta dashboard em formato Markdown."""
        stats = self.get_statistics()
        priorities = self.get_top_priorities()
        monorepos = self.get_monorepos()

        md = f"""# Dashboard - Claude Projects Intelligence Hub

**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 Estatísticas Gerais

| Métrica | Valor |
|---------|-------|
| Total de projetos | {stats['total_projects']} |
| Projetos raiz | {stats['root_projects']} |
| Repositórios Git | {stats['with_git']} |
| Monorepos | {stats['monorepos']} |
| Com Memory System | {stats['with_memory']} |
| Com CLAUDE.md | {stats['with_claude_md']} |
"""

        if stats.get('last_scan'):
            last_scan = stats['last_scan']
            scan_time = datetime.fromisoformat(last_scan['created_at'])
            md += f"| Último scan | {scan_time.strftime('%Y-%m-%d %H:%M')} |\n"

        md += "\n---\n\n## 📦 Por Tipo de Projeto\n\n"
        md += "| Tipo | Quantidade |\n|------|------------|\n"
        for proj_type, count in stats['by_type'].items():
            md += f"| {proj_type} | {count} |\n"

        md += "\n---\n\n## 🎯 Top 5 Prioridades\n\n"
        for i, proj in enumerate(priorities, 1):
            markers = []
            if proj['is_monorepo']:
                markers.append(f"MONOREPO ({proj['subproject_count']} subprojetos)")
            if proj['has_claude_md']:
                markers.append("📄 Documentado")
            if proj['has_memory_system']:
                markers.append("🧠 Memory System")

            md += f"### {i}. {proj['name']}\n\n"
            md += f"- **Prioridade**: P{proj['priority']}\n"
            md += f"- **Tipo**: {proj['type']}\n"
            if proj['framework']:
                md += f"- **Framework**: {proj['framework']}\n"
            if markers:
                md += f"- **Features**: {', '.join(markers)}\n"
            md += "\n"

        if monorepos:
            md += "\n---\n\n## 🏗️ Monorepos\n\n"
            md += "| Nome | Workspace | Subprojetos |\n"
            md += "|------|-----------|-------------|\n"
            for mono in monorepos:
                md += f"| {mono['name']} | {mono['workspace_type'] or 'unknown'} | {mono['subproject_count']} |\n"

        md += f"\n---\n\n*Gerado automaticamente pelo Claude Projects Intelligence Hub*\n"

        return md

    def close(self):
        """Fecha conexão com banco."""
        if self.conn:
            self.conn.close()


def main():
    """CLI principal."""
    parser = argparse.ArgumentParser(
        description='Dashboard CLI - Claude Projects Intelligence Hub'
    )

    parser.add_argument('--export-md', action='store_true', help='Exportar para Markdown')
    parser.add_argument('--interactive', action='store_true', help='Modo interativo (futuro)')
    parser.add_argument('--no-rich', action='store_true', help='Desabilitar rich formatting')

    args = parser.parse_args()

    try:
        dashboard = Dashboard(use_rich=not args.no_rich)

        if args.export_md:
            md = dashboard.export_markdown()
            print(md)
        else:
            dashboard.display()

        dashboard.close()

    except FileNotFoundError as e:
        print(f"Erro: {e}", file=sys.stderr)
        print("\nExecute o scanner primeiro:", file=sys.stderr)
        print("  python3 index/scanner.py full-scan --verbose", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
