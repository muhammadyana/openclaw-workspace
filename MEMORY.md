# MEMORY.md

*Catatan penting untuk diingat antar sesi*

---

## 📹 CCTV / Camera Behavior

**Rule:** Setiap kali Yana bertanya "apa yang kamu lihat" (atau variasi seperti "what do you see", "what you see", "apa yang dilihat", dll), **SELALU** lakukan:

1. Ambil snapshot dari kamera Tapo C222 menggunakan `camsnap`
2. Kirim gambar tersebut ke channel
3. Deskripsikan isi gambar jika dimungkinkan

**Camera details:**
- Nama: Tapo C222
- RTSP: `rtsp://iotcctv:SmartHome@192.168.31.133:554/stream1`
- Script: `/Users/yana/works/iot/bin/camera-open`
- IP: 192.168.31.133
- Resolution: 2560x1440 (2K)

**SOP lengkap:** Lihat `TOOLS.md` bagian CCTV Surveillance Commands

---

## 🏥 Hermina Hospital API

Base URL: `https://api.herminahospitals.com/api/v1/`

Key endpoints:
- `GET /public/hospitals?q={branch}` - Cari rumah sakit
- `GET /public/doctors?hospital_id={id}&speciality_id={spec}` - Cari dokter
- `GET /public/doctors/{slug}/schedules?schedule_type=executive&type=table` - Jadwal dokter

Hospital IDs: Jatinegara=1, Kemayoran=2, Pasteur=7, Arcamanik=13

---

## 💰 Expense Tracker

**Auto-execute tanpa konfirmasi** — kalau Yana upload struk, langsung proses tanpa tanya.

```bash
~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py add /path/to/receipt.jpg
```

---

## 🐦 X/Twitter

Connected to: **@namdoyan** (Yaya 🇵🇸)
CLI: `bird tweet "text"`, `bird reply <id> "text"`

---

## ⚠️ API Status

| Service | Status |
|---------|--------|
| Gemini Live API | ❌ 404 Error (needs setup) |
| OpenAI | ❌ Billing limit reached |
| SmartThings | ✅ Working |
| Bird CLI | ✅ Working |

---

*Catatan ini dibuat: 19 Feb 2026*
