package com.earningssentiment.dto;

import java.time.Instant;

public record SentimentSummaryResponse(
        Long transcriptId,
        String overallLabel,
        Double overallScore,
        Double preparedRemarksScore,
        Double qaScore,
        Double managementScore,
        Double analystScore,
        Integer positiveChunkCount,
        Integer neutralChunkCount,
        Integer negativeChunkCount,
        Instant createdAt
) {
}
