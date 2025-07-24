from app.src.rag.standard_rag import run_retriever as standard_retriever, run as standard_rag_run
from app.src.rag.hybrid_rag import run_retriever as hybrid_retriever, run as hybrid_rag_run
from app.src.rag.iterative_rag import run as iterative_rag_run

async def handle_chat(question: str, 
                      type: str, 
                      client: any, 
                      collection_name: str, 
                      is_topic: bool, 
                      type_iterative: str,
                      is_memmory: bool):
    """
    Chat with the RAG system using a query
    """
    try:
        if type == "standard":
            result = standard_rag_run(question, client, collection_name, is_topic, is_memmory)
        elif type == "hybrid":
            result = hybrid_rag_run(question, client, collection_name, is_topic, is_memmory)
        elif type == "iterative":
            if type_iterative not in ["standard", "hybrid"]:
                return 400, "Invalid type_iterative parameter. Use 'standard' or 'hybrid'.", None
            if type_iterative == "standard":
                retriever = standard_retriever(question, client, collection_name, is_topic)
            else:
                retriever = hybrid_retriever(question, client, collection_name, is_topic)
            if not retriever:
                return 400, "No retriever provided", None
            result = iterative_rag_run(question, client, retriever, collection_name, is_topic)
        else:
            return 400, "Invalid type parameter. Use 'standard' or 'hybrid'.", None
        return 200, "Get answer successfully", result
    except Exception as e:
        return 500, str(e), None