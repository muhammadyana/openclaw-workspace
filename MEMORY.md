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

## 🐛 Lessons Learned

### OpenClaw Control UI - Tool Calling Bug (10 Mar 2026)

**Problem:** Tool calls (exec, read, etc.) tidak berfungsi dari control UI interface.

**Symptoms:**
- Command seperti `ls -la`, `pwd`, atau custom scripts tidak dieksekusi
- Tidak ada output yang dikembalikan
- Agent hanya merespons dengan text biasa tanpa eksekusi

**Environment:**
- Versi bermasalah: Sebelum 2026.3.2
- Platform: Control UI (bukan Telegram/webchat)
- Runtime: Agent main session

**Root Cause:** Bug di versi OpenClaw sebelum 2026.3.2 yang menyebabkan tool calling dari control UI tidak diproses.

**Fix:**
- Downgrade/upgrade ke OpenClaw versi **2026.3.2**
- Setelah update, tool calling berfungsi normal

**Status:** ✅ Resolved

**Report To:** https://github.com/openclaw/openclaw/issues (jika terjadi lagi)

---

### Expense Tracker - Auto-Save Bug (20 Feb 2026)

**Problem:** Receipts were OCR'd and acknowledged but NOT auto-saved to database.

**Impact:** Daily reports showed Rp 0 when there were actually Rp 530,700 in transactions.

**Root Cause:** I only described the receipt but never executed `expense.py add` command.

**Fix:**
1. Added 3 missing transactions manually to database
2. Updated AGENTS.md with explicit instruction: ALWAYS auto-save receipts
3. User preference confirmed: "Gausah tanya lagi" = auto-execute

**Rule:** When user sends receipt/payment screenshot → OCR → Confirm → **EXECUTE SAVE**

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

- ✅ **Manual input only** (OCR dihapus - terlalu sering salah detect)
- Auto-categorization: Makanan, Transport, Belanja, Hiburan, Kesehatan, Utilitas, Lainnya
- Dual storage: SQLite + Excel export with charts
- Telegram format (`--telegram` flag) for mobile-friendly output
- Daily report command (`daily`)
- Button config for Telegram integration

### User Preference

- **Auto-execute without confirmation** ("Gausah tanya lagi, buat apa gue upload struk kalo bukan ditrack")

### Commands

```bash
# Add expense
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py add /path/to/receipt.jpg

# Daily report
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py daily
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py daily --telegram

# List with Telegram format
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py list --dari today --telegram

# Summary & chart
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py summary --bulan 2
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py chart

# Telegram buttons config
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py buttons
```

### Output Format (Preferred)

Gunakan format tabel markdown saat konfirmasi expense:

```
✅ Expense tercatat!

| Detail   | Value                 |
| -------- | --------------------- |
| Merchant | {nama merchant}       |
| Amount   | Rp {total} (MYR {myr}) |
| Category | {kategori}            |
| Date     | {tanggal}             |
| Payment  | {metode pembayaran}   |
| Card     | {kartu/jenis}         |
| Rate     | {rate} IDR/MYR        |  # jika transaksi MYR
| ID       | #{id}                 |
```

### Telegram Button Shortcuts

```json
[
  ["📊 Daily Report", "/expense daily --telegram"],
  ["📈 Monthly", "/expense summary --bulan 2"],
  ["📝 List Today", "/expense list --dari today --telegram"],
  ["📉 Chart", "/expense chart"],
  ["💾 Export Excel", "/expense export"]
]
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

## 🌙 Ramadan Tracker

### Location

`~/.openclaw/workspace/skills/ramadan-tracker/`

### Implemented (21 Feb 2026)

✅ **Sahur/iftar reminders** - Cron jobs otomatis
✅ **Prayer times** - API Al-Adhan (Kemenag method)
✅ **Daily schedules** - `/ramadan today --telegram`
✅ **Telegram buttons** - Quick access jadwal & menu

### Location Settings

- **City**: Bandung
- **Address**: Jl. Tubagus Ismail VII No.11 ASekeloa, Coblong
- **Coordinates**: -6.8735, 107.6190

### Today's Prayer Times (21 Feb 2026)

| Waktu | Jam |
|-------|-----|
| Imsak | 04:28 |
| Subuh | 04:38 |
| Dzuhur | 12:03 |
| Ashar | 15:10 |
| Maghrib | 18:19 |
| Isya | 19:22 |

### Cron Jobs Active

- Sahur 1 jam: 03:28
- Sahur 30 menit: 03:58
- 5 menit sebelum imsak: 04:23
- 5 menit sebelum buka: 18:14
- Buka puasa: 18:19

### Commands

```bash
# Jadwal hari ini
~/.openclaw/workspace/skills/ramadan-tracker/scripts/ramadan.py today
~/.openclaw/workspace/skills/ramadan-tracker/scripts/ramadan.py today --telegram

# Menu buka
~/.openclaw/workspace/skills/ramadan-tracker/scripts/ramadan.py menu

# Lokasi
~/.openclaw/workspace/skills/ramadan-tracker/scripts/ramadan.py location

# Button config
~/.openclaw/workspace/skills/ramadan-tracker/scripts/ramadan.py buttons
```

### Telegram Button Shortcuts

```json
[
  ["📅 Jadwal Hari Ini", "/ramadan today --telegram"],
  ["🍽️ Menu Buka", "/ramadan menu"],
  ["📍 Lokasi", "/ramadan location"]
]
```

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

## 📅 Recent Activity (21 Feb 2026)

### Today's Expenses

Total: **Rp 981.440** (6 transaksi)

| ID | Merchant | Amount | Time |
|----|----------|--------|------|
| #58 | Shopee | Rp 46.850 | 23:53 |
| #57 | Total (Aroem Bandung) | Rp 315.400 | 19:10 |
| #56 | Aroem Bandung Berkah CV | Rp 100.000 | 17:29 |
| #54 | Total Buah Tirtayasa | Rp 149.650 | 17:18 |
| #53 | Shopee | Rp 265.040 | 16:18 |
| #52 | PINHOME | Rp 104.500 | 11:48 |

### Buka Puasa Menu (21 Feb)

- Gurame Tom Yum 🐟🌶️
- Kailan Dua Rasa 🥬🌿
- Sapo Tahu Seafood 🍲🦐
- Semangka + Es Teler 🍉🍨

---

*Last updated: 21 Feb 2026*
