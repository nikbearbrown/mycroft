FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY grader.py .
RUN useradd -u 10001 -m app
USER app
CMD ["python", "-u", "grader.py"]
