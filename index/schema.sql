-- Claude Projects Intelligence Hub - Database Schema v2.0
-- SQLite3 Database for project indexing and analysis
-- SUPORTA HIERARQUIA E PROJETOS ANINHADOS

-- Main projects table (com suporte a hierarquia)
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,

    -- Hierarquia de projetos
    parent_project_id INTEGER,  -- NULL se for projeto raiz, ID do pai se for subprojeto
    depth_level INTEGER DEFAULT 0,  -- 0 = raiz, 1 = nível 1, etc.
    is_monorepo BOOLEAN DEFAULT 0,
    is_subproject BOOLEAN DEFAULT 0,

    type TEXT NOT NULL CHECK(type IN ('nodejs', 'python', 'php', 'rust', 'go', 'java', 'csharp', 'ruby', 'storage', 'git-only', 'unknown')),
    status TEXT NOT NULL DEFAULT 'unknown' CHECK(status IN ('active', 'maintained', 'legacy', 'archived', 'unknown')),
    priority INTEGER DEFAULT 3 CHECK(priority BETWEEN 0 AND 4),  -- 0=max, 4=min

    -- Git information
    has_git BOOLEAN DEFAULT 0,
    git_remote TEXT,
    git_branch TEXT,
    git_last_commit_date TIMESTAMP,

    -- Documentation
    has_claude_md BOOLEAN DEFAULT 0,
    has_readme BOOLEAN DEFAULT 0,
    has_context_md BOOLEAN DEFAULT 0,

    -- Special features
    has_memory_system BOOLEAN DEFAULT 0,
    has_workspace_config BOOLEAN DEFAULT 0,  -- pnpm-workspace.yaml, lerna.json, etc.
    workspace_type TEXT,  -- 'pnpm', 'lerna', 'nx', 'turborepo', etc.

    -- Package manager e framework info
    package_manager TEXT,  -- 'npm', 'pnpm', 'yarn', 'pip', 'poetry', 'composer', 'cargo', etc.
    framework TEXT,  -- 'nextjs', 'nestjs', 'express', 'django', 'laravel', etc.

    -- Metadata
    description TEXT,
    tags TEXT,  -- JSON array of tags
    config_files TEXT,  -- JSON array de arquivos de config encontrados

    -- Timestamps
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Project documentation files
CREATE TABLE IF NOT EXISTS project_docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL CHECK(doc_type IN ('README', 'CLAUDE.md', 'CONTEXT.md', 'STATUS.md', 'AUTOLOAD.md', 'OTHER')),
    file_path TEXT NOT NULL,
    line_count INTEGER,
    last_modified TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Dependencies between projects (código compartilhado, libs internas, etc.)
CREATE TABLE IF NOT EXISTS project_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    depends_on_project_id INTEGER NOT NULL,
    dependency_type TEXT CHECK(dependency_type IN ('monorepo', 'shared-lib', 'related', 'successor', 'fork', 'workspace-member')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, depends_on_project_id)
);

-- Tasks and TODOs per project
CREATE TABLE IF NOT EXISTS project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'done', 'cancelled')),
    priority INTEGER DEFAULT 2 CHECK(priority BETWEEN 0 AND 4),
    assigned_to TEXT,  -- Can be 'human', 'claude', or specific agent name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Analysis history
CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL CHECK(analysis_type IN ('status', 'priority', 'health', 'suggestion', 'hierarchy')),
    result TEXT,  -- JSON result
    suggestions TEXT,  -- JSON array of suggestions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Scan history (for tracking when scans happened)
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,  -- /Users/victorvilanova/projetos/, etc.
    projects_found INTEGER,
    projects_updated INTEGER,
    projects_added INTEGER,
    max_depth_found INTEGER,  -- Profundidade máxima encontrada
    scan_duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project hierarchy cache (para queries rápidas de árvore completa)
CREATE TABLE IF NOT EXISTS project_hierarchy_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    full_path_hierarchy TEXT,  -- Ex: "sisconect-v4/packages/services/auth-service"
    ancestors_json TEXT,  -- JSON array de IDs de todos os ancestrais
    descendants_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects(priority);
CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(type);
CREATE INDEX IF NOT EXISTS idx_projects_has_git ON projects(has_git);
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_parent_id ON projects(parent_project_id);
CREATE INDEX IF NOT EXISTS idx_projects_depth ON projects(depth_level);
CREATE INDEX IF NOT EXISTS idx_projects_is_monorepo ON projects(is_monorepo);
CREATE INDEX IF NOT EXISTS idx_projects_path ON projects(path);

CREATE INDEX IF NOT EXISTS idx_docs_project_id ON project_docs(project_id);
CREATE INDEX IF NOT EXISTS idx_docs_type ON project_docs(doc_type);

CREATE INDEX IF NOT EXISTS idx_deps_project_id ON project_dependencies(project_id);
CREATE INDEX IF NOT EXISTS idx_deps_depends_on ON project_dependencies(depends_on_project_id);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON project_tasks(priority);

CREATE INDEX IF NOT EXISTS idx_analysis_project_id ON analysis_history(project_id);
CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_history(analysis_type);

CREATE INDEX IF NOT EXISTS idx_hierarchy_cache_project_id ON project_hierarchy_cache(project_id);

-- Views for common queries

-- Active projects with high priority (apenas projetos raiz)
CREATE VIEW IF NOT EXISTS v_priority_projects AS
SELECT
    p.id,
    p.name,
    p.path,
    p.type,
    p.status,
    p.priority,
    p.has_git,
    p.git_branch,
    p.has_claude_md,
    p.has_memory_system,
    p.is_monorepo,
    p.description,
    p.last_scanned,
    (SELECT COUNT(*) FROM projects sub WHERE sub.parent_project_id = p.id) as subproject_count
FROM projects p
WHERE p.status IN ('active', 'maintained')
  AND p.parent_project_id IS NULL  -- Apenas projetos raiz
ORDER BY p.priority ASC, p.name ASC;

-- Monorepos com seus subprojetos
CREATE VIEW IF NOT EXISTS v_monorepos AS
SELECT
    p.id,
    p.name,
    p.path,
    p.workspace_type,
    (SELECT COUNT(*) FROM projects sub WHERE sub.parent_project_id = p.id) as subproject_count,
    p.has_workspace_config,
    p.last_scanned
FROM projects p
WHERE p.is_monorepo = 1
ORDER BY subproject_count DESC, p.name ASC;

-- Projetos sem documentação (excluindo subprojetos)
CREATE VIEW IF NOT EXISTS v_undocumented_projects AS
SELECT
    p.id,
    p.name,
    p.path,
    p.type,
    p.status,
    p.has_git,
    p.has_readme,
    p.has_claude_md,
    p.has_context_md,
    p.is_subproject
FROM projects p
WHERE p.has_git = 1
  AND p.has_claude_md = 0
  AND p.status IN ('active', 'maintained')
  AND p.parent_project_id IS NULL  -- Apenas projetos raiz (subprojetos podem não precisar)
ORDER BY p.priority ASC;

-- Projetos com pending tasks
CREATE VIEW IF NOT EXISTS v_projects_with_tasks AS
SELECT
    p.id,
    p.name,
    p.priority,
    p.is_subproject,
    COUNT(t.id) as pending_tasks,
    MIN(t.priority) as highest_task_priority
FROM projects p
INNER JOIN project_tasks t ON p.id = t.project_id
WHERE t.status = 'pending'
GROUP BY p.id, p.name, p.priority, p.is_subproject
ORDER BY highest_task_priority ASC, p.priority ASC;

-- Hierarquia completa (recursive CTE)
-- Retorna todos os projetos com caminho completo da hierarquia
CREATE VIEW IF NOT EXISTS v_project_hierarchy AS
WITH RECURSIVE project_tree AS (
    -- Base case: projetos raiz
    SELECT
        id,
        name,
        path,
        parent_project_id,
        depth_level,
        is_monorepo,
        is_subproject,
        name as full_hierarchy_name,
        CAST(id AS TEXT) as hierarchy_path
    FROM projects
    WHERE parent_project_id IS NULL

    UNION ALL

    -- Recursive case: subprojetos
    SELECT
        p.id,
        p.name,
        p.path,
        p.parent_project_id,
        p.depth_level,
        p.is_monorepo,
        p.is_subproject,
        pt.full_hierarchy_name || ' > ' || p.name as full_hierarchy_name,
        pt.hierarchy_path || '/' || CAST(p.id AS TEXT) as hierarchy_path
    FROM projects p
    INNER JOIN project_tree pt ON p.parent_project_id = pt.id
)
SELECT * FROM project_tree
ORDER BY hierarchy_path;

-- Subprojetos de um monorepo específico
-- Usage: WHERE parent_name = 'sisconect-v4-multi-tenant'
CREATE VIEW IF NOT EXISTS v_monorepo_subprojects AS
SELECT
    parent.name as parent_name,
    parent.id as parent_id,
    sub.id as subproject_id,
    sub.name as subproject_name,
    sub.path as subproject_path,
    sub.type as subproject_type,
    sub.depth_level,
    sub.framework
FROM projects parent
INNER JOIN projects sub ON sub.parent_project_id = parent.id
WHERE parent.is_monorepo = 1
ORDER BY parent.name, sub.depth_level, sub.name;

-- Estatísticas por tipo de projeto
CREATE VIEW IF NOT EXISTS v_project_stats_by_type AS
SELECT
    type,
    COUNT(*) as total,
    SUM(CASE WHEN parent_project_id IS NULL THEN 1 ELSE 0 END) as root_projects,
    SUM(CASE WHEN is_subproject = 1 THEN 1 ELSE 0 END) as subprojects,
    SUM(CASE WHEN is_monorepo = 1 THEN 1 ELSE 0 END) as monorepos,
    SUM(CASE WHEN has_git = 1 THEN 1 ELSE 0 END) as with_git,
    SUM(CASE WHEN has_claude_md = 1 THEN 1 ELSE 0 END) as with_claude_md
FROM projects
GROUP BY type
ORDER BY total DESC;
