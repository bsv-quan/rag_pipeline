from fastapi import UploadFile
from app.src.utils import extract_pdf_text
from app.src.qdrant import qbrant_service as qbrant
from app.src.process import preparing_data
from qdrant_client import QdrantClient
import aiofiles
import tempfile
import os

async def handle_upload_file(file: UploadFile, client: QdrantClient, topic: str, collection_name: str):
    # Sanitize context to prevent path traversal
    topic = topic.replace("/", "_").replace("\\", "_")
    # Create a temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Save uploaded content to temporary file
            async with aiofiles.open(temp_file.name, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Extract text and process to vectors
            extracted_text = extract_pdf_text(temp_file.name)
            if not extracted_text.strip():
                return 400, "No text could be extracted from the PDF", None
            qbrant.init_collection(client=client, collection_name=collection_name)
            ids, vectors, chunks = preparing_data(extracted_text)
            print(f"Extracted {len(chunks)} chunks from PDF.")
            qbrant.add_text(client, collection_name, ids, vectors, chunks, topic=topic)
    
    except Exception as e:
            return 500, f"Error processing PDF: {str(e)}", None

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    return 200, "PDF processed and vectors saved successfully", {
        "filename": file.filename,
        "topic": topic,
        "collection_name": collection_name,
        "message": "PDF processed and vectors saved successfully"
    }