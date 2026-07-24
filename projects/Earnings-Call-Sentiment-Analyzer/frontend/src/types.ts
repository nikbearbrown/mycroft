export type SentimentLabel = 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE'
export type JobStatus = 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED'

export interface UploadResponse {
  transcriptId: number
  jobId: number
  status: JobStatus
}

export interface Transcript {
  id: number
  companyName: string
  ticker: string
  quarter: string
  fiscalYear: number
  status: JobStatus
  createdAt: string
}

export interface AnalysisJob {
  id: number
  transcriptId: number
  status: JobStatus
  progress: number
  message: string | null
  errorMessage: string | null
  startedAt: string | null
  completedAt: string | null
  createdAt: string
}

export interface SentimentSummary {
  transcriptId: number
  overallLabel: SentimentLabel
  overallScore: number
  preparedRemarksScore: number | null
  qaScore: number | null
  managementScore: number | null
  analystScore: number | null
  positiveChunkCount: number
  neutralChunkCount: number
  negativeChunkCount: number
  createdAt: string
}

export interface SentimentChunk {
  chunkId: number
  chunkOrder: number
  sectionName: string
  speakerName: string | null
  speakerRole: string
  chunkText: string
  label: SentimentLabel
  positiveScore: number
  neutralScore: number
  negativeScore: number
  finalScore: number
  modelName: string
}

export interface SentimentAggregate {
  name: string
  role: string | null
  score: number
  positiveCount: number
  neutralCount: number
  negativeCount: number
  chunkCount: number
}

export interface ApiError {
  message?: string
}
