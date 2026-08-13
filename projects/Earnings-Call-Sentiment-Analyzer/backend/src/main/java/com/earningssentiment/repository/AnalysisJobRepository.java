package com.earningssentiment.repository;

import com.earningssentiment.domain.AnalysisJob;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, Long> {
}
