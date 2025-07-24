from app.src.qdrant import StandardRetriever
from app.src.process import generate_answer, get_model, detect_topic
from app.src.qdrant import get_available_topics
from qdrant_client import QdrantClient
import time

def run(question: str, client: QdrantClient, collection_name: str, is_topic: bool, is_memory: bool):
    """
    Run the chat function with the provided parameters.

    Args:
        question (str): The user's question.
        client (QdrantClient): Qdrant vector database client.
        collection_name (str): Name of the collection to search.
        is_topic (bool): Whether to detect topic from the question.

    Returns:
        dict: Contains the answer, detected topic, and elapsed time.
    """
    start = time.time()
    if is_topic:
        # Detect topic based on the question and available topics in the collection
        topic = detect_topic(question, get_available_topics(client, collection_name))
    else:
        topic = None
    # Initialize retriever with embedding function and topic (if any)
    retriever = StandardRetriever(
        client=client,
        collection_name=collection_name,
        embed_fn=get_model().encode,
        topic=topic,
        top_k=5
    )
    # Generate answer using retriever and question
    result = generate_answer(retriever, question, is_memory)
    end = time.time()
    # Return answer, topic, and elapsed time
    return {"answer:": result, "topic": topic, "time": round(end - start, 3), "is_memory": is_memory}

def run_retriever(question: str, client: QdrantClient, collection_name: str, is_topic: bool):
    """
    Run the retriever with the provided parameters.

    Args:
        question (str): The user's question.
        client (QdrantClient): Qdrant vector database client.
        collection_name (str): Name of the collection to search.
        is_topic (bool): Whether to detect topic from the question.

    Returns:
        List[Document]: Retrieved documents based on the question.
    """
    retriever = StandardRetriever(
        client=client,
        collection_name=collection_name,
        embed_fn=get_model().encode,
        topic=detect_topic(question, get_available_topics(client, collection_name)) if is_topic else None,
        top_k=5
    )
    return retriever