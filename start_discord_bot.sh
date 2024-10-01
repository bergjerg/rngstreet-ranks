#!/bin/bash

# Get the current directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DISCORD_BOT_DIR="$DIR/discord_bot"
LOG_DIR="$DIR/logs"

# Check if the Discord bot is already running
if pgrep -f "python.*discord_bot/main.py" > /dev/null; then
    echo "Discord bot is already running."
    exit 1
fi

# Activate virtual environment for the Discord bot
source "$DISCORD_BOT_DIR/venv/bin/activate"

# Start the Discord bot
nohup python -u "$DISCORD_BOT_DIR/main.py" >> "$LOG_DIR/discord_bot.log" 2>&1 &

# Deactivate the virtual environment
deactivate

echo "Discord bot started. Logs can be found in $LOG_DIR"
