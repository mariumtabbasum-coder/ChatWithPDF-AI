import hashlib, os, uuid
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from config import UPLOAD_DIR, MAX_UPLOAD_MB
from backend.database import rows, execute
from backend.pdf_processor import extract_pages
from backend.chunker import chunk_pages
from backend.embeddings import embed_many
from backend.vector_store import add_document, delete_document
from backend.gemini_client import user_facing_error

docs=Blueprint('docs',__name__)

@docs.get('/api/documents')
def list_docs(): return jsonify(rows('SELECT * FROM documents ORDER BY created_at DESC'))

@docs.post('/api/documents/upload')
def upload():
    file=request.files.get('file')
    if not file or not file.filename: return jsonify(error='Choose a PDF file.'),400
    if not file.filename.lower().endswith('.pdf'): return jsonify(error='Only PDF files are accepted.'),400
    data=file.read()
    if len(data)>MAX_UPLOAD_MB*1024*1024: return jsonify(error=f'File exceeds {MAX_UPLOAD_MB} MB limit.'),413
    if not data.startswith(b'%PDF-'): return jsonify(error='The selected file is not a valid PDF document.'),400
    digest=hashlib.sha256(data).hexdigest()
    duplicate=rows('SELECT id FROM documents WHERE file_hash=?',(digest,))
    if duplicate: return jsonify(error='This PDF is already in your library.',document_id=duplicate[0]['id']),409
    doc_id=str(uuid.uuid4()); name=secure_filename(file.filename) or 'document.pdf'; path=UPLOAD_DIR/f'{doc_id}_{name}'
    path.write_bytes(data)
    try:
        pages,page_count=extract_pages(path); chunks=chunk_pages(pages)
        if not chunks: raise ValueError('No usable text chunks found.')
        vectors=embed_many([c['text'] for c in chunks]); add_document(doc_id,chunks,vectors)
        execute('INSERT INTO documents(id,name,file_path,file_hash,page_count,file_size,status) VALUES(?,?,?,?,?,?,?)',(doc_id,name,str(path),digest,page_count,len(data),'ready'))
    except Exception as e:
        path.unlink(missing_ok=True)
        return jsonify(error=user_facing_error(e)),500
    return jsonify(id=doc_id,name=name,page_count=page_count,status='ready'),201

@docs.get('/api/documents/<doc_id>')
def detail(doc_id):
    result=rows('SELECT * FROM documents WHERE id=?',(doc_id,))
    if not result:return jsonify(error='Document not found.'),404
    return jsonify(result[0])

@docs.get('/api/documents/<doc_id>/preview')
def preview(doc_id):
    result=rows('SELECT * FROM documents WHERE id=?',(doc_id,))
    if not result:return jsonify(error='Document not found.'),404
    return send_file(result[0]['file_path'], mimetype='application/pdf')

@docs.delete('/api/documents/<doc_id>')
def remove(doc_id):
    result=rows('SELECT * FROM documents WHERE id=?',(doc_id,))
    if not result:return jsonify(error='Document not found.'),404
    delete_document(doc_id)
    try: os.remove(result[0]['file_path'])
    except OSError: pass
    execute('DELETE FROM documents WHERE id=?',(doc_id,))
    return jsonify(success=True)
