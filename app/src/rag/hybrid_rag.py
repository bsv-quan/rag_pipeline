from app.src.qdrant import HybridRetriever
from app.src.process import generate_answer, get_model, detect_topic
from app.src.qdrant import get_available_topics, get_all_texts_from_qdrant
from qdrant_client import QdrantClient
import time

def run(question: str, client: QdrantClient, collection_name: str, is_topic: bool):
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
    # Get all texts from Qdrant collection for BM25
    pairs = get_all_texts_from_qdrant(client, collection_name)
    bm25_ids = [doc_id for doc_id, _ in pairs]
    bm25_corpus = [text for _, text in pairs]
    # Initialize retriever with embedding function and topic (if any)
    retriever = HybridRetriever(
        client=client,
        collection_name=collection_name,
        embed_fn=get_model().encode,
        bm25_corpus=bm25_corpus,
        bm25_ids=bm25_ids,
        topic=topic,
        top_k=5,
        alpha=0.5  # Balance between semantic and keyword
    )
    # Generate answer using retriever and question
    result = generate_answer(retriever, question)
    end = time.time()
    # Return answer, topic, and elapsed time
    return {"answer:": result, "topic": topic, "time": round(end - start, 3)}