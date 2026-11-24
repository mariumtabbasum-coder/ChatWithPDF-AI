import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import MAX_UPLOAD_MB
from backend.database import init_db
from routes.document_routes import docs
from routes.chat_routes import chat
from routes.action_routes import actions
from routes.search_routes import srch
app=Flask(__name__)
app.config['MAX_CONTENT_LENGTH']=MAX_UPLOAD_MB*1024*1024
CORS(app)
init_db()
app.register_blueprint(docs); app.register_blueprint(chat); app.register_blueprint(actions); app.register_blueprint(srch)

@app.get('/api/health')
def health():
    """Small local check to confirm the Flask server is reachable."""
    return jsonify(status='ok')

@app.get('/')
def home():return render_template('index.html')
@app.get('/workspace')
def workspace():return render_template('workspace.html')
if __name__=='__main__':
    # Keep the development reloader off: ChromaDB is initialized at import time
    # and should only have one process opening its persistent local database.
    app.run(
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', '5000')),
        debug=os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'},
        use_reloader=False,
    )
