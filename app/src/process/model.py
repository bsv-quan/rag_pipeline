from sentence_transformers import SentenceTransformer
def get_model():
    """
    Returns the model for the RAG system.
    Use multilingual E5
    """
    return SentenceTransformer("intfloat/multilingual-e5-small")