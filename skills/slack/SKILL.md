---
name: slack
description: Control Slack via OpenClaw CLI. Use when the user wants to read messages, send messages, react to messages, or manage pins in Slack channels or DMs. The bot token is already configured in ~/.openclaw/openclaw.json.
---

# Slack Actions (OpenClaw)

## Overview

Use OpenClaw's native Slack integration to react, manage pins, send/edit/delete messages. The bot token is already configured in your `~/.openclaw/openclaw.json`.

**Status**: ✅ Configured and working!

## Channel IDs

Use **Channel IDs** (not names) for targeting:

| Channel Name | Channel ID |
|-------------|------------|
| #errors | `C09KB8DU7DW` |
| #general | `C06HVDGQJ8Y` |
| #bug-incidents | `C09K4PB154K` |
| #deployment | `C09FAJN21PV` |

To find other channel IDs:
```bash
# List all channels with IDs
curl -H "Authorization: Bearer TOKEN" \
  "https://slack.com/api/conversations.list?types=public_channel" | jq '.channels[] | {name: .name, id: .id}'
```

## How to Use

### Read Messages from a Channel

```bash
# Use Channel ID (not #name)
openclaw message read --channel slack --target "C09KB8DU7DW" --limit 10
```

With JSON output:
```bash
openclaw message read --channel slack --target "C09KB8DU7DW" --limit 5 --json
```

### Send a Message

To a channel:
```bash
openclaw message send --channel slack --target "#general" --message "Hello team!"
```

To a user:
```bash
openclaw message send --channel slack --target "@username" --message "Hello!"
```

### React to a Message

You need the message timestamp (e.g., `1770568756.646329`) and channel ID:

```bash
openclaw message react --channel slack --target "C09KB8DU7DW" --message "1770568756.646329" --emoji "✅"
```

### List Reactions

```bash
openclaw message reactions --channel slack --target "C09KB8DU7DW" --message "1770568756.646329"
```

### Pin a Message

```bash
openclaw message pin --channel slack --target "C09KB8DU7DW" --message "1770568756.646329"
```

### Unpin a Message

```bash
openclaw message unpin --channel slack --target "C09KB8DU7DW" --message "1770568756.646329"
```

### List Pinned Messages

```bash
openclaw message pins --channel slack --target "C09KB8DU7DW"
```

### Delete a Message

```bash
openclaw message delete --channel slack --target "C09KB8DU7DW" --message "1770568756.646329"
```

### Edit a Message

```bash
openclaw message edit --channel slack --target "C09KB8DU7DW" --message "1770568756.646329" --content "Updated text"
```

## Getting Message Timestamps

When you read messages with `--json`, each message has a timestamp like `1770568756.646329`. Use this for reactions, pins, edits, etc.

## Common Workflows

### Read and React
1. Read messages: `openclaw message read --channel slack --target "C09KB8DU7DW" --limit 5 --json`
2. Find the message timestamp in the output
3. React: `openclaw message react --channel slack --target "C09KB8DU7DW" --message "TIMESTAMP" --emoji "✅"`

### Monitor #errors Channel
```bash
# Read last 10 error alerts
openclaw message read --channel slack --target "C09KB8DU7DW" --limit 10
```
