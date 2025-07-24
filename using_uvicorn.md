# Using Uvicorn: A Guide to Running ASGI Applications

Uvicorn is a lightning-fast ASGI (Asynchronous Server Gateway Interface) server implementation for Python, designed to run asynchronous web applications, such as those built with FastAPI or Starlette. This guide covers how to install, configure, and use Uvicorn to serve your Python web applications.

## Prerequisites
- Python 3.7 or higher installed.
- A Python virtual environment (recommended for dependency isolation). You can create one using `uv`, `venv`, or another tool.
- An ASGI-compatible web application (e.g., built with FastAPI or Starlette).

## Installation
Install Uvicorn using pip or uv in your virtual environment:
```bash
pip install uvicorn
```
or
```bash
uv pip install uvicorn
```

For additional features like WebSocket support or automatic reloading, install optional dependencies:
```bash
pip install "uvicorn[standard]"
```

## Basic Usage
To run an ASGI application with Uvicorn, you need a Python module containing your application. For example, suppose you have a FastAPI app in `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
```

Run the application with Uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

- `main:app`: Refers to the module (`main`) and the ASGI application instance (`app`).
- `--host 127.0.0.1`: Binds the server to localhost.
- `--port 8000`: Specifies the port to listen on.

Once running, visit `http://127.0.0.1:8000` in your browser to see the application.

## Common Configuration Options
Uvicorn provides several command-line options to customize its behavior:
- **Reload on Code Changes** (useful for development):
  ```bash
  uvicorn main:app --reload
  ```
  Enables auto-reload when code changes are detected (requires `uvicorn[standard]`).
- **Workers** (for production):
  ```bash
  uvicorn main:app --workers 4
  ```
  Runs multiple worker processes to handle concurrent requests.
- **Custom Host/Port**:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8080
  ```
  Binds to all network interfaces (e.g., for external access).
- **SSL Support**:
  ```bash
  uvicorn main:app --ssl-keyfile key.pem --ssl-certfile cert.pem
  ```
  Enables HTTPS with the specified key and certificate files.

## Running Programmatically
You can run Uvicorn programmatically within a Python script:
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

This is useful for integrating Uvicorn into larger applications or custom workflows.

## Production Considerations
- **Use a Process Manager**: In production, use a process manager like Gunicorn with Uvicorn workers:
  ```bash
  gunicorn -k uvicorn.workers.UvicornWorker main:app
  ```
- **Logging**: Enable access and error logs with `--log-level`:
  ```bash
  uvicorn main:app --log-level info
  ```
- **Environment Variables**: Configure Uvicorn via environment variables (e.g., `UVICORN_HOST`, `UVICORN_PORT`).
- **Scaling**: Use `--workers` or deploy behind a reverse proxy like Nginx for load balancing.

## Troubleshooting
- **Module Not Found**: Ensure the module and app name are correct (e.g., `main:app`) and the virtual environment is activated.
- **Port Conflicts**: If the port is in use, try a different port or terminate the conflicting process.
- **Performance Issues