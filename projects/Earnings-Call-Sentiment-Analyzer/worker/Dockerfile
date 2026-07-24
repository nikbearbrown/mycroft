FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models/huggingface

WORKDIR /app
RUN addgroup --system worker && adduser --system --ingroup worker worker \
    && mkdir -p /models/huggingface /uploads \
    && chown -R worker:worker /app /models /uploads
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 \
    && pip install --no-cache-dir -r requirements.txt
COPY app ./app
USER worker
CMD ["python", "-m", "app.main"]
