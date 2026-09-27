FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py graph.py llm.py obs.py test_graph.py ./
RUN python test_graph.py
RUN useradd -u 10001 -m app
USER app
CMD ["python", "-u", "app.py"]
