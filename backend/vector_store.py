import json
import math
import sqlite3

from config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_store():
    with _connect() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vector_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                page INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_vector_chunks_document ON vector_chunks(document_id)')


_init_store()


def add_document(doc_id, chunks, vectors):
    records = [
        (f'{doc_id}_{i}', doc_id, int(chunk['page']), i, chunk['text'], json.dumps(vectors[i]))
        for i, chunk in enumerate(chunks)
    ]
    with _connect() as conn:
        conn.executemany(
            'INSERT OR REPLACE INTO vector_chunks (id, document_id, page, chunk_index, text, embedding) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            records,
        )


def search(vector, document_ids=None, n=5):
    if not n or n < 1:
        return []

    sql = 'SELECT document_id, page, text, embedding FROM vector_chunks'
    params = []
    if document_ids is not None:
        if not document_ids:
            return []
        placeholders = ','.join('?' for _ in document_ids)
        sql += f' WHERE document_id IN ({placeholders})'
        params.extend(document_ids)

    query_norm = math.sqrt(sum(float(value) ** 2 for value in vector))
    if query_norm == 0:
        return []

    hits = []
    with _connect() as conn:
        for row in conn.execute(sql, params):
            embedding = json.loads(row['embedding'])
            if len(embedding) != len(vector):
                continue
            doc_norm = math.sqrt(sum(float(value) ** 2 for value in embedding))
            if doc_norm == 0:
                continue
            similarity = sum(float(a) * float(b) for a, b in zip(vector, embedding)) / (query_norm * doc_norm)
            hits.append({
                'text': row['text'],
                'page': row['page'],
                'document_id': row['document_id'],
                'distance': 1.0 - similarity,
            })

    hits.sort(key=lambda hit: hit['distance'])
    return hits[:n]


def delete_document(doc_id):
    with _connect() as conn:
        conn.execute('DELETE FROM vector_chunks WHERE document_id = ?', (doc_id,))
