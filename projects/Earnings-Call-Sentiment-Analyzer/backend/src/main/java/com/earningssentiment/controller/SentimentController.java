package com.earningssentiment.controller;

import com.earningssentiment.dto.AggregateSentimentResponse;
import com.earningssentiment.dto.ChunkSentimentResponse;
import com.earningssentiment.dto.SentimentSummaryResponse;
import com.earningssentiment.service.SentimentService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/transcripts/{transcriptId}/sentiment")
public class SentimentController {
    private final SentimentService sentimentService;

    public SentimentController(SentimentService sentimentService) {
        this.sentimentService = sentimentService;
    }

    @GetMapping("/summary")
    public SentimentSummaryResponse summary(@PathVariable Long transcriptId) {
        return sentimentService.getSummary(transcriptId);
    }

    @GetMapping("/chunks")
    public List<ChunkSentimentResponse> chunks(@PathVariable Long transcriptId) {
        return sentimentService.getChunks(transcriptId);
    }

    @GetMapping("/sections")
    public List<AggregateSentimentResponse> sections(@PathVariable Long transcriptId) {
        return sentimentService.getSections(transcriptId);
    }

    @GetMapping("/speakers")
    public List<AggregateSentimentResponse> speakers(@PathVariable Long transcriptId) {
        return sentimentService.getSpeakers(transcriptId);
    }
}
