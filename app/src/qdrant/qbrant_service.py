from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from typing import List, Tuple

# Create a collection if it doesn't exist.
def init_collection(client: QdrantClient, collection_name: str, vector_size=384):
    if not client.collection_exists(collection_name):
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

# Add text + vector + topic
def add_text(client: QdrantClient, collection_name: str, ids: list, vectors: list, chunks: list, topic: str):
    points = [
        PointStruct(
            id=uid,
            vector=vector,
            payload={"id": uid, "text": chunk, "topic": topic}
        )
        for uid, vector, chunk in zip(ids, vectors, chunks)
    ]
    client.upsert(collection_name=collection_name, points=points)

# Find the nearest vector
def search_text(client: QdrantClient, collection_name: str, query_vector: list, limit: int = 3, topic: str = None):
    results = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=limit,
    query_filter={
        "must": [
            {
                "key": "topic",
                "match": {
                    "value": topic
                }
            }
        ]
    }
)
    return [{"text": r.payload['text'], "topic": r.payload['topic'], "score": r.score} for r in results]

# Delete collection
def delete_collection(client: QdrantClient, collection_name: str):
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name=collection_name)
        print(f"Collection {collection_name} deleted.")
    else:
        print(f"Collection {collection_name} does not exist.")

def get_available_topics(client: QdrantClient, collection_name: str) -> List[str]:
    response, _ = client.scroll(
        collection_name=collection_name,
        limit=10_000,
        with_payload=True,
    )

    topics = {point.payload.get("topic") for point in response if point.payload and point.payload.get("topic")}
    return list(topics)

# Get all texts from your Qdrant collection
def get_all_texts_from_qdrant(client: QdrantClient, collection_name: str) -> List[Tuple[str, str]]:
    scroll_result = client.scroll(
        collection_name=collection_name,
        with_payload=True,
        limit=1000  # adjust based on size
    )
    return [
        (point.payload.get("id", ""), point.payload.get("text", ""))
        for point in scroll_result[0]
        if "id" in point.payload and "text" in point.payload
    ]