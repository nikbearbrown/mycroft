package com.earningssentiment.domain;

import jakarta.persistence.*;

import java.time.Instant;

@Entity
@Table(name = "sentiment_results")
public class SentimentResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "chunk_id", nullable = false, unique = true)
    private TranscriptChunk chunk;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private SentimentLabel label;

    @Column(name = "positive_score", nullable = false)
    private Double positiveScore;

    @Column(name = "neutral_score", nullable = false)
    private Double neutralScore;

    @Column(name = "negative_score", nullable = false)
    private Double negativeScore;

    @Column(name = "final_score", nullable = false)
    private Double finalScore;

    @Column(name = "model_name", nullable = false, length = 200)
    private String modelName;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public TranscriptChunk getChunk() { return chunk; }
    public void setChunk(TranscriptChunk chunk) { this.chunk = chunk; }
    public SentimentLabel getLabel() { return label; }
    public void setLabel(SentimentLabel label) { this.label = label; }
    public Double getPositiveScore() { return positiveScore; }
    public void setPositiveScore(Double positiveScore) { this.positiveScore = positiveScore; }
    public Double getNeutralScore() { return neutralScore; }
    public void setNeutralScore(Double neutralScore) { this.neutralScore = neutralScore; }
    public Double getNegativeScore() { return negativeScore; }
    public void setNegativeScore(Double negativeScore) { this.negativeScore = negativeScore; }
    public Double getFinalScore() { return finalScore; }
    public void setFinalScore(Double finalScore) { this.finalScore = finalScore; }
    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
