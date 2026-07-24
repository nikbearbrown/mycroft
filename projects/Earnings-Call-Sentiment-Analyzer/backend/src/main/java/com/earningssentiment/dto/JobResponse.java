package com.earningssentiment.dto;

import java.time.Instant;

public record JobResponse(
        Long id,
        Long transcriptId,
        String status,
        Integer progress,
        String message,
        String errorMessage,
        Instant startedAt,
        Instant completedAt,
        Instant createdAt
) {
}
