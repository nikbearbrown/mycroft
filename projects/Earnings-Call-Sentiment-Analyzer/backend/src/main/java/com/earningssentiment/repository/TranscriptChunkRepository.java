package com.earningssentiment.repository;

import com.earningssentiment.domain.TranscriptChunk;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TranscriptChunkRepository extends JpaRepository<TranscriptChunk, Long> {
    @EntityGraph(attributePaths = "sentimentResult")
    List<TranscriptChunk> findByTranscriptIdOrderByChunkOrderAsc(Long transcriptId);
}
