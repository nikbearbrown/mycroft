package com.earningssentiment.dto;

import java.time.Instant;

public record TranscriptResponse(
        Long id,
        String companyName,
        String ticker,
        String quarter,
        Integer fiscalYear,
        String status,
        Instant createdAt
) {
}
