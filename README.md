# rag_pipeline
Retrieval-Augmented Generation (RAG) Pipeline

# build qdrant vector db
docker-compose up -d

# build fast api to docker
docker build -t bot_rag_qdrant . 

# run fast api
docker run -d -p 8000:8000 bot_rag_qdrant

# run fast api with .env file
docker run -d -p 8000:8000 --env-file .env bot_rag_qdrant