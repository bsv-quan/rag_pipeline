from app.src.rag.standard_rag import run_retriever as standard_retriever, run as standard_rag_run
from app.src.rag.hybrid_rag import run_retriever as hybrid_retriever, run as hybrid_rag_run
from app.src.rag.iterative_rag import run as iterative_rag_run
from typing import Optional

async def handle_chat(question: str, 
                      type: str, 
                      client: any, 
                      collection_name: str, 
                      is_topic: bool, 
                      type_iterative: str,
                      is_memmory: bool,
                      model_name: Optional[str] = None):
    """
    Chat with the RAG system using a query
    """
    print(f"Handling chat with question: {question}, type: {type}, collection_name: {collection_name}, is_topic: {is_topic}, type_iterative: {type_iterative}, is_memmory: {is_memmory}, model_name: {model_name}")
    try:
        if type == "standard":
            result = standard_rag_run(question, client, collection_name, is_topic, is_memmory, model_name=model_name)
        elif type == "hybrid":
            result = hybrid_rag_run(question, client, collection_name, is_topic, is_memmory, model_name=model_name)
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
        print(f"Error in handle_chat: {e}")
        return 500, str(e), None