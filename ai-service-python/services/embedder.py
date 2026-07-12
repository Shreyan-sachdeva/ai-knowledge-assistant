from fastembed import TextEmbedding

model = None

def get_model():
    global model
    if model is None:
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return model

def create_embeddings(chunks, batch_size=5):
    m = get_model()
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        batch_embeddings = list(m.embed(batch))
        all_embeddings.extend([e.tolist() for e in batch_embeddings])
    return all_embeddings