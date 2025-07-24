from fastapi import FastAPI, File, UploadFile, Form
from app.src.api import create_response, handle_upload_file, handle_chat
from qdrant_client import QdrantClient
from app.src.utils import getEnvVariable, setEnvronVariable

# Set environment variables
setEnvronVariable("OPENAI_API_KEY", getEnvVariable("OPENAI_API_KEY"))
setEnvronVariable("TOKENIZERS_PARALLELISM", "false")

app = FastAPI()
def init_qdrant_client():
    """
    Initialize the Qdrant client with the specified host and port.
    """
    return QdrantClient("localhost", port=6333)
    
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), topic: str = Form(...), collection_name: str = Form(...)):
    """
    Upload a PDF file, process it to vectors
    """
    if not topic:
        return create_response(status_code=400, message="topic parameter is required")
    if not collection_name:
        return create_response(status_code=400, detail="collection_name parameter is required")
    if not file:
        return create_response(status_code=400, detail="File is required")
    if not file.filename.endswith('.pdf'):
        return create_response(status_code=400, detail="Only PDF files are allowed")
    status, message, data = await handle_upload_file(file, init_qdrant_client(), topic, collection_name)
    return create_response(status, message, data)

@app.post("/chat/")
async def chat(question: str = Form(...), collection_name: str = Form(...), type: str = Form(...), is_topic: str = Form(...)):
    """
    Chat with the RAG system using a query
    """
    if not question:
        return create_response(status_code=400, message="question parameter is required")
    if not is_topic:
        return create_response(status_code=400, message="is_topic parameter is required")
    if not collection_name:
        return create_response(status_code=400, message="collection_name parameter is required")
    if not type:
        return create_response(status_code=400, message="type parameter is required")
    if not question.strip():
        return create_response(status_code=400, message="question cannot be empty")
    status, message, data = await handle_chat(
        question=question, 
        client=init_qdrant_client(), 
        collection_name=collection_name, 
        type=type,
        is_topic=is_topic=="true")
    return create_response(status, message, data)