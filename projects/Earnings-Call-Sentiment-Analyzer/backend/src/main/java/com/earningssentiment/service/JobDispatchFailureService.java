package com.earningssentiment.service;

import com.earningssentiment.domain.JobStatus;
import com.earningssentiment.domain.TranscriptStatus;
import com.earningssentiment.repository.AnalysisJobRepository;
import com.earningssentiment.repository.TranscriptRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
public class JobDispatchFailureService {
    private final AnalysisJobRepository jobRepository;
    private final TranscriptRepository transcriptRepository;

    public JobDispatchFailureService(
            AnalysisJobRepository jobRepository,
            TranscriptRepository transcriptRepository
    ) {
        this.jobRepository = jobRepository;
        this.transcriptRepository = transcriptRepository;
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void markFailed(Long jobId, Long transcriptId, String detail) {
        jobRepository.findById(jobId).ifPresent(job -> {
            job.setStatus(JobStatus.FAILED);
            job.setProgress(0);
            job.setMessage("Could not dispatch analysis job");
            job.setErrorMessage(detail == null ? "RabbitMQ publish failed" : detail.substring(0, Math.min(4000, detail.length())));
            job.setCompletedAt(Instant.now());
        });
        transcriptRepository.findById(transcriptId).ifPresent(transcript ->
                transcript.setStatus(TranscriptStatus.FAILED));
    }
}
