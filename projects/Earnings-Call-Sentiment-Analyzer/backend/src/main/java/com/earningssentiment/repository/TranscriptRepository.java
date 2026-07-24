package com.earningssentiment.repository;

import com.earningssentiment.domain.Transcript;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TranscriptRepository extends JpaRepository<Transcript, Long> {
    List<Transcript> findAllByOrderByCreatedAtDesc();
}
