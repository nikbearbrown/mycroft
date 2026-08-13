package com.earningssentiment.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "transcript_chunks")
public class TranscriptChunk {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transcript_id", nullable = false)
    private Transcript transcript;

    @Column(name = "section_name", nullable = false, length = 50)
    private String sectionName;

    @Column(name = "speaker_name", length = 200)
    private String speakerName;

    @Column(name = "speaker_role", nullable = false, length = 50)
    private String speakerRole;

    @Column(name = "chunk_text", nullable = false, columnDefinition = "text")
    private String chunkText;

    @Column(name = "chunk_order", nullable = false)
    private Integer chunkOrder;

    @OneToOne(mappedBy = "chunk", fetch = FetchType.LAZY)
    private SentimentResult sentimentResult;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Transcript getTranscript() { return transcript; }
    public void setTranscript(Transcript transcript) { this.transcript = transcript; }
    public String getSectionName() { return sectionName; }
    public void setSectionName(String sectionName) { this.sectionName = sectionName; }
    public String getSpeakerName() { return speakerName; }
    public void setSpeakerName(String speakerName) { this.speakerName = speakerName; }
    public String getSpeakerRole() { return speakerRole; }
    public void setSpeakerRole(String speakerRole) { this.speakerRole = speakerRole; }
    public String getChunkText() { return chunkText; }
    public void setChunkText(String chunkText) { this.chunkText = chunkText; }
    public Integer getChunkOrder() { return chunkOrder; }
    public void setChunkOrder(Integer chunkOrder) { this.chunkOrder = chunkOrder; }
    public SentimentResult getSentimentResult() { return sentimentResult; }
    public void setSentimentResult(SentimentResult sentimentResult) { this.sentimentResult = sentimentResult; }
}
