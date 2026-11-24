import sqlite3
from config import DB_PATH

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS documents(
          id TEXT PRIMARY KEY, name TEXT NOT NULL, file_path TEXT NOT NULL,
          file_hash TEXT UNIQUE, page_count INTEGER DEFAULT 0, file_size INTEGER DEFAULT 0,
          status TEXT DEFAULT 'processing', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS conversations(
          id TEXT PRIMARY KEY, document_id TEXT NOT NULL, title TEXT DEFAULT 'New chat',
          created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS messages(
          id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL, role TEXT NOT NULL,
          content TEXT NOT NULL, sources_json TEXT DEFAULT '[]', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS generated_actions(
          id TEXT PRIMARY KEY, document_id TEXT NOT NULL, action_type TEXT NOT NULL,
          title TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE);
        ''')

def rows(query, params=()):
    with connect() as c: return [dict(r) for r in c.execute(query, params).fetchall()]

def execute(query, params=()):
    with connect() as c: c.execute(query, params); c.commit()
