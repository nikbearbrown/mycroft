# Sprint 7 (serving) — FastAPI + Streamlit

Serves the stored runs (Sprint 6, DuckDB) two ways. Both are READ-ONLY: they show
what's stored and never score or decide. The human gate stays in the pipeline.

## Setup
    pip install fastapi uvicorn streamlit pandas duckdb

## Run the API
    uvicorn serve.api:app --reload
    # open http://127.0.0.1:8000/docs
    # endpoints: /companies , /companies/{id}/brief , /companies/{id}/trend

## Run the dashboard
    streamlit run serve/dashboard.py
    # opens in the browser: company comparison + trend charts

## Note
With only one stored run the charts are small — that's expected. Store more runs
(python -m storage.store_runs data/deduped/signals.json --store) to see the trend
fill in. Airflow scheduling is a later, separate step.
