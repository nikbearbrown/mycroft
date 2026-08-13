package com.earningssentiment.dto;

public record AnalysisJobMessage(
        Long jobId,
        Long transcriptId,
        String filePath,
        String companyName,
        String ticker,
        String quarter,
        Integer fiscalYear
) {
}
