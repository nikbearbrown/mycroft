from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import logging
from typing import Iterator

import psycopg

from .config import Settings
from .text_processing import ParsedChunk


LOGGER = logging.getLogger(__name__)


class Database:
    def __init__(self, settings: Settings) -> None:
        self.connection_parameters = {
            "host": settings.db_host,
            "port": settings.db_port,
            "dbname": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password,
            "connect_timeout": 10,
        }

    @contextmanager
    def connect(self) -> Iterator[psycopg.Connection]:
        with psycopg.connect(**self.connection_parameters) as connection:
            yield connection

    def get_job_status(self, job_id: int, transcript_id: int) -> str | None:
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT status FROM analysis_jobs WHERE id = %s AND transcript_id = %s",
                (job_id, transcript_id),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def mark_processing(self, job_id: int, transcript_id: int) -> None:
        now = datetime.now(timezone.utc)
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analysis_jobs
                SET status = 'PROCESSING', progress = 5, message = 'Reading transcript',
                    error_message = NULL, started_at = COALESCE(started_at, %s), completed_at = NULL
                WHERE id = %s AND transcript_id = %s AND status <> 'COMPLETED'
                """,
                (now, job_id, transcript_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(
                    f"Job {job_id} is missing, already completed, or does not belong to transcript {transcript_id}"
                )
            cursor.execute(
                "UPDATE transcripts SET status = 'PROCESSING' WHERE id = %s", (transcript_id,)
            )

    def update_progress(self, job_id: int, progress: int, message: str) -> None:
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analysis_jobs SET progress = %s, message = %s
                WHERE id = %s AND status = 'PROCESSING'
                """,
                (progress, message, job_id),
            )

    def save_results(
        self,
        job_id: int,
        transcript_id: int,
        chunks: list[ParsedChunk],
        scores: list[dict[str, float | str]],
        model_name: str,
    ) -> None:
        if len(chunks) != len(scores):
            raise ValueError("Chunk and score counts do not match")

        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute("DELETE FROM sentiment_summaries WHERE transcript_id = %s", (transcript_id,))
            cursor.execute("DELETE FROM transcript_chunks WHERE transcript_id = %s", (transcript_id,))

            for chunk, score in zip(chunks, scores, strict=True):
                cursor.execute(
                    """
                    INSERT INTO transcript_chunks
                        (transcript_id, section_name, speaker_name, speaker_role, chunk_text, chunk_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        transcript_id,
                        chunk.section_name,
                        chunk.speaker_name,
                        chunk.speaker_role,
                        chunk.chunk_text,
                        chunk.chunk_order,
                    ),
                )
                chunk_id = cursor.fetchone()[0]
                cursor.execute(
                    """
                    INSERT INTO sentiment_results
                        (chunk_id, label, positive_score, neutral_score, negative_score,
                         final_score, model_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk_id,
                        score["label"],
                        score["positive_score"],
                        score["neutral_score"],
                        score["negative_score"],
                        score["final_score"],
                        model_name,
                    ),
                )

            summary = calculate_summary(chunks, scores)
            cursor.execute(
                """
                INSERT INTO sentiment_summaries
                    (transcript_id, overall_label, overall_score, prepared_remarks_score,
                     qa_score, management_score, analyst_score, positive_chunk_count,
                     neutral_chunk_count, negative_chunk_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    transcript_id,
                    summary["overall_label"],
                    summary["overall_score"],
                    summary["prepared_remarks_score"],
                    summary["qa_score"],
                    summary["management_score"],
                    summary["analyst_score"],
                    summary["positive_chunk_count"],
                    summary["neutral_chunk_count"],
                    summary["negative_chunk_count"],
                ),
            )
            cursor.execute(
                """
                UPDATE analysis_jobs
                SET status = 'COMPLETED', progress = 100, message = 'Analysis complete',
                    error_message = NULL, completed_at = %s
                WHERE id = %s AND transcript_id = %s
                """,
                (datetime.now(timezone.utc), job_id, transcript_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Analysis job {job_id} disappeared while results were being saved")
            cursor.execute(
                "UPDATE transcripts SET status = 'COMPLETED' WHERE id = %s", (transcript_id,)
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Transcript {transcript_id} disappeared while results were being saved")

    def mark_failed(self, job_id: int, transcript_id: int, error: str) -> bool:
        safe_error = error[:4000]
        try:
            with self.connect() as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE analysis_jobs
                    SET status = 'FAILED', message = 'Analysis failed', error_message = %s,
                        completed_at = %s
                    WHERE id = %s AND transcript_id = %s AND status <> 'COMPLETED'
                    """,
                    (safe_error, datetime.now(timezone.utc), job_id, transcript_id),
                )
                if cursor.rowcount == 1:
                    cursor.execute(
                        "UPDATE transcripts SET status = 'FAILED' WHERE id = %s",
                        (transcript_id,),
                    )
            return True
        except Exception:
            LOGGER.exception("Could not persist failure state for job %s", job_id)
            return False


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def calculate_summary(
    chunks: list[ParsedChunk], scores: list[dict[str, float | str]]
) -> dict[str, float | int | str | None]:
    pairs = list(zip(chunks, scores, strict=True))
    all_scores = [float(score["final_score"]) for _, score in pairs]
    overall = _average(all_scores) or 0.0
    label_counts = {
        label: sum(1 for _, score in pairs if score["label"] == label)
        for label in ("POSITIVE", "NEUTRAL", "NEGATIVE")
    }

    def score_for(predicate) -> float | None:
        return _average(
            [float(score["final_score"]) for chunk, score in pairs if predicate(chunk)]
        )

    overall_label = "POSITIVE" if overall > 0.05 else "NEGATIVE" if overall < -0.05 else "NEUTRAL"
    return {
        "overall_label": overall_label,
        "overall_score": overall,
        "prepared_remarks_score": score_for(lambda chunk: chunk.section_name == "PREPARED_REMARKS"),
        "qa_score": score_for(lambda chunk: chunk.section_name == "Q_AND_A"),
        "management_score": score_for(lambda chunk: chunk.speaker_role in {"CEO", "CFO"}),
        "analyst_score": score_for(lambda chunk: chunk.speaker_role == "ANALYST"),
        "positive_chunk_count": label_counts["POSITIVE"],
        "neutral_chunk_count": label_counts["NEUTRAL"],
        "negative_chunk_count": label_counts["NEGATIVE"],
    }
