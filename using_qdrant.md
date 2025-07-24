# Using Qdrant: A Guide to Vector Search and Storage

Qdrant is a high-performance vector database designed for efficient storage, search, and management of vector embeddings, commonly used for machine learning tasks like semantic search, recommendation systems, and similarity matching. This guide covers how to install, set up, and use Qdrant with Python.

## Prerequisites
- Python 3.8 or higher installed.
- A Python virtual environment (recommended for dependency isolation). You can create one using `uv`, `venv`, or another tool.
- Basic understanding of vector embeddings (e.g., from models like BERT, SentenceTransformers, or OpenAI embeddings).

## Installation
Install the Qdrant client for Python using pip or uv in your virtual environment:
```bash
pip install qdrant-client
```
or
```bash
uv pip install qdrant-client
```

For generating vector embeddings, you may also need a library like `sentence-transformers`:
```bash
pip install sentence-transformers
```

## Setting Up Qdrant
Qdrant can be run locally, in a Docker container, or via Qdrant Cloud. Below are the steps for a local setup using Docker.

1. **Run Qdrant with Docker**
   Pull and run Києва the Qdrant Docker image:
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```
   - Port `6333`: REST API endpoint.
   - Port `6334`: gRPC API endpoint.

2. **Verify Qdrant is Running**
   Check the Qdrant dashboard at `http://localhost:6333/dashboard` or send a request to the REST API:
   ```bash
   curl http://localhost:6333
   ```

## Basic Usage with Python
Below is an example of using the Qdrant Python client to create a collection, store vectors, and perform a search.

### Example: Storing and Searching Vectors
```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Qdrant client
client = QdrantClient("localhost", port=6333)

# Create a collection
collection_name = "example_collection"
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Generate sample embeddings using SentenceTransformers
model = SentenceTransformer("all-MiniLM-L6-v2")
texts = ["This is a sample text.", "Another example sentence."]
embeddings = model.encode(texts)

# Insert vectors into Qdrant
points = [
    PointStruct(id=idx, vector=embedding.tolist(), payload={"text": text})
    for idx, (embedding, text) in enumerate(zip(embeddings, texts))
]
client.upsert(collection_name=collection_name, points=points)

# Search for similar vectors
query_text = "Sample text query"
query_vector = model.encode([query_text])[0].tolist()
search_result = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=2
)

# Print search results
for result in search_result:
    print(f"ID: {result.id}, Score: {result.score}, Text: {result.payload['text']}")
```

### Explanation
- **Collection Creation**: A collection is created with a specified vector size (e.g., 384 for `all-MiniLM-L6-v2`) and distance metric (e.g., `COSINE`).
- **Vector Insertion**: Embeddings are generated using a model and stored with associated payloads (metadata).
- **Search**: A query vector is used to find the most similar vectors in the collection based on the chosen distance metric.

## Key Features
- **Vector Storage**: Efficiently stores high-dimensional vectors with payloads for metadata.
- **Search**: Supports fast similarity search using metrics like Cosine, Euclidean, or Dot Product.
- **Filtering**: Allows filtering results based on payload attributes.
- **Scalability**: Optimized for large-scale datasets with low-latency queries.
- **APIs**: Provides REST and gRPC APIs for flexibility.

## Common Use Cases
- **Semantic Search**: Find similar texts, images, or other data based on embeddings.
- **Recommendation Systems**: Suggest items based on vector similarity.
- **Clustering**: Group similar data points using vector embeddings.

## Configuration Options
- **Distance Metrics**: Choose from `COSINE`, `EUCLID`, or `DOT` for similarity calculations.
- **Payload Indexing**: Add indexes to payloads for faster filtering:
  ```python
  client.create_payload_index(
      collection_name=collection_name,
      field_name="text",
      field_schema="keyword"
  )
  ```
- **Sharding and Replication**: Configure for high availability and scalability in production (see Qdrant documentation).

## Running in Production
- **Qdrant Cloud**: Use Qdrant’s managed cloud service for easier scaling and maintenance.
- **Docker Compose**: Deploy with Docker Compose for multi-node setups.
- **Monitoring**: Enable metrics endpoint (`/metrics`) for performance monitoring.
- **Backups**: Regularly back up collections using Qdrant’s snapshot feature:
  ```bash
  curl -X POST http://localhost:6333/collections/{collection_name}/snapshots
  ```

## Troubleshooting
- **Connection Errors**: Ensure Qdrant is running and accessible at `localhost:6333`. Check Docker or firewall settings.
- **Vector Size Mismatch**: Verify that the vector size in the collection matches the embedding model’s output.
- **Performance Issues**: Increase memory allocation for Docker or optimize collection parameters (e.g., `hnsw_config`).
- **Payload Errors**: Ensure payloads are valid JSON and match the schema if indexed.

## Benefits of Qdrant
- **Performance**: Optimized for fast vector search with HNSW indexing.
- **Flexibility**: Supports multiple distance metrics and payload filtering.
- **Ease of Use**: Simple Python client and intuitive APIs.
- **Open Source**: Freely available with an active community.

## Additional Resources
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [SentenceTransformers Documentation](https://www.sbert.net/)