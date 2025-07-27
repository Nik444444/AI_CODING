#!/bin/bash
# Railway start script

# Get port from environment (Railway sets this automatically)
PORT=${PORT:-8000}

# Start the application
exec uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1