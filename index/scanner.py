#!/usr/bin/env python3
"""
Scanner de Projetos - Claude Projects Intelligence Hub

Escaneia diretórios recursivamente em busca de projetos e atualiza o banco SQLite.

Uso:
    python3 scanner.py scan --location /caminho/para/diretorio
    python3 scanner.py update --path /caminho/para/projeto/especifico
    python3 scanner.py full-scan
"""

import sqlite3
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse
import time

class ProjectScanner:
    """Scanner de projetos que indexa metadados no banco SQLite."""

    # Arquivos que indicam tipos de projeto
    PROJECT_MARKERS = {
        'nodejs': ['package.json'],
        'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
        'php': ['composer.json'],
        'rust': ['Cargo.toml'],
        'go': ['go.mod'],
        'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
        'csharp': ['.csproj', '.sln'],
        'ruby': ['Gemfile'],
    }

    # Arquivos que indicam monorepo
    MONOREPO_MARKERS = [
        'pnpm-workspace.yaml',
        'lerna.json',
        'nx.json',
        'turbo.json',
    ]

    # Documentação conhecida
    DOC_FILES = {
        'README.md': 'README',
        'README': 'README',
        'CLAUDE.md': 'CLAUDE.md',
        '.claude/CLAUDE.md': 'CLAUDE.md',
        'CONTEXT.md': 'CONTEXT.md',
        'STATUS.md': 'STATUS.md',
        'AUTOLOAD.md': 'AUTOLOAD.md',
    }

    # Diretórios a ignorar
    IGNORE_DIRS = {
        'node_modules', '.git', 'dist', 'build', '__pycache__',
        'venv', 'env', '.venv', 'target', 'out', '.next',
        '.cache', 'coverage', '.pytest_cache', 'vendor'
    }

    def __init__(self, db_path: str = None, max_depth: int = 10, verbose: bool = False):
        """
        Inicializa o scanner.

        Args:
            db_path: Path para o banco de dados SQLite.
            max_depth: Profundidade máxima de busca recursiva.
            verbose: Modo verbose para logging.
        """
        if db_path is None:
            script_dir = Path(__file__).parent
            db_path = script_dir / "projects.db"

        self.db_path = Path(db_path)
        self.max_depth = max_depth
        self.verbose = verbose
        self.conn = None
        self._init_database()

    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp."""
        if self.verbose or level == "ERROR":
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def _init_database(self):
        """Inicializa o banco de dados usando schema.sql."""
        schema_path = Path(__file__).parent / "schema.sql"

        if not self.db_path.exists():
            self.log(f"Criando banco de dados: {self.db_path}")

            if schema_path.exists():
                # Criar banco usando schema.sql
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()

                conn = sqlite3.connect(str(self.db_path))
                conn.executescript(schema_sql)
                conn.commit()
                conn.close()
                self.log("Banco de dados criado com sucesso")
            else:
                self.log(f"Schema não encontrado: {schema_path}", "ERROR")
                raise FileNotFoundError(f"Schema SQL não encontrado: {schema_path}")

        # Conectar ao banco
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def scan_location(self, location: str, update_existing: bool = True) -> Dict:
        """
        Escaneia uma localização em busca de projetos.

        Args:
            location: Path do diretório para escanear
            update_existing: Se True, atualiza projetos existentes

        Returns:
            Dicionário com estatísticas do scan
        """
        start_time = time.time()
        location_path = Path(location).resolve()

        if not location_path.exists():
            self.log(f"Localização não existe: {location}", "ERROR")
            return {'error': 'Location not found'}

        self.log(f"Iniciando scan: {location_path}")

        stats = {
            'projects_found': 0,
            'projects_added': 0,
            'projects_updated': 0,
            'max_depth_found': 0,
            'location': str(location_path),
        }

        # Escanear recursivamente
        projects = self._scan_recursive(location_path, depth=0)
        stats['projects_found'] = len(projects)

        # === PASSE 1: Inserir/atualizar todos os projetos (sem hierarquia) ===
        path_to_id = {}

        for project_info in projects:
            if project_info['depth_level'] > stats['max_depth_found']:
                stats['max_depth_found'] = project_info['depth_level']

            existing = self._get_project_by_path(project_info['path'])

            if existing:
                if update_existing:
                    self._update_project(existing['id'], project_info)
                    stats['projects_updated'] += 1
                    self.log(f"Atualizado: {project_info['name']}")
                path_to_id[project_info['path']] = existing['id']
            else:
                project_id = self._insert_project(project_info)
                stats['projects_added'] += 1
                self.log(f"Adicionado: {project_info['name']}")
                path_to_id[project_info['path']] = project_id

        # === PASSE 2: Resolver hierarquia pai/filho com IDs reais ===
        hierarchy_updates = 0
        for project_info in projects:
            parent_path = project_info.get('parent_path')
            if parent_path and parent_path in path_to_id:
                project_path = project_info['path']
                if project_path in path_to_id:
                    parent_db_id = path_to_id[parent_path]
                    project_db_id = path_to_id[project_path]
                    self.conn.execute(
                        "UPDATE projects SET parent_project_id = ?, is_subproject = 1 WHERE id = ?",
                        (parent_db_id, project_db_id)
                    )
                    hierarchy_updates += 1

        if hierarchy_updates > 0:
            self.conn.commit()
            self.log(f"Hierarquia resolvida: {hierarchy_updates} relações pai/filho")

        # Salvar histórico de scan
        duration = time.time() - start_time
        stats['scan_duration_seconds'] = duration
        self._save_scan_history(stats)

        self.log(f"Scan completo: {stats['projects_found']} encontrados, "
                f"{stats['projects_added']} novos, {stats['projects_updated']} atualizados "
                f"em {duration:.2f}s")

        return stats

    def _scan_recursive(self, path: Path, depth: int, parent_path: str = None) -> List[Dict]:
        """
        Escaneia recursivamente em busca de projetos.

        Args:
            path: Caminho atual
            depth: Profundidade atual
            parent_path: Path do projeto pai (para resolução posterior)

        Returns:
            Lista de dicionários com informações de projetos
        """
        if depth > self.max_depth:
            return []

        projects = []

        # Verificar se este diretório é um projeto
        project_info = self._detect_project(path, depth, parent_path)

        if project_info:
            projects.append(project_info)
            current_parent_path = project_info['path']
        else:
            current_parent_path = parent_path

        # Escanear subdiretórios (exceto os ignorados)
        try:
            for item in path.iterdir():
                if item.is_dir() and item.name not in self.IGNORE_DIRS:
                    sub_projects = self._scan_recursive(item, depth + 1, current_parent_path)
                    projects.extend(sub_projects)
        except PermissionError:
            self.log(f"Sem permissão: {path}", "WARN")

        return projects

    def _detect_project(self, path: Path, depth: int, parent_path: str = None) -> Optional[Dict]:
        """
        Detecta se um diretório é um projeto e extrai metadados.

        Args:
            path: Caminho do diretório
            depth: Profundidade atual
            parent_path: Path do projeto pai (para resolução posterior)

        Returns:
            Dicionário com informações do projeto ou None
        """
        project_type = self._detect_type(path)

        if project_type is None:
            return None

        # Informações básicas
        project_info = {
            'name': path.name,
            'path': str(path.resolve()),
            'type': project_type,
            'depth_level': depth,
            'parent_path': parent_path,  # Path do pai para resolução em 2 passes
            'parent_project_id': None,   # Será preenchido no passe 2
            'is_subproject': parent_path is not None,
        }

        # Detectar monorepo
        monorepo_info = self._detect_monorepo(path)
        project_info.update(monorepo_info)

        # Git info
        git_info = self._extract_git_info(path)
        project_info.update(git_info)

        # Documentação
        docs = self._extract_documentation(path)
        project_info['documentation'] = docs
        project_info['has_readme'] = any(d['doc_type'] == 'README' for d in docs)
        project_info['has_claude_md'] = any(d['doc_type'] == 'CLAUDE.md' for d in docs)
        project_info['has_context_md'] = any(d['doc_type'] == 'CONTEXT.md' for d in docs)

        # Memory system
        project_info['has_memory_system'] = (path / '.memory').exists()

        # Package manager e framework
        pm_fw = self._detect_package_manager_framework(path, project_type)
        project_info.update(pm_fw)

        return project_info

    def _detect_type(self, path: Path) -> Optional[str]:
        """Detecta o tipo de projeto baseado em arquivos."""
        for proj_type, markers in self.PROJECT_MARKERS.items():
            for marker in markers:
                if (path / marker).exists():
                    return proj_type

        # Se tem .git mas nenhum marcador de código, é git-only
        if (path / '.git').exists():
            return 'git-only'

        return None

    def _detect_monorepo(self, path: Path) -> Dict:
        """Detecta se é monorepo e qual tipo."""
        for marker in self.MONOREPO_MARKERS:
            marker_path = path / marker
            if marker_path.exists():
                workspace_type = marker.replace('.json', '').replace('.yaml', '').replace('-workspace', '')
                return {
                    'is_monorepo': True,
                    'has_workspace_config': True,
                    'workspace_type': workspace_type,
                }

        return {
            'is_monorepo': False,
            'has_workspace_config': False,
            'workspace_type': None,
        }

    def _extract_git_info(self, path: Path) -> Dict:
        """Extrai informações do repositório git."""
        git_dir = path / '.git'

        if not git_dir.exists():
            return {
                'has_git': False,
                'git_remote': None,
                'git_branch': None,
                'git_last_commit_date': None,
            }

        try:
            # Branch atual
            result = subprocess.run(
                ['git', '-C', str(path), 'branch', '--show-current'],
                capture_output=True, text=True, timeout=5
            )
            branch = result.stdout.strip() if result.returncode == 0 else None

            # Remote URL
            result = subprocess.run(
                ['git', '-C', str(path), 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, timeout=5
            )
            remote = result.stdout.strip() if result.returncode == 0 else None

            # Último commit
            result = subprocess.run(
                ['git', '-C', str(path), 'log', '-1', '--format=%ci'],
                capture_output=True, text=True, timeout=5
            )
            last_commit = result.stdout.strip() if result.returncode == 0 else None

            return {
                'has_git': True,
                'git_remote': remote,
                'git_branch': branch,
                'git_last_commit_date': last_commit,
            }
        except (subprocess.TimeoutExpired, Exception) as e:
            self.log(f"Erro ao extrair git info de {path}: {e}", "WARN")
            return {
                'has_git': True,
                'git_remote': None,
                'git_branch': None,
                'git_last_commit_date': None,
            }

    def _extract_documentation(self, path: Path) -> List[Dict]:
        """Identifica arquivos de documentação."""
        docs = []

        for doc_file, doc_type in self.DOC_FILES.items():
            doc_path = path / doc_file
            if doc_path.exists() and doc_path.is_file():
                try:
                    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)

                    stat = doc_path.stat()
                    last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

                    docs.append({
                        'doc_type': doc_type,
                        'file_path': str(doc_path),
                        'line_count': line_count,
                        'last_modified': last_modified,
                    })
                except Exception as e:
                    self.log(f"Erro ao ler {doc_path}: {e}", "WARN")

        return docs

    def _detect_package_manager_framework(self, path: Path, project_type: str) -> Dict:
        """Detecta package manager e framework."""
        result = {
            'package_manager': None,
            'framework': None,
        }

        if project_type == 'nodejs':
            # Package manager
            if (path / 'pnpm-lock.yaml').exists():
                result['package_manager'] = 'pnpm'
            elif (path / 'yarn.lock').exists():
                result['package_manager'] = 'yarn'
            elif (path / 'package-lock.json').exists():
                result['package_manager'] = 'npm'

            # Framework (detectar via package.json)
            package_json = path / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

                        if 'next' in deps:
                            result['framework'] = 'nextjs'
                        elif '@nestjs/core' in deps:
                            result['framework'] = 'nestjs'
                        elif 'express' in deps:
                            result['framework'] = 'express'
                        elif 'react' in deps and 'vite' in deps:
                            result['framework'] = 'vite'
                except:
                    pass

        elif project_type == 'python':
            if (path / 'Pipfile').exists():
                result['package_manager'] = 'pipenv'
            elif (path / 'poetry.lock').exists():
                result['package_manager'] = 'poetry'
            else:
                result['package_manager'] = 'pip'

        elif project_type == 'php':
            result['package_manager'] = 'composer'
            if (path / 'artisan').exists():
                result['framework'] = 'laravel'

        elif project_type == 'rust':
            result['package_manager'] = 'cargo'

        elif project_type == 'go':
            result['package_manager'] = 'go'

        return result

    def _get_project_by_path(self, path: str) -> Optional[Dict]:
        """Busca projeto pelo path."""
        cursor = self.conn.execute(
            "SELECT * FROM projects WHERE path = ?",
            (path,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def _insert_project(self, project_info: Dict) -> int:
        """Insere novo projeto no banco."""
        cursor = self.conn.execute("""
            INSERT INTO projects (
                name, path, type, depth_level, parent_project_id, is_subproject,
                is_monorepo, has_workspace_config, workspace_type,
                has_git, git_remote, git_branch, git_last_commit_date,
                has_readme, has_claude_md, has_context_md, has_memory_system,
                package_manager, framework
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_info['name'],
            project_info['path'],
            project_info['type'],
            project_info['depth_level'],
            project_info.get('parent_project_id'),
            project_info['is_subproject'],
            project_info['is_monorepo'],
            project_info['has_workspace_config'],
            project_info.get('workspace_type'),
            project_info['has_git'],
            project_info.get('git_remote'),
            project_info.get('git_branch'),
            project_info.get('git_last_commit_date'),
            project_info['has_readme'],
            project_info['has_claude_md'],
            project_info['has_context_md'],
            project_info['has_memory_system'],
            project_info.get('package_manager'),
            project_info.get('framework'),
        ))

        project_id = cursor.lastrowid

        # Inserir documentação
        for doc in project_info.get('documentation', []):
            self.conn.execute("""
                INSERT INTO project_docs (project_id, doc_type, file_path, line_count, last_modified)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_id,
                doc['doc_type'],
                doc['file_path'],
                doc['line_count'],
                doc['last_modified'],
            ))

        self.conn.commit()
        return project_id

    def _update_project(self, project_id: int, project_info: Dict):
        """Atualiza projeto existente."""
        self.conn.execute("""
            UPDATE projects SET
                name = ?, type = ?, depth_level = ?, parent_project_id = ?,
                is_subproject = ?, is_monorepo = ?, has_workspace_config = ?,
                workspace_type = ?, has_git = ?, git_remote = ?, git_branch = ?,
                git_last_commit_date = ?, has_readme = ?, has_claude_md = ?,
                has_context_md = ?, has_memory_system = ?, package_manager = ?,
                framework = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            project_info['name'],
            project_info['type'],
            project_info['depth_level'],
            project_info.get('parent_project_id'),
            project_info['is_subproject'],
            project_info['is_monorepo'],
            project_info['has_workspace_config'],
            project_info.get('workspace_type'),
            project_info['has_git'],
            project_info.get('git_remote'),
            project_info.get('git_branch'),
            project_info.get('git_last_commit_date'),
            project_info['has_readme'],
            project_info['has_claude_md'],
            project_info['has_context_md'],
            project_info['has_memory_system'],
            project_info.get('package_manager'),
            project_info.get('framework'),
            project_id,
        ))

        # Atualizar documentação (deletar e reinserir)
        self.conn.execute("DELETE FROM project_docs WHERE project_id = ?", (project_id,))
        for doc in project_info.get('documentation', []):
            self.conn.execute("""
                INSERT INTO project_docs (project_id, doc_type, file_path, line_count, last_modified)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_id,
                doc['doc_type'],
                doc['file_path'],
                doc['line_count'],
                doc['last_modified'],
            ))

        self.conn.commit()

    def _save_scan_history(self, stats: Dict):
        """Salva histórico de scan."""
        self.conn.execute("""
            INSERT INTO scan_history (
                location, projects_found, projects_updated, projects_added,
                max_depth_found, scan_duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            stats['location'],
            stats['projects_found'],
            stats['projects_updated'],
            stats['projects_added'],
            stats['max_depth_found'],
            stats['scan_duration_seconds'],
        ))
        self.conn.commit()

    def update_project(self, path: str) -> bool:
        """Atualiza informações de um projeto específico."""
        path_obj = Path(path).resolve()

        if not path_obj.exists():
            self.log(f"Projeto não existe: {path}", "ERROR")
            return False

        self.log(f"Atualizando projeto: {path}")

        # Detectar projeto
        project_info = self._detect_project(path_obj, depth=0)

        if not project_info:
            self.log(f"Não é um projeto válido: {path}", "ERROR")
            return False

        # Verificar se existe
        existing = self._get_project_by_path(str(path_obj))

        if existing:
            self._update_project(existing['id'], project_info)
            self.log(f"Projeto atualizado: {project_info['name']}")
        else:
            self._insert_project(project_info)
            self.log(f"Projeto adicionado: {project_info['name']}")

        return True

    def full_scan(self) -> Dict:
        """Escaneia todas as localizações configuradas."""
        locations = [
            '/Users/victorvilanova/projetos/',
            '/Users/victorvilanova/Downloads/',
        ]

        total_stats = {
            'locations_scanned': 0,
            'total_projects_found': 0,
            'total_projects_added': 0,
            'total_projects_updated': 0,
            'max_depth_overall': 0,
            'total_duration': 0,
        }

        for location in locations:
            if not Path(location).exists():
                self.log(f"Localização não existe: {location}", "WARN")
                continue

            stats = self.scan_location(location)

            if 'error' not in stats:
                total_stats['locations_scanned'] += 1
                total_stats['total_projects_found'] += stats['projects_found']
                total_stats['total_projects_added'] += stats['projects_added']
                total_stats['total_projects_updated'] += stats['projects_updated']
                total_stats['max_depth_overall'] = max(
                    total_stats['max_depth_overall'],
                    stats['max_depth_found']
                )
                total_stats['total_duration'] += stats['scan_duration_seconds']

        return total_stats

    def close(self):
        """Fecha conexão com banco."""
        if self.conn:
            self.conn.close()


def main():
    """CLI principal do scanner."""
    parser = argparse.ArgumentParser(
        description='Scanner de Projetos - Claude Projects Intelligence Hub'
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando: scan
    scan_parser = subparsers.add_parser('scan', help='Escanear localização específica')
    scan_parser.add_argument('--location', required=True, help='Path do diretório')
    scan_parser.add_argument('--max-depth', type=int, default=10, help='Profundidade máxima')
    scan_parser.add_argument('--verbose', action='store_true', help='Modo verbose')

    # Comando: update
    update_parser = subparsers.add_parser('update', help='Atualizar projeto específico')
    update_parser.add_argument('--path', required=True, help='Path do projeto')
    update_parser.add_argument('--verbose', action='store_true', help='Modo verbose')

    # Comando: full-scan
    full_parser = subparsers.add_parser('full-scan', help='Escanear todas as localizações')
    full_parser.add_argument('--max-depth', type=int, default=10, help='Profundidade máxima')
    full_parser.add_argument('--verbose', action='store_true', help='Modo verbose')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Executar comando
    if args.command == 'scan':
        scanner = ProjectScanner(max_depth=args.max_depth, verbose=args.verbose)
        stats = scanner.scan_location(args.location)
        print(json.dumps(stats, indent=2))
        scanner.close()

    elif args.command == 'update':
        scanner = ProjectScanner(verbose=args.verbose)
        success = scanner.update_project(args.path)
        scanner.close()
        exit(0 if success else 1)

    elif args.command == 'full-scan':
        scanner = ProjectScanner(max_depth=args.max_depth, verbose=args.verbose)
        stats = scanner.full_scan()
        print("\n" + "="*60)
        print("FULL SCAN COMPLETO")
        print("="*60)
        print(f"Localizações escaneadas: {stats['locations_scanned']}")
        print(f"Total de projetos encontrados: {stats['total_projects_found']}")
        print(f"Novos projetos: {stats['total_projects_added']}")
        print(f"Projetos atualizados: {stats['total_projects_updated']}")
        print(f"Profundidade máxima: {stats['max_depth_overall']} níveis")
        print(f"Duração total: {stats['total_duration']:.2f}s")
        print("="*60)
        scanner.close()


if __name__ == "__main__":
    main()
