#!/bin/bash
# AI-powered Software Builder - Render startup script
set -e
cd backend
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
