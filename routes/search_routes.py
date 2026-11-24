from flask import Blueprint,request,jsonify
from backend.embeddings import embed
from backend.vector_store import search
from backend.database import rows
from backend.gemini_client import user_facing_error
srch=Blueprint('search',__name__)
@srch.post('/api/search')
def semantic_search():
    body=request.json or {}; query=(body.get('query') or '').strip(); doc_ids=body.get('document_ids') or []
    if not query:return jsonify(error='Enter a search query.'),400
    try:
        hits=search(embed(query),doc_ids or None,10)
        names={r['id']:r['name'] for r in rows('SELECT id,name FROM documents')}
        return jsonify(results=[{**h,'document_name':names.get(h['document_id'],'Document')} for h in hits])
    except Exception as e:return jsonify(error=user_facing_error(e)),500
