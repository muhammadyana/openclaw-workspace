# MEMORY.md - Long-Term Memory

*Curated knowledge from daily memory logs*

---

## 🏥 Hermina Hospital API

### Base URL
`https://api.herminahospitals.com/api/v1/`

### Key Endpoints
- **Hospitals**: `GET /public/hospitals?q={branch}` - Find by branch name
- **Doctors**: `GET /public/doctors?hospital_id={id}&speciality_id={spec}&q={query}`
- **Schedules**: `GET /public/doctors/{slug}/schedules?schedule_type=executive&type=table`
  - `schedule_type`: `executive` (Padma/private) or `specialist` (BPJS/insurance)
  - `type=table` for weekly schedule display

### Hospital IDs (Known)
- Jatinegara = 1
- Kemayoran = 2
- Pasteur = 7
- Arcamanik = 13

### Local Database Schema
- `doctors` - full_name, speciality_id, hospital_id
- `hospitals` - name, branch, id
- `schedules` - doctor_id, hospital_id, day, from_time, to_time

---

## 📹 CCTV Surveillance Commands

### Trigger Phrases
- "what do you see" / "apa yang kamu lihat"
- "what you hear" / "apa yang kamu dengar"
- "what do you see and hear"

### Camera Details
- **Device**: Tapo C222 (RTSP-enabled)
- **IP**: `192.168.31.133`
- **RTSP**: `rtsp://iotcctv:SmartHome@192.168.31.133:554/stream1`
- **Resolution**: 2560x1440 (2K)
- **Location**: Workspace/bedroom area

### Actions
**SEE**: Capture snapshot → describe image → send via Telegram/Slack → TTS audio
**HEAR**: 10-second clip → Whisper transcription → identify song if music → send audio
**SEE + HEAR**: Both simultaneously

### Critical Rules
- ALWAYS send actual image file, not just description
- ALWAYS send actual audio file, not just transcription
- ALWAYS generate TTS voice message
- Include timestamp from camera overlay

---

## 💰 Expense Tracker

### Location
`~/.openclaw/workspace/skills/expense-tracker/`

### Features
- OCR from receipt photos (tesseract + pytesseract)
- Auto-extract: merchant, total, date, items
- Auto-categorization: Makanan, Transport, Belanja, Hiburan, Kesehatan, Utilitas, Lainnya
- Dual storage: SQLite + Excel export with charts

### User Preference
- **Auto-execute without confirmation** ("Gausah tanya lagi, buat apa gue upload struk kalo bukan ditrack")

### Usage
```bash
# Via cron (daily at 22:00) or manual:
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py add /path/to/receipt.jpg
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py summary --bulan 2
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py chart
```

---

## 🐦 X/Twitter (Bird CLI)

### Account
Connected to: **@namdoyan** (Yaya 🇵🇸)

### Commands
```bash
bird whoami              # Check current user
bird user-tweets namdoyan
bird mentions
bird tweet "text"
bird reply <id> "text"
```

### Notes
- Uses Chrome profile cookies (no API keys needed)
- Rate limits apply for replies

---

## 🌙 Ramadan Preparation

### Setup Needed
- Sahur/iftar reminders
- Zakat calculator
- Daily schedules
- Prayer time notifications

### Audio Note
User requested help for Ramadan ("tolong bantu aku nanti di bulan ramadhan")

---

## ⚠️ API Status & Issues

| Service | Status | Notes |
|---------|--------|-------|
| Gemini Live API | ⚠️ 404 Error | API key configured but needs billing/project setup |
| OpenAI | ❌ Billing Limit | Hard limit reached - cannot use image editing |
| OpenAI Whisper | ❌ Quota Exceeded | Using local Whisper CLI instead |
| SmartThings | ✅ Working | Token active |
| Bird CLI | ✅ Working | Cookie-based auth |

---

## 📋 User Preferences & Rules

### Decision History
1. Read **ALL** memory files (not just today+yesterday) - changed in AGENTS.md
2. Auto-execute expense tracking without confirmation
3. Prefer local tools over cloud APIs when possible
4. Use fallback TTS while Gemini Live API has issues

### Travel Info
- Recent trip: Karimun Jawa (one-day trip, 200K budget)
- Interested in: Tanjung Bira, Wakatobi, Bunaken, Raja Ampat, Sumba, Banda Neira, Pulau Weh

---

## 🛠️ Workspace Skills

| Skill | Path | Status |
|-------|------|--------|
| audit-code | `~/.openclaw/skills/audit-code/` | ✅ Active |
| expense-tracker | `~/.openclaw/workspace/skills/expense-tracker/` | ✅ Active |
| hello-world | `~/.openclaw/skills/hello-world/` | ✅ Active |
| slack | `~/.openclaw/skills/slack/` | ✅ Configured |
| x | `~/.openclaw/skills/x/` | ✅ Active |
| ramadan-tracker | `~/.openclaw/workspace/skills/ramadan-tracker/` | ✅ Active |

---

*Last updated: 19 Feb 2026*
*Reconstructed from memory/ folder after history rewrite*
