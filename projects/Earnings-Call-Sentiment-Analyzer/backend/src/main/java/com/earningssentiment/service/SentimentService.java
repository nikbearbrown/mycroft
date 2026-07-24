package com.earningssentiment.service;

import com.earningssentiment.domain.SentimentResult;
import com.earningssentiment.domain.SentimentSummary;
import com.earningssentiment.domain.TranscriptChunk;
import com.earningssentiment.dto.AggregateSentimentResponse;
import com.earningssentiment.dto.ChunkSentimentResponse;
import com.earningssentiment.dto.SentimentSummaryResponse;
import com.earningssentiment.exception.ResourceNotFoundException;
import com.earningssentiment.repository.SentimentSummaryRepository;
import com.earningssentiment.repository.TranscriptChunkRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.function.Function;

@Service
public class SentimentService {
    private final SentimentSummaryRepository summaryRepository;
    private final TranscriptChunkRepository chunkRepository;
    private final TranscriptService transcriptService;

    public SentimentService(
            SentimentSummaryRepository summaryRepository,
            TranscriptChunkRepository chunkRepository,
            TranscriptService transcriptService
    ) {
        this.summaryRepository = summaryRepository;
        this.chunkRepository = chunkRepository;
        this.transcriptService = transcriptService;
    }

    @Transactional(readOnly = true)
    public SentimentSummaryResponse getSummary(Long transcriptId) {
        transcriptService.findTranscript(transcriptId);
        SentimentSummary summary = summaryRepository.findByTranscriptId(transcriptId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Sentiment summary for transcript " + transcriptId + " is not available yet"));
        return new SentimentSummaryResponse(
                transcriptId, summary.getOverallLabel().name(), summary.getOverallScore(),
                summary.getPreparedRemarksScore(), summary.getQaScore(), summary.getManagementScore(),
                summary.getAnalystScore(), summary.getPositiveChunkCount(), summary.getNeutralChunkCount(),
                summary.getNegativeChunkCount(), summary.getCreatedAt());
    }

    @Transactional(readOnly = true)
    public List<ChunkSentimentResponse> getChunks(Long transcriptId) {
        transcriptService.findTranscript(transcriptId);
        return chunkRepository.findByTranscriptIdOrderByChunkOrderAsc(transcriptId).stream()
                .filter(chunk -> chunk.getSentimentResult() != null)
                .map(this::toChunkResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<AggregateSentimentResponse> getSections(Long transcriptId) {
        return aggregate(transcriptId, TranscriptChunk::getSectionName, ignored -> null);
    }

    @Transactional(readOnly = true)
    public List<AggregateSentimentResponse> getSpeakers(Long transcriptId) {
        return aggregate(
                transcriptId,
                chunk -> chunk.getSpeakerName() == null || chunk.getSpeakerName().isBlank()
                        ? "Unknown speaker" : chunk.getSpeakerName(),
                TranscriptChunk::getSpeakerRole);
    }

    private List<AggregateSentimentResponse> aggregate(
            Long transcriptId,
            Function<TranscriptChunk, String> nameExtractor,
            Function<TranscriptChunk, String> roleExtractor
    ) {
        transcriptService.findTranscript(transcriptId);
        Map<String, MutableAggregate> groups = new LinkedHashMap<>();
        for (TranscriptChunk chunk : chunkRepository.findByTranscriptIdOrderByChunkOrderAsc(transcriptId)) {
            SentimentResult result = chunk.getSentimentResult();
            if (result == null) continue;
            String name = nameExtractor.apply(chunk);
            String role = roleExtractor.apply(chunk);
            String key = name + "\u0000" + Objects.toString(role, "");
            groups.computeIfAbsent(key, ignored -> new MutableAggregate(name, role)).add(result);
        }
        return groups.values().stream()
                .map(MutableAggregate::toResponse)
                .sorted(Comparator.comparingLong(AggregateSentimentResponse::chunkCount).reversed())
                .toList();
    }

    private ChunkSentimentResponse toChunkResponse(TranscriptChunk chunk) {
        SentimentResult result = chunk.getSentimentResult();
        return new ChunkSentimentResponse(
                chunk.getId(), chunk.getChunkOrder(), chunk.getSectionName(), chunk.getSpeakerName(),
                chunk.getSpeakerRole(), chunk.getChunkText(), result.getLabel().name(), result.getPositiveScore(),
                result.getNeutralScore(), result.getNegativeScore(), result.getFinalScore(), result.getModelName());
    }

    private static class MutableAggregate {
        private final String name;
        private final String role;
        private double scoreTotal;
        private long positive;
        private long neutral;
        private long negative;

        private MutableAggregate(String name, String role) {
            this.name = name;
            this.role = role;
        }

        void add(SentimentResult result) {
            scoreTotal += result.getFinalScore();
            switch (result.getLabel()) {
                case POSITIVE -> positive++;
                case NEUTRAL -> neutral++;
                case NEGATIVE -> negative++;
            }
        }

        AggregateSentimentResponse toResponse() {
            long total = positive + neutral + negative;
            return new AggregateSentimentResponse(
                    name, role, total == 0 ? 0 : scoreTotal / total, positive, neutral, negative, total);
        }
    }
}
