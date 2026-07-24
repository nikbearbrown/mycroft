package com.earningssentiment.domain;

import jakarta.persistence.*;

import java.time.Instant;

@Entity
@Table(name = "transcripts")
public class Transcript {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "company_name", nullable = false, length = 200)
    private String companyName;

    @Column(nullable = false, length = 20)
    private String ticker;

    @Column(nullable = false, length = 20)
    private String quarter;

    @Column(name = "fiscal_year", nullable = false)
    private Integer fiscalYear;

    @Column(name = "file_path", nullable = false, length = 1000)
    private String filePath;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private TranscriptStatus status;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @PrePersist
    void prePersist() {
        if (createdAt == null) createdAt = Instant.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getCompanyName() { return companyName; }
    public void setCompanyName(String companyName) { this.companyName = companyName; }
    public String getTicker() { return ticker; }
    public void setTicker(String ticker) { this.ticker = ticker; }
    public String getQuarter() { return quarter; }
    public void setQuarter(String quarter) { this.quarter = quarter; }
    public Integer getFiscalYear() { return fiscalYear; }
    public void setFiscalYear(Integer fiscalYear) { this.fiscalYear = fiscalYear; }
    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) { this.filePath = filePath; }
    public TranscriptStatus getStatus() { return status; }
    public void setStatus(TranscriptStatus status) { this.status = status; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
