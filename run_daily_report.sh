#!/bin/bash
# Daily Expense Report Runner - For Cron Job
# Simple wrapper that runs the Python script and captures output

cd /Users/yana/.openclaw/workspace

# Run the daily report and capture output
OUTPUT=$(/Users/yana/.pyenv/versions/3.10.14/bin/python3 /Users/yana/.openclaw/workspace/skills/expense-tracker/scripts/daily_report.py 2>&1)

# Log the output
echo "[$(date)] Daily report executed" >> /tmp/expense_cron.log
echo "$OUTPUT" >> /tmp/expense_cron.log

# Also log errors separately if any
if [ $? -ne 0 ]; then
    echo "[$(date)] ERROR: Daily report failed" >> /tmp/expense_cron.error.log
    echo "$OUTPUT" >> /tmp/expense_cron.error.log
    exit 1
fi

exit 0
