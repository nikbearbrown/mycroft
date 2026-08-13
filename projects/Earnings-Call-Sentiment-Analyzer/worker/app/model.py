from __future__ import annotations

import logging

from transformers import pipeline


LOGGER = logging.getLogger(__name__)


class FinBertAnalyzer:
    def __init__(self, model_name: str, batch_size: int = 16) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        LOGGER.info("Loading FinBERT model %s", model_name)
        self.classifier = pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            device=-1,
        )
        LOGGER.info("FinBERT model loaded")

    def analyze(self, texts: list[str]) -> list[dict[str, float | str]]:
        if not texts:
            return []
        raw_results = self.classifier(
            texts,
            top_k=None,
            batch_size=self.batch_size,
            truncation=True,
            max_length=512,
        )
        results: list[dict[str, float | str]] = []
        for raw in raw_results:
            scores = {item["label"].lower(): float(item["score"]) for item in raw}
            positive = scores.get("positive", 0.0)
            neutral = scores.get("neutral", 0.0)
            negative = scores.get("negative", 0.0)
            label = max(
                (("POSITIVE", positive), ("NEUTRAL", neutral), ("NEGATIVE", negative)),
                key=lambda item: item[1],
            )[0]
            results.append(
                {
                    "label": label,
                    "positive_score": positive,
                    "neutral_score": neutral,
                    "negative_score": negative,
                    "final_score": positive - negative,
                }
            )
        return results
