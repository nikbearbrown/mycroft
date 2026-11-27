export const INITIAL_METRICS = {
  totalEvaluated: 1284,
  hallucinationsBlocked: 47,
  cacheHitRate: 84.6,
  avgLatencyMs: 14,
};

export const SYSTEM_SERVICES = [
  { name: "FastAPI Gatekeeper", port: "8000", status: "healthy", detail: "JWT Auth Active" },
  { name: "Redis Cache", port: "6379", status: "healthy", detail: "TTL: 3600s · 84.6% Hit" },
  { name: "ChromaDB Ledger", port: "local", status: "healthy", detail: "Ground Truth Synced" },
  { name: "Prometheus Telemetry", port: "9090", status: "healthy", detail: "Scraping every 5s" },
  { name: "n8n Alert Engine", port: "5678", status: "healthy", detail: "Webhook Active" },
];

export const BLOCKED_PAYLOADS = [
  {
    id: "CLM-9042",
    timestamp: "2026-11-26 14:12:08",
    claim: "Q3 Net Revenue reached $45.0M across North America.",
    groundTruth: "Q3 Net Revenue was $4.5M across North America.",
    varianceType: "Magnitude Error",
    cacheStatus: "MISS",
    alertSent: true,
  },
  {
    id: "CLM-9041",
    timestamp: "2026-11-26 14:09:51",
    claim: "Operating margin expanded by +18.2% YoY.",
    groundTruth: "Operating margin contracted by -2.4% YoY.",
    varianceType: "Polarity Error",
    cacheStatus: "HIT",
    alertSent: true,
  },
  {
    id: "CLM-9038",
    timestamp: "2026-11-26 13:54:22",
    claim: "Debt-to-equity ratio dropped to 0.12 in Q3.",
    groundTruth: "Debt-to-equity ratio stood at 1.20 in Q3.",
    varianceType: "Magnitude Error",
    cacheStatus: "MISS",
    alertSent: true,
  },
  {
    id: "CLM-9035",
    timestamp: "2026-11-26 13:41:03",
    claim: "FY2026 guidance projects $120M in recurring cloud sales.",
    groundTruth: "No FY2026 recurring cloud sales guidance issued.",
    varianceType: "Unverified Entity",
    cacheStatus: "MISS",
    alertSent: true,
  },
];