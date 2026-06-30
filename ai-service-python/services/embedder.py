from fastembed import TextEmbedding

model = None

def get_model():
    global model
    if model is None:
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return model

def create_embeddings(chunks):
    embeddings = list(get_model().embed(chunks))

    return [e.tolist() for e in embeddings]