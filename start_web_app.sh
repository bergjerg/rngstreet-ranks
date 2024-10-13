#!/bin/bash

# Get the current directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_APP_DIR="$DIR/web_app"
LOG_DIR="$DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check if the web app is already running
if pgrep -f "gunicorn.*web_app:app" > /dev/null; then
    echo "Web app is already running."
    exit 1
fi

# Navigate to the web app directory
cd "$WEB_APP_DIR" || { echo "Failed to navigate to web app directory"; exit 1; }

# Activate virtual environment for the web app
if ! source "$WEB_APP_DIR/venv/bin/activate"; then
    echo "Failed to activate virtual environment"
    exit 1
fi

# Start the Python web app using Gunicorn in production mode with logging
nohup gunicorn -w 4 -b 0.0.0.0:8080 \
    --access-logfile "$LOG_DIR/gunicorn_access.log" \
    --error-logfile "$LOG_DIR/gunicorn_error.log" \
    --capture-output --log-level info \
    web_app:app >> "$LOG_DIR/web_app.log" 2>&1 &

# Check if Gunicorn started successfully
if [ $? -eq 0 ]; then
    echo "Web app (via Gunicorn) started successfully. Logs can be found in $LOG_DIR"
else
    echo "Failed to start the web app via Gunicorn"
fi

# Deactivate the virtual environment
deactivate
