#!/bin/bash
source env/bin/activate
uvicorn web.server:app --reload --port 8000
