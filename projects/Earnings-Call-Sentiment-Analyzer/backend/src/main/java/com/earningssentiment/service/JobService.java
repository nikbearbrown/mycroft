package com.earningssentiment.service;

import com.earningssentiment.domain.AnalysisJob;
import com.earningssentiment.dto.JobResponse;
import com.earningssentiment.exception.ResourceNotFoundException;
import com.earningssentiment.repository.AnalysisJobRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class JobService {
    private final AnalysisJobRepository repository;

    public JobService(AnalysisJobRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public JobResponse get(Long id) {
        AnalysisJob job = repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Analysis job " + id + " was not found"));
        return new JobResponse(
                job.getId(), job.getTranscript().getId(), job.getStatus().name(), job.getProgress(),
                job.getMessage(), job.getErrorMessage(), job.getStartedAt(), job.getCompletedAt(), job.getCreatedAt());
    }
}
