from typing import List, Optional, Callable
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

class StandardRetriever(BaseRetriever, BaseModel):
    client: QdrantClient
    collection_name: str
    embed_fn: Callable[[List[str]], List[List[float]]]
    topic: Optional[str] = None
    top_k: int = 5

    def _get_filter(self):
        if self.topic:
            return Filter(
                must=[
                    FieldCondition(
                        key="topic",
                        match=MatchValue(value=self.topic)
                    )
                ]
            )
        return None

    def _get_relevant_documents(self, query: str) -> List[Document]:
        vector = self.embed_fn([f"passage: {query}"])[0]
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=self.top_k,
            query_filter=self._get_filter(),
            with_payload=True
        )
        return [
            Document(page_content=hit.payload.get("text", ""), metadata=hit.payload)
            for hit in hits
        ]
