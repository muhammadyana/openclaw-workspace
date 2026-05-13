# MEMORY.md - Long-Term Memory

*Curated knowledge from daily memory logs*

---

## 🏥 Hermina Hospital API

### Knowledge Base: MRN Per Branch (Afya System)

#### Core Concept
Di Afya, **setiap RS/branch punya MRN berbeda** untuk pasien yang sama. 1 pasien punya banyak MRN tergantung di mana aja dia pernah berobat.

#### What Halo Hermina Records
Yang dicatat di aplikasi Halo Hermina itu dari **API balikan check patient** — yaitu MRN dari branch tempat pasien bikin janji, bukan MRN global.

#### Flow: How MRN Gets Assigned

1. **Patient check** (`/v1/patientmgmt/master/patient/patientlist`):
   - `AfyaIntegrable#check_afya_patient(hospital)` — dipanggil setiap kali bikin appointment
   - Search by NIK + DOB, balikin patient data per branch
   - **Dari sinilah MRN yang dipake diambil** (bukan dari column db profile)

2. **Appointment creation** (`/v1/transaction/patientmgmt/appointment/patient/create`):
   - `Simrs::Afya::Appointment::Create#assign_mrn_from_create_patient_check_result`
   - Priority MRN:
     1. `patient_check[:patient_data][:medical_record_number]` — dari check patient
     2. `patient_check[:patient_data][:mrn]`
     3. `response[:MedicalRecordNumber]` — dari response appointment create
   - **Update profile's MRN:** `profile.update(medical_record_number: mrn)`
   - **Appointment's MRN:** `appointment.mrn = mrn`

3. **Sync via CheckByNikDob** (`/v1/afyamobilefamily/getpatientlist/forfamily`):
   - Digunakan oleh `SyncAfyaMrn` service (cron job)
   - Endpoint berbeda dari check pasien di atas

#### Why Two Different MRNs Can Appear (Root Cause)

- **Profile MRN (`medical_record_number` column)**: Bisa dari kunjungan sebelumnya di branch lain
- **SIMRS Response MRN**: MRN spesifik untuk branch tujuan appointment

Contoh real:
| Source | MRN | Branch |
|--------|-----|-------|
| Profile DB column | 1190098741 | Branch A (kunjungan sebelumnya) |
| Afya appointment response | 1130144544 | Pasteur - Klinik Mata Padma |

#### Key Insight for Debugging

- Jangan bandingin `profile.medical_record_number` dengan response SIMRS langsung — bisa beda karena beda branch
- Yang bener dipake SIMRS untuk appointment itu MRN dari **response check patient per hospital**
- Kalau MRN di profile tidak update setelah appointment, cek:
  - Apakah `assign_mrn_from_create_patient_check_result` kepanggil?
  - Apakah patient_data dari check result ada `medical_record_number`?
  - Apakah `profile.update(medical_record_number: mrn)` berhasil (ada validasi?)
- Ada **dua endpoint check pasien berbeda**:
  1. `/v1/patientmgmt/master/patient/patientlist` — di `AfyaIntegrable#check_afya_patient` (dipake appointment create)
  2. `/v1/afyamobilefamily/getpatientlist/forfamily` — di `CheckByNikDob` (dipake sync MRN job)

---

### Base URL

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

### S3 Upload - ACL Public-Read (10 Apr 2026)

**Problem:** Files uploaded to S3 without `--acl public-read` returned AccessDenied when shared.

**Impact:** Users couldn't access shared files via public URLs.

**Root Cause:** Forgot to include `--acl public-read` flag in upload commands.

**Fix:**
1. Updated SKILL.md with critical warning about ACL
2. Added rule to TOOLS.md: ALWAYS use `--acl public-read`
3. Added MEMORY.md section for S3 upload best practices

**Rules:**
- ALWAYS include `--acl public-read` in all S3 upload commands
- ALWAYS share the public URL: `https://herminafiles.s3.amazonaws.com/halohermina/openclaw/<filename>`
- If AccessDenied occurs, fix immediately: `aws s3api put-object-acl --bucket herminafiles --key "halohermina/openclaw/<filename>" --acl public-read`

**Status:** ✅ Resolved - all documentation updated

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

## 📋 Hermina PEP Project Board

**Board:** <https://github.com/orgs/herminadev/projects/6> (Hermina PEP)

**Existing Issues Added:**
- hermina-mobile [#68](https://github.com/herminadev/hermina-mobile/issues/68) — Reset Password OTP Mobile
- hermina-core [#935](https://github.com/herminadev/hermina-core/issues/935) — BE Kirim OTP Email

**Rule:** Semua issue yang berkaitan atau dibahas di grup #hermina-pep wajib dimasukkan ke project ini sebagai **Backlog**.

**Constraint:** GitHub token perlu `project` write scope untuk auto-add via API. Saat ini cuma `read:project`.

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
| Z.AI (GLM-5) | ✅ Active | API key updated 10 Apr 2026 |
| Gemini Live API | ✅ Active | Default model: `gemini-3-pro-preview` |
| OpenAI | ❌ Billing Limit | Hard limit reached - cannot use image editing |
| Anthropic | ❌ Credit Low | Balance too low |
| Image Models | ⚠️ Limited | All paid models down — using Tesseract OCR as fallback |
| SmartThings | ✅ Working | Token active |
| Bird CLI | ✅ Working | Cookie-based auth |
| Claude Code | ✅ Working | v2.1.89, alias `cc` in .zshrc |

---

## 📦 S3 Upload (herminafiles)

### Configuration
- **Bucket:** `herminafiles`
- **Base path:** `halohermina/openclaw/`
- **Public URL format:** `https://herminafiles.s3.amazonaws.com/halohermina/openclaw/<filename>`

### Upload Commands (with ACL)
```bash
# Single file
aws s3 cp <local-path> s3://herminafiles/halohermina/openclaw/<filename> --acl public-read

# Multiple files
aws s3 cp <local-path> s3://herminafiles/halohermina/openclaw/ --recursive --acl public-read
```

### Critical Rules (10 Apr 2026)
- ✅ **ALWAYS include `--acl public-read`** - files are for public sharing
- ✅ **ALWAYS share the public URL** after upload
- ✅ **If AccessDenied occurs**, fix immediately:
  ```bash
  aws s3api put-object-acl --bucket herminafiles --key "halohermina/openclaw/<filename>" --acl public-read
  ```

---

## 📋 User Preferences & Rules

### Decision History

1. Read **ALL** memory files (not just today+yesterday) - changed in AGENTS.md
2. Auto-execute expense tracking without confirmation
3. Prefer local tools over cloud APIs when possible
4. Use fallback TTS while Gemini Live API has issues
5. **S3 uploads MUST use `--acl public-read`** - always share public URL, fix AccessDenied immediately

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

## 🔧 Config Changes (April 2026)

### Default Model
- Changed from `zai/glm-4.7` → `zai/glm-5` (10 Apr 2026)
- Fallback chain: glm-4.7, glm-5v-turbo, glm-5-turbo, glm-5
- Z.AI API key updated (10 Apr 2026)

### Cron Jobs
- **bug-triage**: Changed from weekdays-only to everyday (`0 6-18/3 * * *`)
- **daily-error-report**: Changed from weekdays-only to everyday, reads last 5 messages from #errors
- Both use Slack channel ID `C09KB8DU7DW` (not `#errors` name)
- Timeout: 300 seconds (increased from 120)

### OpenClaw Version
- Updated to **2026.4.11** (12 Apr 2026)
- Key improvements: timeout handling, failover, Dreaming ChatGPT import

### Skills Added
- **s3-upload** (`~/.openclaw/workspace/skills/s3-upload/`) — Auto-upload to `herminafiles` bucket

### OCR Fallback
- When image models are unavailable (billing/quotas), use **Tesseract OCR** (`tesseract <img> stdout -l ind+eng`)
- Works well for Indonesian receipts

---

*Last updated: 13 Apr 2026*

## Promoted From Short-Term Memory (2026-04-24)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:443:445 -->
- - Candidate: Possible Lasting Truths: Bug Triage & Daily Report Cron Fixes: **Fixes Applied:** [confidence=0.58 evidence=memory/2026-04-08.md:11-11]; Bug Triage & Daily Report Cron Fixes: **Problem:** Daily error report and bug-triage cron jobs kept failing with model errors. [confidence=0.58 - confidence: 0.62 - evidence: memory/2026-04-15.md:458-460 [score=0.845 recalls=0 avg=0.620 source=memory/2026-04-16.md:13-15]
<!-- openclaw-memory-promotion:memory:memory/2026-04-17.md:388:390 -->
- - Candidate: Possible Lasting Truths: Bug Triage & Daily Report Cron Fixes: **Fixes Applied:** [confidence=0.58 evidence=memory/2026-04-08.md:11-11]; Bug Triage & Daily Report Cron Fixes: **Problem:** Daily error report and bug-triage cron jobs kept failing with model errors. [confidence=0.58 - confidence: 0.62 - evidence: memory/2026-04-16.md:443-445 [score=0.845 recalls=0 avg=0.620 source=memory/2026-04-17.md:13-15]
<!-- openclaw-memory-promotion:memory:memory/2026-04-18.md:438:440 -->
- - Candidate: Possible Lasting Truths: Bug Triage & Daily Report Cron Fixes: **Fixes Applied:** [confidence=0.58 evidence=memory/2026-04-08.md:11-11]; Bug Triage & Daily Report Cron Fixes: **Problem:** Daily error report and bug-triage cron jobs kept failing with model errors. [confidence=0.58 - confidence: 0.62 - evidence: memory/2026-04-17.md:388-390 [score=0.838 recalls=0 avg=0.620 source=memory/2026-04-18.md:168-170]

## Promoted From Short-Term Memory (2026-04-26)

<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:424:426 -->
- - Candidate: Possible Lasting Truths: Bug Fix: Hermina Run Resend Email Confirmation: "Translation missing: id.hermina_run_participants.resend.success"; "can't find record with friendly id: \"undefined\"" - resend sends undefined [confidence=0.58 evidence=memory/2026-04-14.md:353-354]; Bug Fi - confidence: 0.62 - evidence: memory/2026-04-19.md:444-446 [score=0.849 recalls=0 avg=0.620 source=memory/2026-04-20.md:173-175]
<!-- openclaw-memory-promotion:memory:memory/2026-04-22.md:298:301 -->
- - Candidate: Reflections: Theme: `assistant` kept surfacing across 433 memories.; confidence: 1.00; evidence: memory/2026-04-09.md:221-224, memory/2026-04-10.md:397-400, memory/2026-04-11.md:452-455; note: reflection - confidence: 0.62 - evidence: memory/2026-04-22.md:333-336 - recalls: 0 [score=0.836 recalls=0 avg=0.620 source=memory/2026-04-22.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-04-22.md:308:310 -->
- - Candidate: Possible Lasting Truths: Bug Fix: Hermina Run Resend Email Confirmation: "Translation missing: id.hermina_run_participants.resend.success"; "can't find record with friendly id: \"undefined\"" - resend sends undefined [confidence=0.58 evidence=memory/2026-04-14.md:353-354]; Bug Fi - confidence: 0.62 - evidence: memory/2026-04-21.md:318-320 [score=0.836 recalls=0 avg=0.620 source=memory/2026-04-22.md:123-125]

## Promoted From Short-Term Memory (2026-04-27)

<!-- openclaw-memory-promotion:memory:memory/2026-04-21.md:318:320 -->
- - Candidate: Possible Lasting Truths: Bug Fix: Hermina Run Resend Email Confirmation: "Translation missing: id.hermina_run_participants.resend.success"; "can't find record with friendly id: \"undefined\"" - resend sends undefined [confidence=0.58 evidence=memory/2026-04-14.md:353-354]; Bug Fi - confidence: 0.62 - evidence: memory/2026-04-20.md:424-426 [score=0.857 recalls=0 avg=0.620 source=memory/2026-04-21.md:163-165]

## Promoted From Short-Term Memory (2026-05-12)

<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:5:5 -->
- Yana explained: di Afya setiap RS/branch punya MRN beda-beda. 1 pasien punya banyak MRN tergantung di mana pernah berobat. Yang dicatat di Halo Hermina itu dari API balikan check patient — bukan MRN global. [score=0.865 recalls=0 avg=0.620 source=memory/2026-05-07.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:7:7 -->
- Saved detailed knowledge base entry ke MEMORY.md. [score=0.865 recalls=0 avg=0.620 source=memory/2026-05-07.md:7-7]
