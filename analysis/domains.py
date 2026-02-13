#!/usr/bin/env python3
"""
Análise de Domínios de Negócio - Claude Projects Intelligence Hub

Classifica projetos por domínio de negócio e identifica oportunidades de integração.

Uso:
    python3 domains.py classify
    python3 domains.py report
    python3 domains.py integrations
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import json


class DomainAnalyzer:
    """Analisador de domínios de negócio dos projetos."""

    # Regras de classificação: (padrão no nome ou path, domínio, descrição)
    DOMAIN_RULES = [
        # ERP/CRM/COMEX
        (['sisconect', 'sisimpo', 'sistema-impo', 'comex', 'nf-e', 'fiscal'],
         'ERP/CRM/COMEX', 'Sistemas empresariais, importação e exportação'),

        # Ponto Eletrônico
        (['ponyo', 'ponto-digital', 'ponto-eletronico'],
         'Ponto Eletrônico', 'Controle de ponto e RH'),

        # Financeiro
        (['financeiro', 'cash-flow', 'p2p', 'arbitragem', 'crypto', 'fechamento'],
         'Financeiro', 'Sistemas financeiros e criptomoedas'),

        # Marketing/Sites
        (['vvn', 'marketing', 'site', 'landing', 'xprecords', 'music'],
         'Marketing/Sites', 'Sites institucionais e marketing digital'),

        # AI/ML
        (['ai', 'ml-system', 'assistente', 'jarvis', 'vilanova-ai', 'claude', 'memory'],
         'AI/ML', 'Inteligência artificial e machine learning'),

        # Gaming/Rifas
        (['rifa', 'game', 'bet', 'sorteio'],
         'Gaming/Entretenimento', 'Jogos, rifas e entretenimento'),

        # Educação
        (['edu', 'tcc', 'faculdade', 'curso', 'learn'],
         'Educação', 'Projetos educacionais'),

        # Logística
        (['bill-of-lading', 'shipping', 'freight', 'logistica'],
         'Logística', 'Transporte e logística'),

        # Infraestrutura/DevOps
        (['docker', 'ci-cd', 'deploy', 'infra', 'mcp', 'crawler'],
         'Infraestrutura', 'DevOps e infraestrutura'),
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

    def classify_project(self, name: str, path: str) -> str:
        """Classifica um projeto em um domínio de negócio."""
        name_lower = name.lower()
        path_lower = path.lower()

        for keywords, domain, _ in self.DOMAIN_RULES:
            for kw in keywords:
                if kw in name_lower or kw in path_lower:
                    return domain

        return 'Outros'

    def classify_all(self) -> Dict[str, List[Dict]]:
        """Classifica todos os projetos raiz por domínio."""
        cursor = self.conn.execute("""
            SELECT id, name, path, type, status, priority, framework,
                   has_git, git_last_commit_date, has_claude_md, has_memory_system,
                   is_monorepo
            FROM projects
            WHERE parent_project_id IS NULL
            ORDER BY priority ASC, name ASC
        """)

        domains = defaultdict(list)

        for row in cursor.fetchall():
            project = dict(row)
            domain = self.classify_project(project['name'], project['path'])
            project['domain'] = domain
            domains[domain].append(project)

        return dict(domains)

    def get_domain_stats(self) -> List[Dict]:
        """Retorna estatísticas por domínio."""
        domains = self.classify_all()
        stats = []

        for domain, projects in sorted(domains.items(), key=lambda x: len(x[1]), reverse=True):
            active = sum(1 for p in projects if p['status'] == 'active')
            maintained = sum(1 for p in projects if p['status'] == 'maintained')
            legacy = sum(1 for p in projects if p['status'] in ('legacy', 'unknown'))
            with_git = sum(1 for p in projects if p['has_git'])
            with_docs = sum(1 for p in projects if p['has_claude_md'])
            monorepos = sum(1 for p in projects if p['is_monorepo'])

            stats.append({
                'domain': domain,
                'total': len(projects),
                'active': active,
                'maintained': maintained,
                'legacy': legacy,
                'with_git': with_git,
                'with_docs': with_docs,
                'monorepos': monorepos,
                'health_score': round((active + maintained * 0.5) / max(len(projects), 1) * 100),
            })

        return stats

    def find_integrations(self) -> List[Dict]:
        """Identifica oportunidades de integração entre domínios."""
        domains = self.classify_all()
        integrations = []

        # Regras de integração
        integration_rules = [
            ('ERP/CRM/COMEX', 'Financeiro',
             'Integrar fechamento fiscal com sistema financeiro'),
            ('ERP/CRM/COMEX', 'Logística',
             'Conectar processos de importação com bill of lading'),
            ('Ponto Eletrônico', 'ERP/CRM/COMEX',
             'Integrar dados de funcionários do ERP com ponto'),
            ('AI/ML', 'ERP/CRM/COMEX',
             'Usar IA para análise preditiva de processos'),
            ('Marketing/Sites', 'ERP/CRM/COMEX',
             'CRM integrado com sites de marketing'),
        ]

        for domain_a, domain_b, description in integration_rules:
            if domain_a in domains and domain_b in domains:
                projects_a = [p['name'] for p in domains[domain_a] if p['status'] in ('active', 'maintained')]
                projects_b = [p['name'] for p in domains[domain_b] if p['status'] in ('active', 'maintained')]

                if projects_a and projects_b:
                    integrations.append({
                        'domain_a': domain_a,
                        'domain_b': domain_b,
                        'description': description,
                        'projects_a': projects_a[:3],
                        'projects_b': projects_b[:3],
                        'feasibility': 'alta' if len(projects_a) <= 2 and len(projects_b) <= 2 else 'média',
                    })

        return integrations

    def generate_report(self) -> str:
        """Gera relatório completo de domínios em Markdown."""
        stats = self.get_domain_stats()
        domains = self.classify_all()
        integrations = self.find_integrations()

        lines = [
            "# Relatório de Domínios de Negócio",
            f"\n**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Domínios identificados**: {len(stats)}",
            "",
            "## Resumo por Domínio",
            "",
            "| Domínio | Total | Ativos | Mantidos | Legacy | Saúde |",
            "|---------|-------|--------|----------|--------|-------|",
        ]

        for s in stats:
            lines.append(
                f"| {s['domain']} | {s['total']} | {s['active']} | "
                f"{s['maintained']} | {s['legacy']} | {s['health_score']}% |"
            )

        lines.append("")

        # Detalhes por domínio
        for domain_name, projects in sorted(domains.items()):
            lines.append(f"## {domain_name}")
            lines.append("")

            for p in projects:
                status_icon = {'active': 'o', 'maintained': '-', 'legacy': 'x'}.get(p['status'], '?')
                framework = f" ({p['framework']})" if p['framework'] else ""
                lines.append(f"- [{status_icon}] **{p['name']}**{framework} - {p['path']}")

            lines.append("")

        # Integrações
        if integrations:
            lines.append("## Oportunidades de Integração")
            lines.append("")

            for i, intg in enumerate(integrations, 1):
                lines.append(f"### {i}. {intg['domain_a']} + {intg['domain_b']}")
                lines.append(f"**Descrição**: {intg['description']}")
                lines.append(f"**Viabilidade**: {intg['feasibility']}")
                lines.append(f"**Projetos**: {', '.join(intg['projects_a'])} <-> {', '.join(intg['projects_b'])}")
                lines.append("")

        return "\n".join(lines)

    def update_tags(self):
        """Atualiza a coluna tags de cada projeto com seu domínio."""
        domains = self.classify_all()
        updated = 0

        for domain, projects in domains.items():
            for p in projects:
                current_tags = p.get('tags') or '[]'
                try:
                    tags = json.loads(current_tags) if isinstance(current_tags, str) else []
                except:
                    tags = []

                if domain not in tags:
                    tags.append(domain)

                self.conn.execute(
                    "UPDATE projects SET tags = ? WHERE id = ?",
                    (json.dumps(tags), p['id'])
                )
                updated += 1

        self.conn.commit()
        return updated

    def close(self):
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Análise de Domínios - Claude Projects Intelligence Hub'
    )

    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('classify', help='Classificar projetos por domínio')
    subparsers.add_parser('stats', help='Estatísticas por domínio')
    subparsers.add_parser('integrations', help='Oportunidades de integração')
    subparsers.add_parser('report', help='Relatório completo')
    subparsers.add_parser('update-tags', help='Atualizar tags no banco')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    analyzer = DomainAnalyzer()

    try:
        if args.command == 'classify':
            domains = analyzer.classify_all()
            print(f"\n{'='*60}")
            print("CLASSIFICAÇÃO POR DOMÍNIO")
            print(f"{'='*60}\n")

            for domain, projects in sorted(domains.items()):
                print(f"\n--- {domain} ({len(projects)} projetos) ---")
                for p in projects:
                    status = p.get('status', 'unknown')
                    print(f"  [{status:10s}] {p['name']}")

        elif args.command == 'stats':
            stats = analyzer.get_domain_stats()
            print(f"\n{'='*60}")
            print("ESTATÍSTICAS POR DOMÍNIO")
            print(f"{'='*60}\n")

            for s in stats:
                print(f"{s['domain']}:")
                print(f"  Total: {s['total']} | Ativos: {s['active']} | "
                      f"Mantidos: {s['maintained']} | Legacy: {s['legacy']}")
                print(f"  Saúde: {s['health_score']}% | Git: {s['with_git']} | "
                      f"Docs: {s['with_docs']} | Monorepos: {s['monorepos']}")
                print()

        elif args.command == 'integrations':
            integrations = analyzer.find_integrations()
            print(f"\n{'='*60}")
            print("OPORTUNIDADES DE INTEGRAÇÃO")
            print(f"{'='*60}\n")

            if not integrations:
                print("Nenhuma oportunidade identificada.\n")
            else:
                for i, intg in enumerate(integrations, 1):
                    print(f"{i}. {intg['domain_a']} <-> {intg['domain_b']}")
                    print(f"   {intg['description']}")
                    print(f"   Viabilidade: {intg['feasibility']}")
                    print()

        elif args.command == 'report':
            print(analyzer.generate_report())

        elif args.command == 'update-tags':
            updated = analyzer.update_tags()
            print(f"\n{updated} projetos atualizados com tags de domínio.\n")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
