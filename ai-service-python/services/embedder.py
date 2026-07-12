import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN")
)

def create_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        result = client.feature_extraction(
            chunk,
            model="BAAI/bge-small-en-v1.5"
        )
        embeddings.append(result.tolist())
    return embeddings