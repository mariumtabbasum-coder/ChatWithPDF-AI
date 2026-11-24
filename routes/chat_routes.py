import uuid, json
from flask import Blueprint, request, jsonify
from backend.database import rows, execute
from backend.embeddings import embed
from backend.vector_store import search
from backend.chatbot import answer_question
from backend.gemini_client import user_facing_error

chat=Blueprint('chat',__name__)
@chat.post('/api/chats')
def new_chat():
    doc_id=request.json.get('document_id')
    if not rows('SELECT id FROM documents WHERE id=?',(doc_id,)): return jsonify(error='Document not found.'),404
    cid=str(uuid.uuid4()); execute('INSERT INTO conversations(id,document_id,title) VALUES(?,?,?)',(cid,doc_id,'New chat'))
    return jsonify(id=cid),201
@chat.get('/api/chats')
def chats_list(): return jsonify(rows('SELECT c.*, d.name AS document_name FROM conversations c LEFT JOIN documents d ON d.id=c.document_id ORDER BY c.updated_at DESC'))
@chat.get('/api/chats/<cid>/messages')
def messages(cid): return jsonify(rows('SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at',(cid,)))
@chat.post('/api/chat')
def ask():
    body=request.json or {}; question=(body.get('question') or '').strip(); cid=body.get('conversation_id')
    if not question or not cid: return jsonify(error='Question and conversation ID are required.'),400
    conv=rows('SELECT * FROM conversations WHERE id=?',(cid,))
    if not conv:return jsonify(error='Conversation not found.'),404
    doc_id=conv[0]['document_id']; prior=rows('SELECT role,content FROM messages WHERE conversation_id=? ORDER BY created_at',(cid,))
    execute('INSERT INTO messages(id,conversation_id,role,content) VALUES(?,?,?,?)',(str(uuid.uuid4()),cid,'user',question))
    try:
        vector=embed(question); hits=search(vector,[doc_id],5); response=answer_question(question,hits,prior)
    except Exception as e: return jsonify(error=user_facing_error(e)),500
    sources=[{'page':h['page'],'document_id':h['document_id'],'snippet':h['text'][:350]} for h in hits]
    execute('INSERT INTO messages(id,conversation_id,role,content,sources_json) VALUES(?,?,?,?,?)',(str(uuid.uuid4()),cid,'assistant',response,json.dumps(sources)))
    execute('UPDATE conversations SET updated_at=CURRENT_TIMESTAMP WHERE id=?',(cid,))
    return jsonify(answer=response,sources=sources)
@chat.delete('/api/chats/<cid>')
def delete_chat(cid): execute('DELETE FROM conversations WHERE id=?',(cid,)); return jsonify(success=True)
@chat.patch('/api/chats/<cid>/rename')
def rename(cid):
    title=(request.json or {}).get('title','').strip()
    if not title:return jsonify(error='Title cannot be empty.'),400
    execute('UPDATE conversations SET title=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(title,cid)); return jsonify(success=True)
