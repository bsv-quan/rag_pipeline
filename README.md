# RAG Pipeline

## Overview
This repository contains a **Retrieval-Augmented Generation (RAG)** pipeline designed to process and retrieve information using a vector database (Qdrant) integrated with a FastAPI-based application. The pipeline supports uploading PDF files, vectorizing them, and enabling chat-based queries with memory and context awareness.

## Project Structure
```
app/
  __pycache__/
src/
  main.py
env/
qdrant_storage/
.gitignore
api_guide.markdown
docker-compose.yml
Dockerfile
knowledge_rag.markdown
README.md
requirements.txt
using_qdrant.md
using_uv_environment.md
using_uvicorn.md
```

## Prerequisites
- **Docker**: For containerizing the application and Qdrant vector database.
- **Python 3.8+**: For running the FastAPI application.
- **Environment Variables**: Configure API keys (e.g., `OPENAI_API_KEY`) in a `.env` file.

## Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd rag_pipeline
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory and add the necessary variables, e.g.:
```
OPENAI_API_KEY=your_openai_api_key
TOKENIZERS_PARALLELISM=false
```

### 3. Build and Run the Qdrant Vector Database
Use Docker Compose to start the Qdrant service:
```bash
docker-compose up -d
```
This command runs Qdrant in detached mode on `localhost:6333`.

### 4. Build the FastAPI Application
Build the Docker image for the FastAPI application:
```bash
docker build -t bot_rag_qdrant .
```

### 5. Run the FastAPI Application
Run the containerized FastAPI app, mapping port `8000`:
```bash
docker run -d -p 8000:8000 bot_rag_qdrant
```

### 6. Run with Environment File (Optional)
To include environment variables from the `.env` file:
```bash
docker run -d -p 8000:8000 --env-file .env bot_rag_qdrant
```

## Usage
- **Upload Endpoint**: Use `POST /upload/` to upload PDF files and store them as vectors in Qdrant (requires `topic` and `collection_name`).
- **Chat Endpoint**: Use `POST /chat/` to query the RAG system with parameters like `question`, `collection_name`, and `type`.

Refer to `api_guide.markdown` for detailed API documentation.

## Additional Resources
- [Using Qdrant](using_qdrant.md): Guide on integrating and managing the Qdrant vector database.
- [Using UV Environment](using_uv_environment.md): Instructions for setting up the UV environment.
- [Using Uvicorn](using_uvicorn.md): Details on running the app with Uvicorn.
- [Knowledge RAG](knowledge_rag.markdown): Overview of the RAG knowledge base.

## Contributing
Feel free to submit issues or pull requests. Ensure you follow the project structure and update `requirements.txt` if new dependencies are added.

## License
[MIT License](LICENSE) (or specify your preferred license).