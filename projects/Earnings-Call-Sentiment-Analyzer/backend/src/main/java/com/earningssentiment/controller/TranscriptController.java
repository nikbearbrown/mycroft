package com.earningssentiment.controller;

import com.earningssentiment.dto.TranscriptResponse;
import com.earningssentiment.dto.UploadTranscriptResponse;
import com.earningssentiment.service.TranscriptService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/transcripts")
public class TranscriptController {
    private final TranscriptService transcriptService;

    public TranscriptController(TranscriptService transcriptService) {
        this.transcriptService = transcriptService;
    }

    @PostMapping(consumes = "multipart/form-data")
    @ResponseStatus(HttpStatus.CREATED)
    public UploadTranscriptResponse upload(
            @RequestParam MultipartFile file,
            @RequestParam String companyName,
            @RequestParam String ticker,
            @RequestParam String quarter,
            @RequestParam Integer fiscalYear
    ) {
        return transcriptService.upload(file, companyName, ticker, quarter, fiscalYear);
    }

    @GetMapping
    public List<TranscriptResponse> list() {
        return transcriptService.list();
    }

    @GetMapping("/{transcriptId}")
    public TranscriptResponse get(@PathVariable Long transcriptId) {
        return transcriptService.get(transcriptId);
    }
}
