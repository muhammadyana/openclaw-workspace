#!/bin/bash
# Send Ramadan reminder based on job name

JOB_NAME="$1"
JSON_FILE="$HOME/.openclaw/workspace/ramadan_cron_jobs.json"

# Extract message from JSON based on job name
MESSAGE=$(python3 -c "
import json, sys
with open('$JSON_FILE') as f:
    jobs = json.load(f)
for job in jobs:
    if job['name'] == '$JOB_NAME':
        print(job['message'])
        break
")

# Send via Telegram
if [ -n "$MESSAGE" ]; then
    /opt/homebrew/bin/openclaw message send --channel telegram --target telegram:210669138 --message "$MESSAGE"
fi
