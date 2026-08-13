package com.earningssentiment.controller;

import com.earningssentiment.dto.JobResponse;
import com.earningssentiment.service.JobService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/jobs")
public class JobController {
    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    @GetMapping("/{jobId}")
    public JobResponse get(@PathVariable Long jobId) {
        return jobService.get(jobId);
    }
}
