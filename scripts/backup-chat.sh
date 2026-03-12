#!/bin/bash
# Daily Chat Backup Script for OpenClaw
# Captures both session metadata AND conversation history
# Format: DD-MM-YYYY-chat.md

BACKUP_DIR="/Users/yana/.openclaw/workspace/chats"
DATE=$(date +"%d-%m-%Y")
TIME=$(date +"%H:%M:%S")
BACKUP_FILE="${BACKUP_DIR}/${DATE}-chat.md"
AGENT_DIR="/Users/yana/.openclaw/agents/main"

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
    cat > "$BACKUP_FILE" << EOF
# Chat Backup - ${DATE}

**Backup Date:** ${DATE}  
**Backup Time:** ${TIME}  
**Hostname:** $(hostname)  
**User:** $(whoami)

---

## System Information

- **OpenClaw Version:** $(openclaw --version 2>/dev/null || echo 'unknown')
- **Working Directory:** /Users/yana/.openclaw/workspace
- **Backup Location:** ${BACKUP_FILE}

---

EOF
fi

# Add timestamp for this backup run
echo "" >> "$BACKUP_FILE"
echo "---" >> "$BACKUP_FILE"
echo "" >> "$BACKUP_FILE"
echo "## Backup Run - ${TIME}" >> "$BACKUP_FILE"
echo "" >> "$BACKUP_FILE"

# Get current session ID from sessions.json
CURRENT_SESSION_ID=$(jq -r '.["agent:main:main"].sessionId' "$AGENT_DIR/sessions/sessions.json" 2>/dev/null)

if [ -n "$CURRENT_SESSION_ID" ] && [ -f "$AGENT_DIR/sessions/${CURRENT_SESSION_ID}.jsonl" ]; then
    echo "Backing up conversation from session: $CURRENT_SESSION_ID"
    
    # Capture conversation history
    echo "### Conversation History" >> "$BACKUP_FILE"
    echo "" >> "$BACKUP_FILE"
    
    # Extract user and assistant messages
    jq -r 'select(.type=="message") | 
           if .message.role == "user" then 
             "**User:** " + (.message.content[]? | select(.type=="text") | .text) 
           elif .message.role == "assistant" then 
             "**Assistant:** " + (.message.content[]? | select(.type=="text") | .text)
           else empty end' \
        "$AGENT_DIR/sessions/${CURRENT_SESSION_ID}.jsonl" 2>/dev/null >> "$BACKUP_FILE" || echo "*Could not extract conversation*" >> "$BACKUP_FILE"
    
    echo "" >> "$BACKUP_FILE"
else
    echo "### Conversation History" >> "$BACKUP_FILE"
    echo "" >> "$BACKUP_FILE"
    echo "*No active session found or session file not available*" >> "$BACKUP_FILE"
    echo "" >> "$BACKUP_FILE"
fi

# Also capture session list for reference
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
