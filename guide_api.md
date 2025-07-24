# API Guide for RAG System

This guide provides detailed instructions for interacting with the RAG (Retrieval-Augmented Generation) system's API endpoints using FastAPI. The API allows users to upload PDF files for processing into vectors and query the system for responses based on the uploaded data.

## Prerequisites
- **FastAPI**: The API is built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python.
- **Qdrant**: A vector search engine used for storing and retrieving vectorized data.
- **Environment Variables**:
  - `OPENAI_API_KEY`: Required for accessing OpenAI's API.
  - `TOKENIZERS_PARALLELISM`: Set to `"false"` to disable tokenizer parallelism.

## Setup
The API initializes a FastAPI application and a Qdrant client to interact with a Qdrant server running on `localhost:6333`. Ensure the Qdrant server is running before using the API.

### Environment Variables
The following environment variables are configured at startup:
```python
setEnvronVariable("OPENAI_API_KEY", getEnvVariable("OPENAI_API_KEY"))
setEnvronVariable("TOKENIZERS_PARALLELISM", "false")
```

## Endpoints

### 1. Upload PDF Endpoint
This endpoint allows users to upload a PDF file, which is processed into vectors and stored in a specified Qdrant collection.

#### Endpoint
`POST /upload/`

#### Parameters
| Parameter         | Type          | Description                                                                 | Required |
|-------------------|---------------|-----------------------------------------------------------------------------|----------|
| `file`            | `UploadFile`  | The PDF file to be uploaded and processed into vectors.                      | Yes      |
| `topic`           | `str`         | The topic associated with the uploaded file.                                | Yes      |
| `collection_name` | `str`         | The name of the Qdrant collection where the vectors will be stored.         | Yes      |

#### Request Example
```bash
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@/path/to/document.pdf" \
  -F "topic=example_topic" \
  -F "collection_name=example_collection"
```

#### Response
- **Success**: Returns a response with status, message, and data from the file processing.
- **Error**: Returns a 400 status code with an error message if:
  - The `topic` parameter is missing or empty.
  - The `collection_name` parameter is missing or empty.
  - No file is provided.
  - The uploaded file is not a PDF.

#### Response Format
```json
{
  "status": <status_code>,
  "message": "<message>",
  "data": <data>
}
```

#### Example Error Response
```json
{
  "status": 400,
  "message": "Only PDF files are allowed",
  "data": null
}
```

### 2. Chat Endpoint
This endpoint allows users to interact with the RAG system by submitting a query and receiving a response based on the data stored in the Qdrant collection.

#### Endpoint
`POST /chat/`

#### Parameters
| Parameter         | Type          | Description                                                                 | Required | Default Value |
|-------------------|---------------|-----------------------------------------------------------------------------|----------|---------------|
| `question`        | `str`         | The user's query to the RAG system.                                         | Yes      | -             |
| `collection_name` | `str`         | The name of the Qdrant collection to query.                                 | Yes      | -             |
| `type`            | `str`         | The type of RAG processing (e.g., standard, iterative).                     | Yes      | -             |
| `is_topic`        | `str`         | Indicates if the query is topic-specific (`"true"` or `"false"`).           | Yes      | -             |
| `memory`          | `str`         | Indicates if memory (conversation history) should be used (`"true"` or `"false"`). | Yes      | -             |
| `type_iterative`  | `Optional[str]` | Specifies the iterative RAG type (if applicable).                         | No       | `"standard"`  |

#### Request Example
```bash
curl -X POST "http://localhost:8000/chat/" \
  -F "question=What is the capital of France?" \
  -F "collection_name=example_collection" \
  -F "type=standard" \
  -F "is_topic=true" \
  -F "memory=true" \
  -F "type_iterative=standard"
```

#### Response
- **Success**: Returns a response with status, message, and data from the RAG system.
- **Error**: Returns a 400 status code with an error message if:
  - The `question` parameter is missing or empty.
  - The `is_topic` parameter is missing.
  - The `collection_name` parameter is missing.
  - The `type` parameter is missing.
  - The `memory` parameter is missing.

#### Response Format
```json
{
  "status": <status_code>,
  "message": "<message>",
  "data": <data>
}
```

#### Example Error Response
```json
{
  "status": 400,
  "message": "question parameter is required",
  "data": null
}
```

## Implementation Details
- **Qdrant Client**: The `init_qdrant_client` function initializes a Qdrant client connected to `localhost:6333` for vector storage and retrieval.
- **Helper Functions**:
  - `create_response`: Generates a standardized response with status, message, and data.
  - `handle_upload_file`: Processes the uploaded PDF file and stores its vectors in the specified Qdrant collection.
  - `handle_chat`: Handles the chat logic, retrieving relevant data from Qdrant and generating a response using the RAG system.

## Notes
- Ensure the Qdrant server is running on `localhost:6333` before making API requests.
- Only PDF files are supported for the `/upload/` endpoint.
- The `is_topic` and `memory` parameters must be provided as strings (`"true"` or `"false"`) in the `/chat/` endpoint.
- The API uses environment variables for configuration, so ensure they are set correctly before running the application.