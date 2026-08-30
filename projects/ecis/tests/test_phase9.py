"""Tests for speaker weighting, chunk quality, and retrospective trend labels."""

from datetime import date

from ecis.extraction.chunk_quality import completeness_score, score_chunk, speaker_transition_score
from ecis.extraction.speaker_roles import classify_speaker, speaker_weight
from ecis.extraction.temporal_linking import assign_trends, label_trend
from ecis.extraction.triangulator import triangulate_chunk
from ecis.schemas.signal import GuidanceDirection


class TestSpeakerRoles:
    def test_cfo_and_analyst(self):
        assert classify_speaker("Jane Doe, Chief Financial Officer") == "cfo"
        assert classify_speaker("Unidentified Analyst") == "analyst"
        assert classify_speaker("Operator") == "operator"
        assert classify_speaker("John Smith") == "unknown"

    def test_weights(self):
        assert speaker_weight("CFO") == 1.0
        assert speaker_weight("equity analyst") == 0.3
        assert speaker_weight("Operator") == 0.0
        assert speaker_weight("John Smith") == 0.8


class TestChunkQuality:
    def test_complete_chunk_scores_high(self):
        text = (
            "We are raising our full year revenue guidance based on stronger "
            "data center demand and improved visibility into the second half. "
        ) * 8
        scores = score_chunk({"text": text})
        assert scores["chunk_quality"] > 0.7
        assert scores["completeness"] == 1.0

    def test_transitions_penalise_multi_speaker(self):
        one = speaker_transition_score("[SPEAKER: CFO] We raised guidance.")
        many = speaker_transition_score(
            "[SPEAKER: CFO] Hello.\n[SPEAKER: CEO] Thanks.\n[SPEAKER: Analyst] Question."
        )
        assert one == 1.0
        assert many < one

    def test_mid_sentence_completeness(self):
        assert completeness_score("and we continue to see demand across") == 0.2


class TestTrendLabels:
    def test_label_trend(self):
        assert label_trend("raised", None) == "single"
        assert label_trend("raised", "raised") == "consecutive_raise"
        assert label_trend("lowered", "lowered") == "consecutive_lower"
        assert label_trend("maintained", "maintained") == "stable_maintained"
        assert label_trend("raised", "lowered") == "reversal"

    def test_assign_trends_uses_prior_quarter(self):
        rows = [
            {"signal_id": 1, "ticker": "TICKER", "direction": "raised",
             "confidence_raw": 0.9, "transcript_date": "2024-01-15"},
            {"signal_id": 2, "ticker": "TICKER", "direction": "raised",
             "confidence_raw": 0.8, "transcript_date": "2024-04-15"},
            {"signal_id": 3, "ticker": "TICKER", "direction": "lowered",
             "confidence_raw": 0.7, "transcript_date": "2024-07-15"},
        ]
        labels = assign_trends(rows)
        assert labels[1] == "single"
        assert labels[2] == "consecutive_raise"
        assert labels[3] == "reversal"


class TestTriangulatorEnrichment:
    def test_analyst_downweights_confidence(self):
        chunk = {
            "ticker": "TICKER",
            "text": "We are raising full year revenue guidance on stronger demand. " * 10,
            "section_label": "qa",
            "speaker": "Unidentified Analyst",
            "transcript_date": "2025-01-15",
            "chunk_index": 0,
            "char_start": 0,
            "char_end": 80,
        }
        kw = {"matched": True, "direction": "raised", "confidence": 1.0, "phrases": ["raising guidance"]}
        cfo_chunk = {**chunk, "speaker": "Jane Doe, CFO"}
        analyst = triangulate_chunk(chunk, kw, None, None)
        cfo = triangulate_chunk(cfo_chunk, kw, None, None)
        assert analyst is not None and cfo is not None
        assert analyst.speaker_role == "analyst"
        assert cfo.speaker_role == "cfo"
        assert analyst.confidence_raw < cfo.confidence_raw
        assert cfo.direction == GuidanceDirection.RAISED
