import time

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from services.pdf_parser import extract_text
from services.chunker import chunk_text
from services.embedder import create_embeddings
from services.vector_store import store_chunks, search_similar_chunks, save_chat_history, get_chat_history
from services.ollama_service import generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

class SearchRequest(BaseModel):
    question: str
    limit: int = 1

class AskRequest(BaseModel):
    question: str
    session_id: str
    limit: int = 1 

class HistoryRequest(BaseModel):
    session_id: str

@app.get("/warmup")
async def warmup():
    from services.embedder import get_model
    get_model()
    return {"status": "model loaded"}
    
@app.post("/process")
async def process_document(file: UploadFile = File(...), documentId: int = Form(...)):
    try:
        import tempfile
        import os

        content = await file.read()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        text = extract_text(temp_file_path)
        os.unlink(temp_file_path)

        chunks = chunk_text(text)
        embeddings = create_embeddings(chunks)
        store_chunks(chunks, embeddings, documentId)

        return {
            "success": True,
            "chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post('/ask')
async def ask(request: AskRequest):
    try:
        total_start = time.time()

        # Step 1: create embedding for question
        t1 = time.time()
        query_embedding = create_embeddings([request.question])[0]
        t2 = time.time()
        print(f"[TIMER] Embedding question: {t2-t1:.2f}s")

        # Step 2: search similar chunks
        t3 = time.time()
        results = search_similar_chunks(query_embedding, request.limit)
        t4 = time.time()
        print(f"[TIMER] Vector search: {t4-t3:.2f}s")

        # Step 3: get chunk texts
        relevant_chunks = [r[0] for r in results]

        # Step 4: generate answer with Ollama
        t5 = time.time()
        answer = generate_answer(request.question, relevant_chunks)
        t6 = time.time()
        print(f"[TIMER] Ollama generation: {t6-t5:.2f}s")

        # Step 5: save to chat history
        t7 = time.time()
        save_chat_history(request.session_id, request.question, answer)
        t8 = time.time()
        print(f"[TIMER] Save history: {t8-t7:.2f}s")

        total_end = time.time()
        print(f"[TIMER] TOTAL: {total_end-total_start:.2f}s")

        return {
            "success": True,
            "question": request.question,
            "answer": answer,
            "chunks_used": len(relevant_chunks),
            "session_id": request.session_id,
            "timings": {
                "embedding": round(t2-t1, 2),
                "search": round(t4-t3, 2),
                "ollama": round(t6-t5, 2),
                "save_history": round(t8-t7, 2),
                "total": round(total_end-total_start, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/search')
async def search(request: SearchRequest):
    try:
        query_embedding = create_embeddings([request.question])[0]
        results = search_similar_chunks(query_embedding, request.limit)
        return {
            "success": True,
            "results":[
            {
                "chunk_text" : r[0],
                "similarity" : float(r[1])
            }
            for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.get('/history/{session_id}')
async def get_history(session_id: str):
    try:
        history = get_chat_history(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "history": [
                {
                    "question": h[2],
                    "answer": h[3],
                    "created_at": str(h[4])
                }
                for h in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail =str(e))

@app.get("/health")
def health():
    return {
        "status": "ai-service-python is running"
    }