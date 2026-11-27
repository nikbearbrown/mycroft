import { useState } from "react";
import { INITIAL_METRICS, SYSTEM_SERVICES, BLOCKED_PAYLOADS } from "./data/mockTelemetry";
import "./App.css";

export default function App() {
  const [filter, setFilter] = useState("ALL");

  const varianceTypes = ["ALL", "Magnitude Error", "Polarity Error", "Unverified Entity"];
  const filteredPayloads =
    filter === "ALL"
      ? BLOCKED_PAYLOADS
      : BLOCKED_PAYLOADS.filter((item) => item.varianceType === filter);

  return (
    <div className="portal">
      <header className="portal-header">
        <div>
          <h1>Provenance Gatekeeper</h1>
          <p className="subtitle">AI Financial Hallucination Intercept & Telemetry Portal</p>
        </div>
        <span className="status-pill">● SYSTEM OPERATIONAL</span>
      </header>

      {/* KPI Cards */}
      <section className="kpi-grid">
        <div className="card">
          <span className="card-label">Claims Evaluated</span>
          <strong className="card-value">{INITIAL_METRICS.totalEvaluated.toLocaleString()}</strong>
        </div>
        <div className="card card-alert">
          <span className="card-label">Hallucinations Blocked</span>
          <strong className="card-value">{INITIAL_METRICS.hallucinationsBlocked}</strong>
        </div>
        <div className="card card-accent">
          <span className="card-label">Redis Cache Hit Rate</span>
          <strong className="card-value">{INITIAL_METRICS.cacheHitRate}%</strong>
        </div>
        <div className="card">
          <span className="card-label">Avg Intercept Latency</span>
          <strong className="card-value">{INITIAL_METRICS.avgLatencyMs} ms</strong>
        </div>
      </section>

      {/* Infrastructure Health Strip */}
      <section className="panel">
        <h2>Microservice Infrastructure Health</h2>
        <div className="service-grid">
          {SYSTEM_SERVICES.map((svc) => (
            <div key={svc.name} className="service-item">
              <div className="service-top">
                <strong>{svc.name}</strong>
                <span className="badge-ok">{svc.status.toUpperCase()}</span>
              </div>
              <small>Port: {svc.port} · {svc.detail}</small>
            </div>
          ))}
        </div>
      </section>

      {/* Blocked Payloads Table */}
      <section className="panel">
        <div className="panel-header">
          <h2>Intercepted Hallucination Ledger</h2>
          <div className="filter-bar">
            {varianceTypes.map((type) => (
              <button
                key={type}
                className={filter === type ? "filter-btn active" : "filter-btn"}
                onClick={() => setFilter(type)}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Claim ID</th>
                <th>Timestamp</th>
                <th>Generated AI Claim</th>
                <th>ChromaDB Ground Truth</th>
                <th>Variance Type</th>
                <th>Cache</th>
                <th>n8n Alert</th>
              </tr>
            </thead>
            <tbody>
              {filteredPayloads.map((row) => (
                <tr key={row.id}>
                  <td className="mono">{row.id}</td>
                  <td className="mono muted">{row.timestamp}</td>
                  <td>{row.claim}</td>
                  <td className="truth">{row.groundTruth}</td>
                  <td><span className="badge-fail">{row.varianceType}</span></td>
                  <td><span className={row.cacheStatus === "HIT" ? "badge-hit" : "badge-miss"}>{row.cacheStatus}</span></td>
                  <td>{row.alertSent ? "Dispatched" : "Pending"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}