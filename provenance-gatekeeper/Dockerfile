FROM python:3.10-slim

WORKDIR /code

# Install system dependencies required for C++ compilation (bcrypt / chromadb)
RUN apt-get update && apt-get install -y build-essential curl

COPY requirements.txt .

# Upgrade pip first so it handles modern wheel metadata cleanly
RUN pip install --upgrade pip

# Install CPU-only PyTorch first to avoid 1GB+ of unused NVIDIA/Triton packages
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /code/app

# Expose the FastAPI default port
EXPOSE 8000

# Run the web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]