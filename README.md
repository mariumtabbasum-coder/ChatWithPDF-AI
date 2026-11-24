# ChatWithPDF AI — Intelligent Document Workspace

A Flask-based PDF intelligence app with a forest/sage/linen workspace UI, Gemini-powered RAG chat, semantic retrieval, document actions, and two-document comparison.

## Features in this package
- Application dashboard with document, conversation, and saved-insight counts
- PDF upload, basic PDF signature validation, duplicate detection, text extraction, page-aware chunking and Gemini embeddings
- My Documents library with open, search and delete actions
- PDF.js document reader with page navigation and grounded AI chat citations
- Persistent conversations with reopen, rename and delete controls
- Semantic search across all documents or a selected document
- AI Studio: summary, detailed summary, chapter-wise summary, notes, key points, definitions, quiz, flashcards, checklist and explain
- Two-document comparison
- Saved generated insights
- Responsive sidebar navigation and mobile layouts
- SQLite metadata and vector storage

## Setup (Windows PowerShell)
```powershell
cd ChatWithPDF-AI
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Add your Gemini API key to `.env`, then run:
```powershell
venv\Scripts\python.exe app.py
```
Open http://127.0.0.1:5000.

Keep the terminal running while using the app, and open the URL above in your browser. Do not open `templates/index.html` directly: the pages use same-origin `/api/...` routes served by Flask, so opening a file or a separately hosted copy causes browser requests to fail. The local server check is available at http://127.0.0.1:5000/api/health and should return `{"status":"ok"}`.

If the dashboard loads but upload or chat reports a Gemini error, check that `GEMINI_API_KEY` in `.env` is a valid Google AI API key and restart the server after changing it.

## Important configuration and limitations
- The app uses the Gemini model names configured in `.env`. If the primary chat model returns a temporary 503 overload, chat, notes and comparison retry with `GEMINI_FALLBACK_CHAT_MODEL` (defaults to `gemini-3.8-flash`). Availability depends on your Google AI account and API access.
- Text-based PDFs are supported. Scanned/image-only PDFs require OCR, which is not included.
- Embedding calls are currently sequential; large PDFs can take time and may encounter provider rate limits.
- SQLite metadata and vectors are stored under `data/`, and PDFs under `uploads/`. Vercel uses its writable `/tmp` directory; serverless storage is ephemeral, so uploaded documents are lost when an instance is recycled. Use a hosted database and object storage for persistent deployment.
- This is a local single-user starter, not a production multi-tenant service. Add authentication, authorization, CSRF protection, rate limiting, background jobs and stricter file lifecycle controls before public deployment.
- PDF.js is loaded from a CDN in the workspace page; an internet connection is required for that viewer dependency.
- API keys belong only in `.env`; never commit or share it.
