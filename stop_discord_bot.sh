f
#!/bin/bash

# Get the current directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if the Discord bot is running
if pgrep -f "python.*discord_bot/main.py" > /dev/null; then
    # Kill the Discord bot process
    pkill -f "python.*discord_bot/main.py"
    echo "Discord bot stopped."
else
    echo "Discord bot is not running."
fi
