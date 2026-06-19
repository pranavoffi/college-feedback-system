# config.py

# import torch
# from langchain.embeddings import HuggingFaceEmbeddings
#
# VECTOR_STORE_PATH = "db/chroma_index"
# EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
#
# USE_CUDA = torch.cuda.is_available()
#
# def get_embedding_model():
#     return HuggingFaceEmbeddings(
#         model_name=EMBEDDING_MODEL_NAME,
#         model_kwargs={"device": "cuda" if USE_CUDA else "cpu"}
#     )



# config.py

from langchain_community.embeddings.ollama import OllamaEmbeddings

VECTOR_STORE_PATH = "db/chroma_index"
OLLAMA_MODEL = "nomic-embed-text"

def get_embedding_model():
    return OllamaEmbeddings(model=OLLAMA_MODEL)
