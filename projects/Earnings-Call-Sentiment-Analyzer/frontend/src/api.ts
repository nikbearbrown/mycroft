import axios from 'axios'
import type {
  AnalysisJob,
  SentimentAggregate,
  SentimentChunk,
  SentimentSummary,
  Transcript,
  UploadResponse,
} from './types'

export const api = axios.create({
  baseURL: '/api',
  timeout: 30_000,
})

export async function uploadTranscript(formData: FormData) {
  const { data } = await api.post<UploadResponse>('/transcripts', formData)
  return data
}

export async function getTranscripts() {
  const { data } = await api.get<Transcript[]>('/transcripts')
  return data
}

export async function getTranscript(id: number) {
  const { data } = await api.get<Transcript>(`/transcripts/${id}`)
  return data
}

export async function getJob(id: number) {
  const { data } = await api.get<AnalysisJob>(`/jobs/${id}`)
  return data
}

export async function getSummary(transcriptId: number) {
  const { data } = await api.get<SentimentSummary>(`/transcripts/${transcriptId}/sentiment/summary`)
  return data
}

export async function getChunks(transcriptId: number) {
  const { data } = await api.get<SentimentChunk[]>(`/transcripts/${transcriptId}/sentiment/chunks`)
  return data
}

export async function getSections(transcriptId: number) {
  const { data } = await api.get<SentimentAggregate[]>(`/transcripts/${transcriptId}/sentiment/sections`)
  return data
}

export async function getSpeakers(transcriptId: number) {
  const { data } = await api.get<SentimentAggregate[]>(`/transcripts/${transcriptId}/sentiment/speakers`)
  return data
}
