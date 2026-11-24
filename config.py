import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
UPLOAD_DIR = BASE_DIR / 'uploads'
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / 'app.db'
CHROMA_PATH = DATA_DIR / 'chroma'
API_KEY = os.getenv('GEMINI_API_KEY', '')
CHAT_MODEL = os.getenv('GEMINI_CHAT_MODEL', 'gemini-2.5-flash')
CHAT_FALLBACK_MODEL = os.getenv('GEMINI_FALLBACK_CHAT_MODEL', 'gemini-3.8-flash')
EMBED_MODEL = os.getenv('GEMINI_EMBED_MODEL', 'gemini-embedding-001')
MAX_UPLOAD_MB = int(os.getenv('MAX_UPLOAD_MB', '20'))
