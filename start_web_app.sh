#!/bin/bash

# Get the current directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_APP_DIR="$DIR/web_app"
LOG_DIR="$DIR/logs"

# Check if the web app is already running
if pgrep -f "gunicorn.*web_app:app" > /dev/null; then
    echo "Web app is already running."
    exit 1
fi

# Navigate to the web app directory
cd "$WEB_APP_DIR" || exit

# Activate virtual environment for the web app
source "$WEB_APP_DIR/venv/bin/activate"

# Start the Python web app using Gunicorn in production mode
nohup gunicorn -w 4 -b 0.0.0.0:8080 --access-logfile "$LOG_DIR/gunicorn_access.log" web_app:app >> "$LOG_DIR/web_app.log" 2>&1 &

# Deactivate the virtual environment
deactivate

echo "Web app (via Gunicorn) started. Logs can be found in $LOG_DIR"
