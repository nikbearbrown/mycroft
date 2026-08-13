from __future__ import annotations

import json
import logging
import signal
import time

import pika
import psycopg

from .config import Settings
from .database import Database
from .model import FinBertAnalyzer
from .text_processing import parse_transcript
from .transcript_reader import read_transcript


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)
QUEUE_NAME = "sentiment.analysis.queue"
EXCHANGE_NAME = "sentiment.exchange"
ROUTING_KEY = "sentiment.analysis"


class SentimentWorker:
    def __init__(self, settings: Settings, analyzer: FinBertAnalyzer) -> None:
        self.settings = settings
        self.database = Database(settings)
        self.analyzer = analyzer
        self.connection: pika.BlockingConnection | None = None

    def process(self, channel, method, _properties, body: bytes) -> None:
        job_id: int | None = None
        transcript_id: int | None = None
        results_committed = False
        try:
            message = json.loads(body)
            job_id = int(message["jobId"])
            transcript_id = int(message["transcriptId"])
            file_path = self.settings.resolve_upload_path(message["filePath"])
            LOGGER.info("Received analysis job %s for transcript %s", job_id, transcript_id)

            status = self.database.get_job_status(job_id, transcript_id)
            if status is None:
                raise ValueError(f"Analysis job {job_id} does not exist")
            if status == "COMPLETED":
                LOGGER.info("Job %s is already completed; acknowledging duplicate message", job_id)
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

            self.database.mark_processing(job_id, transcript_id)
            raw_text = read_transcript(file_path)
            self.database.update_progress(job_id, 20, "Detecting sections and speakers")
            chunks = parse_transcript(raw_text)
            if not chunks:
                raise ValueError("No analyzable text was found in the transcript")

            self.database.update_progress(job_id, 40, f"Scoring {len(chunks)} evidence chunks with FinBERT")
            scores = self.analyzer.analyze([chunk.chunk_text for chunk in chunks])
            self.database.update_progress(job_id, 85, "Saving evidence and calculating summary")
            self.database.save_results(
                job_id, transcript_id, chunks, scores, self.settings.model_name
            )
            results_committed = True
            channel.basic_ack(delivery_tag=method.delivery_tag)
            LOGGER.info("Completed analysis job %s with %s chunks", job_id, len(chunks))
        except Exception as exception:
            LOGGER.exception("Analysis job failed")
            if results_committed:
                self._nack_safely(channel, method.delivery_tag, requeue=True)
                return
            if isinstance(exception, psycopg.OperationalError):
                self._nack_safely(channel, method.delivery_tag, requeue=True)
                return

            failure_persisted = True
            if job_id is not None and transcript_id is not None:
                failure_persisted = self.database.mark_failed(job_id, transcript_id, str(exception))
            self._nack_safely(channel, method.delivery_tag, requeue=not failure_persisted)

    @staticmethod
    def _nack_safely(channel, delivery_tag: int, requeue: bool) -> None:
        try:
            channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)
        except Exception:
            LOGGER.exception("Could not reject RabbitMQ delivery; broker recovery will requeue it")

    def run(self) -> None:
        credentials = pika.PlainCredentials(
            self.settings.rabbitmq_user, self.settings.rabbitmq_password
        )
        parameters = pika.ConnectionParameters(
            host=self.settings.rabbitmq_host,
            port=self.settings.rabbitmq_port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )
        self.connection = pika.BlockingConnection(parameters)
        channel = self.connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct", durable=True)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=self.process, auto_ack=False)
        LOGGER.info("Waiting for analysis jobs")
        channel.start_consuming()

    def stop(self, *_args) -> None:
        LOGGER.info("Stopping worker")
        if self.connection and self.connection.is_open:
            self.connection.close()


def main() -> None:
    settings = Settings()
    analyzer: FinBertAnalyzer | None = None
    while analyzer is None:
        try:
            analyzer = FinBertAnalyzer(settings.model_name, settings.model_batch_size)
        except Exception:
            LOGGER.exception("Model initialization failed; retrying in 10 seconds")
            time.sleep(10)

    while True:
        worker: SentimentWorker | None = None
        try:
            worker = SentimentWorker(settings, analyzer)
            signal.signal(signal.SIGTERM, worker.stop)
            signal.signal(signal.SIGINT, worker.stop)
            worker.run()
            return
        except KeyboardInterrupt:
            return
        except Exception:
            LOGGER.exception("Worker connection failed; retrying in 10 seconds")
            time.sleep(10)


if __name__ == "__main__":
    main()
