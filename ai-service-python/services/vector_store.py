import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host = os.getenv('DB_HOST'),
        port = os.getenv('DB_PORT'),
        database = os.getenv('DB_NAME'),        
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD')
    )

def store_chunks(chunks, embeddings, document_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for i in range(len(chunks)):
            cursor.execute("INSERT INTO document_chunks (document_id, chunk_text, chunk_index) VALUES (%s, %s, %s) RETURNING id", (document_id, chunks[i], i))
            chunk_id = cursor.fetchone()[0]            
            embedding_str = str(embeddings[i])
            cursor.execute("INSERT INTO embeddings (chunk_id, vector) VALUES (%s, %s::vector)", (chunk_id, embedding_str))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def search_similar_chunks(query_embedding, limit = 1):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query_str = str(query_embedding)
        cursor.execute("SELECT dc.chunk_text, 1 - (e.vector <=> %s::vector) as similarity FROM embeddings e JOIN document_chunks dc ON e.chunk_id = dc.id ORDER BY e.vector <=> %s::vector LIMIT %s",(query_str, query_str, limit))
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()       

def save_chat_history(session_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO chat_history (session_id, question, answer) VALUES (%s, %s, %s)", (session_id, question, answer))
        conn.commit()    
    except Exception as e:
        conn.rollback()
        raise e    
    finally:
        cursor.close()
        conn.close()

def get_chat_history(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM chat_history WHERE session_id = %s ORDER BY created_at ASC", (session_id,))
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()
