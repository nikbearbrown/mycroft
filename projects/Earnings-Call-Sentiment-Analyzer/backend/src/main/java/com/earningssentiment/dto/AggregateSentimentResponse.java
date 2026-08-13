package com.earningssentiment.dto;

public record AggregateSentimentResponse(
        String name,
        String role,
        Double score,
        long positiveCount,
        long neutralCount,
        long negativeCount,
        long chunkCount
) {
}
