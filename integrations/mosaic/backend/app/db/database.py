import sqlite3

from app.core.config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS _mosaic_meta (key TEXT PRIMARY KEY, value TEXT)")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                model_name TEXT NOT NULL,
                configuration TEXT NOT NULL DEFAULT '{}',
                enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1))
            )
        """)

        columns = {row["name"] for row in connection.execute("PRAGMA table_info(models)").fetchall()}
        if "configuration" not in columns:
            connection.execute("ALTER TABLE models ADD COLUMN configuration TEXT NOT NULL DEFAULT '{}'")
        if "enabled" not in columns:
            connection.execute("ALTER TABLE models ADD COLUMN enabled INTEGER NOT NULL DEFAULT 1")

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_models_provider_model_name
            ON models (provider, model_name)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NULL,
                workspace TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                state TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NULL,
                type TEXT NOT NULL CHECK (type IN ('user_fact', 'user_preference', 'user_claim', 'project_state', 'instruction')),
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL NULL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                mode TEXT NOT NULL DEFAULT 'chat',
                model_id INTEGER NOT NULL,
                project_id INTEGER NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NULL,
                project_id INTEGER NULL,
                type TEXT NOT NULL CHECK (
                    type IN ('code_project', 'document', 'analysis', 'report', 'generic')
                ),
                mode TEXT NOT NULL CHECK (mode IN ('create', 'agent')),
                status TEXT NOT NULL DEFAULT 'pending' CHECK (
                    status IN (
                        'pending',
                        'planning',
                        'awaiting_approval',
                        'executing',
                        'validating',
                        'completed',
                        'failed',
                        'cancelled'
                    )
                ),
                plan TEXT NULL,
                result TEXT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                CHECK (conversation_id IS NOT NULL OR project_id IS NOT NULL),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_conversation_id
            ON tasks(conversation_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_project_id
            ON tasks(project_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                target TEXT NULL,
                payload TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending' CHECK (
                    status IN (
                        'pending',
                        'approved',
                        'executing',
                        'completed',
                        'rejected',
                        'failed',
                        'cancelled'
                    )
                ),
                result TEXT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_actions_task_id
            ON actions(task_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_actions_status
            ON actions(status)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                task_id INTEGER NULL,
                tool_name TEXT NOT NULL,
                arguments TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending' CHECK (
                    status IN (
                        'pending',
                        'approved',
                        'executing',
                        'completed',
                        'failed',
                        'rejected',
                        'cancelled'
                    )
                ),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calls_conversation_id
            ON tool_calls(conversation_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calls_task_id
            ON tool_calls(task_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calls_status
            ON tool_calls(status)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tool_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_call_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('completed', 'failed')),
                data TEXT NULL,
                error TEXT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (tool_call_id) REFERENCES tool_calls(id) ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_results_tool_call_id
            ON tool_results(tool_call_id)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS task_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                conversation_id INTEGER NULL,
                project_id INTEGER NULL,
                tool_call_id INTEGER NULL,
                action_id INTEGER NULL,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error')),
                component TEXT NOT NULL,
                event_name TEXT NOT NULL,
                message TEXT NOT NULL,
                duration_ms INTEGER NULL CHECK (duration_ms IS NULL OR duration_ms >= 0),
                status TEXT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (tool_call_id) REFERENCES tool_calls(id) ON DELETE SET NULL,
                FOREIGN KEY (action_id) REFERENCES actions(id) ON DELETE SET NULL
            )
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_events_task_order
            ON task_events(task_id, id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_events_conversation
            ON task_events(conversation_id, id)
        """)

        connection.commit()
