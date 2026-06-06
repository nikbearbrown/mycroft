import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import StrategyPage from './pages/Strategy'
import FlowPage from './pages/Flow'
import DriftPage from './pages/Drift'
import MetricsPage from './pages/Metrics'
import EventsPage from './pages/Events'
import SimulatePage from './pages/Simulate'

export default function App() {
  return (
    <div className="flex min-h-screen bg-bg text-text">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/"         element={<StrategyPage />} />
          <Route path="/flow"     element={<FlowPage />} />
          <Route path="/drift"    element={<DriftPage />} />
          <Route path="/metrics"  element={<MetricsPage />} />
          <Route path="/events"   element={<EventsPage />} />
          <Route path="/simulate" element={<SimulatePage />} />
        </Routes>
      </main>
    </div>
  )
}