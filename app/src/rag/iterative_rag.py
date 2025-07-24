from app.src.process import generate_answer_from_docs, generate_followup_question_if_needed, get_model, detect_topic
from app.src.qdrant import get_available_topics
from qdrant_client import QdrantClient
from typing import List
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
import time

def run(question: str, client: QdrantClient, retriever: BaseRetriever, collection_name: str, is_topic: bool, max_iterations: int = 3):
    """
    Run Iterative RAG to refine answer through multiple retrieval and generation steps.

    Args:
        question (str): The user's complex question.
        client (QdrantClient): Qdrant vector database client.
        collection_name (str): Name of the collection to search.
        is_topic (bool): Whether to detect topic from the question.
        max_iterations (int): Maximum number of refinement loops.

    Returns:
        dict: Final answer, topic, and elapsed time.
    """
    
    if not retriever:
        return {"answer": "No retriever provided", "topic": None, "time": 0, "iterations": 0}
    
    start = time.time()  # Start timing
    
    if is_topic:
        # Detect topic from the question and available topics
        topic = detect_topic(question, get_available_topics(client, collection_name))
    else:
        topic = None
        
    current_question = question  # Set the current question for the first iteration
    accumulated_context: List[Document] = []  # Store all retrieved documents
    answer = ""  # Initialize answer
    
    for iteration in range(max_iterations):
        # Retrieve documents relevant to the current question
        docs = retriever.get_relevant_documents(current_question)
        accumulated_context.extend(docs)  # Add new docs to the context

        # Generate answer from the accumulated context
        answer = generate_answer_from_docs(current_question, accumulated_context)

        # Generate a follow-up question if the answer is insufficient
        followup_question = generate_followup_question_if_needed(current_question, answer)

        if not followup_question:
            break  # No follow-up needed, stop iteration

        current_question = followup_question  # Update question for next iteration

    end = time.time()  # End timing
    return {
        "answer": answer,  # Final answer
        "topic": topic,    # Detected topic (if any)
        "time": round(end - start, 3),  # Total elapsed time
        "iterations": iteration + 1     # Number of iterations performed
    }
