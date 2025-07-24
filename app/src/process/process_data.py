import uuid
from .model import get_model
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Optional, List
from sentence_transformers import util

def preparing_data(text):
    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    embeddings = get_model().encode(["passage: " + c for c in chunks]).tolist()

    ids = [str(uuid.uuid4()) for _ in chunks]
    return [ids, embeddings, chunks]

def detect_topic(question: str, context_labels: List[str]) -> Optional[str]:
    """
    Detect topic using zero-shot classification.
    """
    model = get_model()

    # Encode
    emb_q = model.encode(question, convert_to_tensor=True)
    emb_labels = model.encode(context_labels, convert_to_tensor=True)

    # Calculate the similarity
    cos_scores = util.cos_sim(emb_q, emb_labels)[0]

    # Take the label with the highest score
    best_label = context_labels[cos_scores.argmax()]
    return best_label