from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from rank_bm25 import BM25Okapi
from typing import List, Callable, Optional
from pydantic import BaseModel
import numpy as np

class HybridRetriever(BaseRetriever, BaseModel):
    client: QdrantClient
    collection_name: str
    embed_fn: Callable[[List[str]], List[List[float]]]
    bm25_corpus: List[str]  # Raw texts for BM25
    bm25_ids: List[str]  # IDs corresponding to the BM25 corpus
    topic: Optional[str] = None
    top_k: int = 5
    alpha: float = 0.5  # Weight for vector vs. keyword search
    bm25_id_map: dict = {}  # Map of BM25 IDs to texts

    def __init__(self, **data):
        super().__init__(**data)
        # Tokenize for BM25 index
        self._bm25_tokenized = [doc.lower().split() for doc in self.bm25_corpus]
        self._bm25 = BM25Okapi(self._bm25_tokenized)
        self.bm25_id_map = dict(zip(self.bm25_ids, self.bm25_corpus))

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
        # ====== 1. Vector Search with Qdrant ======
        vector = self.embed_fn([f"passage: {query}"])[0]
        vector_hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=20,
            query_filter=self._get_filter(),
            with_payload=True,
        )
        vector_scores = {
            hit.payload["id"]: 1 - hit.score  # id → similarity
            for hit in vector_hits if "id" in hit.payload
        }
        id_to_text = {
            hit.payload["id"]: hit.payload.get("text", "")
            for hit in vector_hits if "id" in hit.payload
        }

        # ====== 2. BM25 Search ======
        bm25_scores = self._bm25.get_scores(query.lower().split())
        bm25_map = {
            self.bm25_ids[i]: score for i, score in enumerate(bm25_scores)
        }  # self.bm25_ids: list of ids in same order as corpus

        # ====== 3. Merge by ID ======
        all_ids = set(vector_scores.keys()) | set(bm25_map.keys())
        combined_scores = []
        for doc_id in all_ids:
            vec_score = vector_scores.get(doc_id, 0.0)
            bm25_score = bm25_map.get(doc_id, 0.0)
            combined = self.alpha * vec_score + (1 - self.alpha) * bm25_score
            text = id_to_text.get(doc_id, self.bm25_id_map.get(doc_id, ""))
            combined_scores.append((text, combined, doc_id))

        # ====== 4. Sort and build Document ======
        top_results = sorted(combined_scores, key=lambda x: x[1], reverse=True)[:self.top_k]
        docs = [
            Document(
                page_content=text,
                metadata={"score": score, "id": doc_id}
            )
            for text, score, doc_id in top_results
        ]
        return docs
