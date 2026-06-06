import { useState } from 'react'
import Upload from './pages/Upload'
import Results from './pages/Results'

export default function App() {
  const [report, setReport] = useState(null)

  return report
    ? <Results report={report} onReset={() => setReport(null)} />
    : <Upload onReport={setReport} />
}