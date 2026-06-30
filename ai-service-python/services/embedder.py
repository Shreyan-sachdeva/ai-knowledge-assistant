from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

def create_embeddings(chunks):
    embeddings = model.encode(chunks)

    return embeddings.tolist()