package com.earningssentiment.domain;

import jakarta.persistence.*;

import java.time.Instant;

@Entity
@Table(name = "sentiment_summaries")
public class SentimentSummary {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transcript_id", nullable = false, unique = true)
    private Transcript transcript;

    @Enumerated(EnumType.STRING)
    @Column(name = "overall_label", nullable = false, length = 30)
    private SentimentLabel overallLabel;

    @Column(name = "overall_score", nullable = false)
    private Double overallScore;

    @Column(name = "prepared_remarks_score")
    private Double preparedRemarksScore;

    @Column(name = "qa_score")
    private Double qaScore;

    @Column(name = "management_score")
    private Double managementScore;

    @Column(name = "analyst_score")
    private Double analystScore;

    @Column(name = "positive_chunk_count", nullable = false)
    private Integer positiveChunkCount;

    @Column(name = "neutral_chunk_count", nullable = false)
    private Integer neutralChunkCount;

    @Column(name = "negative_chunk_count", nullable = false)
    private Integer negativeChunkCount;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Transcript getTranscript() { return transcript; }
    public void setTranscript(Transcript transcript) { this.transcript = transcript; }
    public SentimentLabel getOverallLabel() { return overallLabel; }
    public void setOverallLabel(SentimentLabel overallLabel) { this.overallLabel = overallLabel; }
    public Double getOverallScore() { return overallScore; }
    public void setOverallScore(Double overallScore) { this.overallScore = overallScore; }
    public Double getPreparedRemarksScore() { return preparedRemarksScore; }
    public void setPreparedRemarksScore(Double preparedRemarksScore) { this.preparedRemarksScore = preparedRemarksScore; }
    public Double getQaScore() { return qaScore; }
    public void setQaScore(Double qaScore) { this.qaScore = qaScore; }
    public Double getManagementScore() { return managementScore; }
    public void setManagementScore(Double managementScore) { this.managementScore = managementScore; }
    public Double getAnalystScore() { return analystScore; }
    public void setAnalystScore(Double analystScore) { this.analystScore = analystScore; }
    public Integer getPositiveChunkCount() { return positiveChunkCount; }
    public void setPositiveChunkCount(Integer positiveChunkCount) { this.positiveChunkCount = positiveChunkCount; }
    public Integer getNeutralChunkCount() { return neutralChunkCount; }
    public void setNeutralChunkCount(Integer neutralChunkCount) { this.neutralChunkCount = neutralChunkCount; }
    public Integer getNegativeChunkCount() { return negativeChunkCount; }
    public void setNegativeChunkCount(Integer negativeChunkCount) { this.negativeChunkCount = negativeChunkCount; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
