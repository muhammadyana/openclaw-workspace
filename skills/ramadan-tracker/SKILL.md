---
name: ramadan-tracker
description: Track Ramadan prayer times, set sahur and iftar reminders, and provide healthy iftar menu recommendations. Use when setting up Ramadan schedules, managing prayer time reminders, getting iftar menu suggestions, or automating daily fasting reminders with location-based prayer times.
---

# Ramadan Tracker

Skill untuk mengelola jadwal puasa Ramadan lengkap dengan reminder otomatis dan rekomendasi menu buka puasa sehat.

## Fitur

- 📍 **Location-based prayer times** - Jadwal sholat sesuai lokasi (default: Bandung)
- 🌅 **Sahur reminders** - 1 jam, 30 menit, dan 5 menit sebelum imsak
- 🌙 **Iftar reminders** - 5 menit sebelum buka dan ucapan buka puasa
- 🍽️ **Healthy menu recommendations** - Rotating menu buka puasa sehat
- ⏰ **Auto cron setup** - Generate cron jobs untuk semua reminder

## Lokasi Default

**Jl. Tubagus Ismail VII No.11 ASekeloa, Kecamatan Coblong, Kota Bandung, Jawa Barat 40134**

Koordinat: -6.8735, 107.6190

## Quick Start

### Lihat Jadwal Hari Ini
```bash
python3 "$SKILL_DIR/scripts/ramadan.py" today
python3 "$SKILL_DIR/scripts/ramadan.py" today --telegram  # Format mobile-friendly
```

### Lihat Menu Buka Puasa
```bash
python3 "$SKILL_DIR/scripts/ramadan.py" menu
```

### Cek Lokasi
```bash
python3 "$SKILL_DIR/scripts/ramadan.py" location
```

### Telegram Button Config
```bash
python3 "$SKILL_DIR/scripts/ramadan.py" buttons
```

### Setup Reminder Otomatis
```bash
# Generate cron jobs
python3 "$SKILL_DIR/scripts/ramadan.py" setup

# Lihat file cron yang di-generate
cat ~/.openclaw/workspace/ramadan_cron_jobs.json
```

## Reminder Schedule

| Reminder | Waktu | Keterangan |
|----------|-------|------------|
| Sahur 1 jam | Imsak - 1 jam | Persiapan sahur |
| Sahur 30 menit | Imsak - 30 menit | Waktu sahur tinggal sedikit |
| Imsak 5 menit | Imsak - 5 menit | Segera selesaikan makan |
| Buka 5 menit | Maghrib - 5 menit | Siapkan menu + doa |
| Buka puasa | Maghrib | Ucapan berbuka + reminder sholat |

## Ganti Lokasi

Untuk mengganti lokasi, edit file `scripts/ramadan.py` dan ubah `DEFAULT_LOCATION`:

```python
DEFAULT_LOCATION = {
    "city": "Nama Kota",
    "country": "Indonesia", 
    "latitude": -6.xxxx,
    "longitude": 107.xxxx,
    "timezone": "Asia/Jakarta"
}
```

Cari koordinat di Google Maps atau website prayer time.

## API Prayer Times

Menggunakan Al-Adhan API (https://aladhan.com/prayer-times-api) dengan:
- **Method**: 11 (Kemenag Indonesia)
- **City lookup**: Bandung, Indonesia (untuk akurasi lebih tinggi)
- **Tune adjustments**: `3,3,3,0,0,7,7,0,0` untuk sinkron dengan Kemenag Bandung resmi

### Perbandingan Jadwal

| Waktu | Kemenag Bandung (Muslim Pro) | Sistem |
|-------|------------------------------|--------|
| Imsak | 04:28 | 04:28 ✓ |
| Subuh | 04:38 | 04:38 ✓ |
| Maghrib | 18:19 | 18:19 ✓ |

Jadwal sudah sinkron dengan aplikasi Muslim Pro (Kemenag) untuk lokasi Bandung.

## Contoh Output

```
📅 Jadwal Ramadan Hari Ini (19 Februari 2026)
📍 Lokasi: Bandung, Indonesia

🌅 Waktu Sholat:
• Imsak: 04:31
• Subuh: 04:41
• Dzuhur: 12:08
• Ashar: 15:30
• Maghrib (Buka): 18:14
• Isya: 19:23

⏰ Jadwal Reminder:
• Sahur (1 jam): 03:31
• Sahur (30 min): 04:01
• 5 menit sebelum imsak: 04:26
• 5 menit sebelum buka: 18:09
```

## Dependencies

```bash
pip install requests
```

## Catatan

- Script menggunakan API online, memerlukan internet
- Waktu mengikuti timezone Asia/Jakarta
- Metode perhitungan: Kemenag Indonesia
- Cron jobs di-generate ke file JSON, perlu di-import manual ke OpenClaw cron
