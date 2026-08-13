package com.earningssentiment.dto;

public record ChunkSentimentResponse(
        Long chunkId,
        Integer chunkOrder,
        String sectionName,
        String speakerName,
        String speakerRole,
        String chunkText,
        String label,
        Double positiveScore,
        Double neutralScore,
        Double negativeScore,
        Double finalScore,
        String modelName
) {
}
