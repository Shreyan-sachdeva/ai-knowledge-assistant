# AI Knowledge Assistant

An AI-powered document assistant that lets you upload PDFs and ask questions about them using RAG (Retrieval Augmented Generation).

---

## What It Does

- Admin uploads PDF files via a web interface
- PDFs are parsed, chunked, and stored in PostgreSQL
- Embeddings created using sentence-transformers and stored in pgvector
- Users ask questions in a chat interface
- AI generates answers from the uploaded documents only
- Chat history tracked by session

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Node.js + Express.js |
| AI Service | Python + FastAPI |
| Database | PostgreSQL + pgvector (Docker) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Groq API (llama-3.1-8b-instant) |
| Frontend | HTML + CSS + JavaScript |

---

## Project Structure

```
ai-knowledge-assistant/
├── backend-node/
│   ├── index.js
│   ├── package.json
│   ├── .env
│   ├── config/
│   │   ├── db.js
│   │   └── multer.js
│   ├── routes/
│   │   └── upload.js
│   └── middleware/
│       └── errorHandler.js
│
├── ai-service-python/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   └── services/
│       ├── pdf_parser.py
│       ├── chunker.py
│       ├── embedder.py
│       ├── vector_store.py
│       └── ollama_service.py
│
└── frontend/
    ├── admin.html
    └── user.html
```

---

## Setup & Installation

### Prerequisites
- Node.js
- Python 3.10+
- Docker Desktop
- Groq API key (free at https://console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/Shreyan-sachdeva/ai-knowledge-assistant.git
cd ai-knowledge-assistant
```

### 2. Start PostgreSQL with pgvector
```bash
docker run --name pgvector-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=knowledge_db \
  -e POSTGRES_USER=postgres \
  -p 5432:5432 \
  -d pgvector/pgvector:pg16
```

### 3. Create database tables
```bash
docker exec -it pgvector-db psql -U postgres -d knowledge_db
```
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT,
    chunk_index INTEGER
);

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER REFERENCES document_chunks(id),
    vector vector(384)
);

CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    question TEXT,
    answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Setup Node.js backend
```bash
cd backend-node
npm install
```

Create `.env`:
```env
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowledge_db
DB_USER=postgres
DB_PASSWORD=yourpassword
PYTHON_SERVICE_URL=http://localhost:8000
```

### 5. Setup Python AI service
```bash
cd ai-service-python
pip install -r requirements.txt
```

Create `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowledge_db
DB_USER=postgres
DB_PASSWORD=yourpassword
GROQ_API_KEY=your-groq-api-key
```

---

## Running The Project

### Terminal 1 — Start Docker:
```bash
docker start pgvector-db
```

### Terminal 2 — Start Node.js:
```bash
cd backend-node
node index.js
```

### Terminal 3 — Start Python:
```bash
cd ai-service-python
python -m uvicorn main:app --reload --port 8000
```

### Open Frontend:
- Admin panel: open `frontend/admin.html` in browser
- Chat interface: open `frontend/user.html` in browser

---

## API Endpoints

### Node.js (port 3000)
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/upload | Upload PDF |
| GET | /api/documents | List all documents |
| DELETE | /api/documents/:id | Delete document |
| GET | /health | Health check |

### Python (port 8000)
| Method | Endpoint | Description |
|---|---|---|
| POST | /process | Process PDF (called by Node.js) |
| POST | /ask | Ask a question (RAG) |
| POST | /search | Semantic search |
| GET | /history/{session_id} | Get chat history |
| GET | /health | Health check |

---

## Architecture

```
Admin uploads PDF
      ↓
Node.js receives file → saves to uploads/
      ↓
Node.js calls Python /process
      ↓
Python: extracts text → chunks → embeddings → pgvector
      ↓
User asks question (chat UI)
      ↓
Python: question → embedding → pgvector search
      ↓
Relevant chunks + question → Groq API
      ↓
AI generates answer from document context
```

---

## Git Workflow

```bash
# new feature
git checkout develop
git checkout -b feature/your-feature
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

Commit style:
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code improvement
- `docs:` documentation update
