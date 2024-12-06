#!/bin/bash

# Activate virtual environment if you're using one
# source venv/bin/activate  # Uncomment if using virtualenv

# Ensure we're in the server directory
cd "$(dirname "$0")"

# Define PID file location
PID_FILE="gunicorn.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if ps -p $pid > /dev/null 2>&1; then
        echo "Server is already running with PID: $pid"
        exit 1
    else
        # Remove stale PID file
        rm "$PID_FILE"
    fi
fi

# Start Gunicorn
python -m gunicorn --bind 0.0.0.0:5000 wsgi:app \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    # --reload \
    # --daemon \
    --pid "$PID_FILE"

echo "Server started. PID file: $PID_FILE"
