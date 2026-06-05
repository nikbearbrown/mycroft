# Frontend

React + Vite + Tailwind CSS. Two-page UI: CSV upload with broker preview, and a results page displaying the edge report, dimension scores, and detailed agent insights.

---

## Setup

```bash
npm install
npm run dev
```

Expects the backend running at `localhost:8000`. The Vite dev server proxies all `/api` requests to the backend — no CORS configuration needed.

For production, update the `target` in `vite.config.js` to point to your deployed backend URL.