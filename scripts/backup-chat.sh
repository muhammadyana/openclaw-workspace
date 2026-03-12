#!/bin/bash
# Daily Chat Backup Script for OpenClaw
# This script is triggered by OpenClaw cron job
# Format: DD-MM-YYYY-chat.md

BACKUP_DIR="/Users/yana/.openclaw/workspace/chats"
DATE=$(date +"%d-%m-%Y")
TIME=$(date +"%H:%M:%S")
BACKUP_FILE="${BACKUP_DIR}/${DATE}-chat.md"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Check if backup already exists for today
if [ -f "$BACKUP_FILE" ]; then
    echo "Backup already exists for today: $BACKUP_FILE"
    echo "Appending new content..."
    APPEND_MODE=true
else
    APPEND_MODE=false
fi

if [ "$APPEND_MODE" = false ]; then
    # Create markdown header for new file
    cat > "$BACKUP_FILE" << 'HEADER'
# Chat Backup - DATE_PLACEHOLDER

**Backup Date:** DATE_PLACEHOLDER  
**Backup Time:** TIME_PLACEHOLDER  
**Hostname:** HOSTNAME_PLACEHOLDER  
**User:** USER_PLACEHOLDER

---

## System Information

- **OpenClaw Version:** OPENCLAW_VERSION_PLACEHOLDER
- **Working Directory:** WORKDIR_PLACEHOLDER
- **Backup Location:** BACKUP_FILE_PLACEHOLDER

---

HEADER

    # Replace placeholders
    sed -i '' "s/DATE_PLACEHOLDER/${DATE}/g" "$BACKUP_FILE"
    sed -i '' "s/TIME_PLACEHOLDER/${TIME}/g" "$BACKUP_FILE"
    sed -i '' "s/HOSTNAME_PLACEHOLDER/$(hostname)/g" "$BACKUP_FILE"
    sed -i '' "s/USER_PLACEHOLDER/$(whoami)/g" "$BACKUP_FILE"
    sed -i '' "s|OPENCLAW_VERSION_PLACEHOLDER|$(openclaw --version 2>/dev/null || echo 'unknown')|g" "$BACKUP_FILE"
    sed -i '' "s|WORKDIR_PLACEHOLDER|/Users/yana/.openclaw/workspace|g" "$BACKUP_FILE"
    sed -i '' "s|BACKUP_FILE_PLACEHOLDER|${BACKUP_FILE}|g" "$BACKUP_FILE"
fi

# Add timestamp for this backup run
echo "" >> "$BACKUP_FILE"
echo "---" >> "$BACKUP_FILE"
echo "" >> "$BACKUP_FILE"
echo "## Backup Run - ${TIME}" >> "$BACKUP_FILE"
echo "" >> "$BACKUP_FILE"

# Try to get session info using openclaw CLI
echo "### Active Sessions" >> "$BACKUP_FILE"
echo "" >> "$BACKUP_FILE"
echo '```' >> "$BACKUP_FILE"
openclaw sessions >> "$BACKUP_FILE" 2>&1 || echo "Could not retrieve sessions" >> "$BACKUP_FILE"
echo '```' >> "$BACKUP_FILE"
echo "" >> "$BACKUP_FILE"

echo "✅ Chat backup completed: $BACKUP_FILE"
echo "   Size: $(ls -lh "$BACKUP_FILE" | awk '{print $5}')"

# Cleanup: Compress backups older than 30 days
find "$BACKUP_DIR" -name "*.md" -mtime +30 -exec gzip {} \; 2>/dev/null || true

# Keep only last 90 days of backups
find "$BACKUP_DIR" -name "*.md.gz" -mtime +90 -delete 2>/dev/null || true

echo "   Old backups compressed and cleaned up."
