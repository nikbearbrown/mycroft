package com.earningssentiment.service;

import com.earningssentiment.domain.*;
import com.earningssentiment.dto.*;
import com.earningssentiment.exception.BadRequestException;
import com.earningssentiment.exception.ResourceNotFoundException;
import com.earningssentiment.repository.AnalysisJobRepository;
import com.earningssentiment.repository.TranscriptRepository;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Path;
import java.time.Year;
import java.util.List;
import java.util.Locale;

@Service
public class TranscriptService {
    private final TranscriptRepository transcriptRepository;
    private final AnalysisJobRepository analysisJobRepository;
    private final FileStorageService fileStorageService;
    private final ApplicationEventPublisher eventPublisher;

    public TranscriptService(
            TranscriptRepository transcriptRepository,
            AnalysisJobRepository analysisJobRepository,
            FileStorageService fileStorageService,
            ApplicationEventPublisher eventPublisher
    ) {
        this.transcriptRepository = transcriptRepository;
        this.analysisJobRepository = analysisJobRepository;
        this.fileStorageService = fileStorageService;
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public UploadTranscriptResponse upload(
            MultipartFile file,
            String companyName,
            String ticker,
            String quarter,
            Integer fiscalYear
    ) {
        validateMetadata(companyName, ticker, quarter, fiscalYear);
        Path storedPath = fileStorageService.store(file);
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCompletion(int status) {
                if (status != STATUS_COMMITTED) {
                    fileStorageService.deleteQuietly(storedPath);
                }
            }
        });
        try {
            Transcript transcript = new Transcript();
            transcript.setCompanyName(companyName.trim());
            transcript.setTicker(ticker.trim().toUpperCase(Locale.ROOT));
            transcript.setQuarter(quarter.trim().toUpperCase(Locale.ROOT));
            transcript.setFiscalYear(fiscalYear);
            transcript.setFilePath(storedPath.toString());
            transcript.setStatus(TranscriptStatus.QUEUED);
            transcriptRepository.save(transcript);

            AnalysisJob job = new AnalysisJob();
            job.setTranscript(transcript);
            job.setStatus(JobStatus.QUEUED);
            job.setProgress(0);
            job.setMessage("Waiting for an analysis worker");
            analysisJobRepository.save(job);

            eventPublisher.publishEvent(new AnalysisJobQueuedEvent(new AnalysisJobMessage(
                    job.getId(), transcript.getId(), transcript.getFilePath(), transcript.getCompanyName(),
                    transcript.getTicker(), transcript.getQuarter(), transcript.getFiscalYear())));

            return new UploadTranscriptResponse(transcript.getId(), job.getId(), job.getStatus().name());
        } catch (RuntimeException exception) {
            fileStorageService.deleteQuietly(storedPath);
            throw exception;
        }
    }

    @Transactional(readOnly = true)
    public List<TranscriptResponse> list() {
        return transcriptRepository.findAllByOrderByCreatedAtDesc().stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public TranscriptResponse get(Long id) {
        return toResponse(findTranscript(id));
    }

    @Transactional(readOnly = true)
    public Transcript findTranscript(Long id) {
        return transcriptRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Transcript " + id + " was not found"));
    }

    private TranscriptResponse toResponse(Transcript transcript) {
        return new TranscriptResponse(
                transcript.getId(), transcript.getCompanyName(), transcript.getTicker(), transcript.getQuarter(),
                transcript.getFiscalYear(), transcript.getStatus().name(), transcript.getCreatedAt());
    }

    private void validateMetadata(String companyName, String ticker, String quarter, Integer fiscalYear) {
        if (companyName == null || companyName.isBlank() || companyName.length() > 200) {
            throw new BadRequestException("companyName is required and must be 200 characters or fewer");
        }
        if (ticker == null || !ticker.trim().matches("[A-Za-z0-9.-]{1,20}")) {
            throw new BadRequestException("ticker must be 1-20 letters, numbers, dots, or dashes");
        }
        if (quarter == null || !quarter.trim().matches("(?i)Q[1-4]")) {
            throw new BadRequestException("quarter must be Q1, Q2, Q3, or Q4");
        }
        int maxYear = Year.now().getValue() + 2;
        if (fiscalYear == null || fiscalYear < 1990 || fiscalYear > maxYear) {
            throw new BadRequestException("fiscalYear must be between 1990 and " + maxYear);
        }
    }
}
