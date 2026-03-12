#!/bin/bash
# Manual Chat Backup - Run this anytime to backup current chat
# Usage: ./backup-chat-now.sh

BACKUP_DIR="/Users/yana/.openclaw/workspace/chats"
DATE=$(date +"%d-%m-%Y")
TIME=$(date +"%H-%M-%S")
BACKUP_FILE="${BACKUP_DIR}/${DATE}-chat.md"

echo "🔄 Starting chat backup..."
echo "   Target: $BACKUP_FILE"

# Run the backup script
/Users/yana/.openclaw/workspace/scripts/backup-chat.sh

echo ""
echo "✅ Manual backup complete!"
echo ""
echo "📁 Backup location:"
ls -lh "$BACKUP_FILE"
