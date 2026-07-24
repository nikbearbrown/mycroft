import axios from 'axios'
import type { ApiError } from './types'

export function apiErrorMessage(error: unknown, fallback = 'Something went wrong') {
  if (axios.isAxiosError<ApiError>(error)) {
    return error.response?.data?.message || error.message || fallback
  }
  return error instanceof Error ? error.message : fallback
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

export function formatNetTone(value: number | null | undefined) {
  if (value == null) return '—'
  const percentage = Math.round(value * 100)
  return percentage > 0 ? `+${percentage}%` : `${percentage}%`
}

export function readableName(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (letter: string) => letter.toUpperCase())
}
