from fastapi import FastAPI, File, UploadFile, Form
from app.src.api import create_response, handle_upload_file, handle_chat
from qdrant_client import QdrantClient
from app.src.utils import getEnvVariable, setEnvronVariable
from typing import Optional

# Set environment variables for API keys and tokenizer parallelism
setEnvronVariable("OPENAI_API_KEY", getEnvVariable("OPENAI_API_KEY"))
setEnvronVariable("TOKENIZERS_PARALLELISM", "false")

# Initialize FastAPI app
app = FastAPI()

def init_qdrant_client():
    """
    Initialize the Qdrant client with the specified host and port.
    """
    return QdrantClient("localhost", port=6333)
    
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), topic: str = Form(...), collection_name: str = Form(...)):
    """
    Endpoint to upload a PDF file and process it into vectors for retrieval.
    """
    # Validate required parameters
    if not topic:
        return create_response(status_code=400, message="topic parameter is required")
    if not collection_name:
        return create_response(status_code=400, detail="collection_name parameter is required")
    if not file:
        return create_response(status_code=400, detail="File is required")
    if not file.filename.endswith('.pdf'):
        return create_response(status_code=400, detail="Only PDF files are allowed")
    # Handle file upload and processing
    status, message, data = await handle_upload_file(file, init_qdrant_client(), topic, collection_name)
    return create_response(status, message, data)

@app.post("/chat/")
async def chat(
    question: str = Form(...), 
    collection_name: str = Form(...), 
    type: str = Form(...), 
    is_topic: str = Form(...), 
    memory: str = Form(...), 
    type_iterative: Optional[str] = Form("standard")
):
    """
    Endpoint to chat with the RAG system using a user query.
    """
    # Validate required parameters
    if not question:
        return create_response(status_code=400, message="question parameter is required")
    if not is_topic:
        return create_response(status_code=400, message="is_topic parameter is required")
    if not collection_name:
        return create_response(status_code=400, message="collection_name parameter is required")
    if not type:
        return create_response(status_code=400, message="type parameter is required")
    if not memory:
        return create_response(status_code=400, message="memory parameter is required")
    if not question.strip():
        return create_response(status_code=400, message="question cannot be empty")
    # Handle chat logic and return response
    status, message, data = await handle_chat(
        question=question, 
        client=init_qdrant_client(), 
        collection_name=collection_name, 
        type=type,
        is_topic=is_topic=="true",
        type_iterative=type_iterative,
        is_memmory=memory=="true"
    )
    return create_response(status, message, data)