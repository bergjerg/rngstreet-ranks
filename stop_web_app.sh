#!/bin/bash

# Get the current directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if the web app is running
if pgrep -f "gunicorn.*web_app:app" > /dev/null; then
    # Kill the web app process
    pkill -f "gunicorn.*web_app:app"
    echo "Web app stopped."
else
    echo "Web app is not running."
fi
