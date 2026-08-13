package com.earningssentiment.repository;

import com.earningssentiment.domain.SentimentSummary;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface SentimentSummaryRepository extends JpaRepository<SentimentSummary, Long> {
    Optional<SentimentSummary> findByTranscriptId(Long transcriptId);
}
