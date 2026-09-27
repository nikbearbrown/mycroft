FROM python:3.10-slim

WORKDIR /code

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /code/app

# Expose the FastAPI default port
EXPOSE 8000

# Run the web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]