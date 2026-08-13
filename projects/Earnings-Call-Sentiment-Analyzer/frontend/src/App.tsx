import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { DashboardPage } from './pages/DashboardPage'
import { JobStatusPage } from './pages/JobStatusPage'
import { TranscriptsPage } from './pages/TranscriptsPage'
import { UploadPage } from './pages/UploadPage'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/transcripts" replace />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/transcripts" element={<TranscriptsPage />} />
        <Route path="/jobs/:jobId" element={<JobStatusPage />} />
        <Route path="/transcripts/:transcriptId" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/transcripts" replace />} />
      </Routes>
    </AppShell>
  )
}
