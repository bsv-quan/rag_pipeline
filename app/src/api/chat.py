from app.src.rag.standard_rag import run as standard_rag_run
from app.src.rag.hybrid_rag import run as hybrid_rag_run
import time

async def handle_chat(question: str, type: str, client: any, collection_name: str, is_topic: bool):
    """
    Chat with the RAG system using a query
    """
    try:
        if type == "standard":
            result = standard_rag_run(question, client, collection_name, is_topic)
        elif type == "hybrid":
            result = hybrid_rag_run(question, client, collection_name, is_topic)
        return 200, "Get answer successfully", result
    except Exception as e:
        return 500, str(e), None