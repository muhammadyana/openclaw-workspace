---
name: expense-tracker
description: Track expenses from receipt photos with OCR, auto-categorization, SQLite/Excel storage, and chart reporting. When user asks about expenses, ALWAYS use the exec tool to run the commands and show the output.
---

# Expense Tracker

Sistem pencatatan keuangan otomatis dari foto struk/invoice dengan OCR, kategorisasi otomatis, dan laporan grafik.

## IMPORTANT - Execution Instructions

When user asks anything about expenses (pengeluaran), you MUST:
1. Use the `exec` tool to run the Python script
2. Capture the output
3. Return the output to user

DO NOT just type the command as text - EXECUTE it using the shell/exec tool.

Example execution:
- Tool: `exec` or `shell`
- Command: `python3 ~/.openclaw/workspace/skills/expense-tracker/scripts/expense.py list --dari today --telegram`

## Fitur

- 📸 **OCR**: Extract text dari foto struk
- 💰 **Auto-extract**: Merchant, total, tanggal, items
- 🏷️ **Auto-kategorisasi**: Makanan, Transport, Belanja, dll
- 💾 **Dual storage**: SQLite (default) + Excel export
- 📊 **Chart**: Grafik pengeluaran per kategori & waktu
- 🔍 **Filter**: By kategori, tanggal, merchant
- 📅 **Daily Report**: Laporan otomatis jam 22:00 via Telegram

## Quick Start

### Tambah Expense dari Foto
```bash
python3 "$SKILL_DIR/scripts/expense.py" add /path/to/receipt.jpg
```

### Lihat Semua Expense
```bash
python3 "$SKILL_DIR/scripts/expense.py" list
```

### Filter by Kategori
```bash
python3 "$SKILL_DIR/scripts/expense.py" list --kategori "Makanan"
```

### Laporan Harian (Daily Report)
```bash
python3 "$SKILL_DIR/scripts/expense.py" daily              # Hari ini
python3 "$SKILL_DIR/scripts/expense.py" daily -d 2026-02-20  # Tanggal spesifik
python3 "$SKILL_DIR/scripts/expense.py" daily --telegram     # Format mobile-friendly
```

### List dengan Format Telegram
```bash
python3 "$SKILL_DIR/scripts/expense.py" list --dari today --telegram
```

### Laporan Bulanan
```bash
python3 "$SKILL_DIR/scripts/expense.py" summary --bulan 2 --tahun 2026
```

### Export ke Excel
```bash
python3 "$SKILL_DIR/scripts/expense.py" export --output ~/expenses_2026.xlsx
```

### Generate Chart
```bash
python3 "$SKILL_DIR/scripts/expense.py" chart --bulan 2
```

### Telegram Button Config
```bash
python3 "$SKILL_DIR/scripts/expense.py" buttons
```

## Daily Report (Cron Job)

Setiap hari jam 22:00 WIB, laporan pengeluaran otomatis dikirim via Telegram.

**Fitur laporan:**
- 📊 Total pengeluaran hari ini
- 📂 Breakdown per kategori
- 📝 Detail transaksi
- 📈 Perbandingan dengan hari sebelumnya
- 📊 Total bulan ini + proyeksi

**Cron job ID:** `9ab992a2-0490-4a09-bb00-8682f2f7ef90`
**Schedule:** `0 22 * * *` (Setiap hari jam 22:00 WIB)

## Kategori Default

| Kategori | Keyword Trigger |
|----------|-----------------|
| Makanan | restoran, cafe, food, makan, minum, warung |
| Transport | bbm, gojek, grab, parkir, toll, bensin |
| Belanja | indomaret, alfamart, supermarket, mall, toko |
| Hiburan | bioskop, game, spotify, netflix, hiburan |
| Kesehatan | apotek, klinik, rumah sakit, obat |
| Utilitas | pln, pdam, internet, pulsa, listrik, air |
| Lainnya | (default) |

## Database Schema

**SQLite**: `~/.openclaw/workspace/expenses.db`

```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal DATE,
    merchant TEXT,
    total REAL,
    kategori TEXT,
    items TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Command Reference

```bash
# Add expense (interactive/manual)
python3 "$SKILL_DIR/scripts/expense.py" add [image_path]
python3 "$SKILL_DIR/scripts/expense.py" add --manual

# List dengan filter
python3 "$SKILL_DIR/scripts/expense.py" list [--kategori X] [--dari YYYY-MM-DD] [--sampai YYYY-MM-DD]
python3 "$SKILL_DIR/scripts/expense.py" list --dari today  # Hari ini

# Daily report
python3 "$SKILL_DIR/scripts/expense.py" daily [--tanggal YYYY-MM-DD]

# Summary/statistics
python3 "$SKILL_DIR/scripts/expense.py" summary [--bulan N] [--tahun YYYY]

# Generate charts (PNG)
python3 "$SKILL_DIR/scripts/expense.py" chart [--bulan N] [--tahun YYYY] [--output path.png]

# Export
python3 "$SKILL_DIR/scripts/expense.py" export [--format excel|csv] [--output path]

# Delete expense
python3 "$SKILL_DIR/scripts/expense.py" delete <id>

# Get Telegram button config
python3 "$SKILL_DIR/scripts/expense.py" buttons
```

## Telegram Button Shortcuts

Untuk integrasi dengan Telegram bot, gunakan output dari command `buttons`:

```bash
python3 "$SKILL_DIR/scripts/expense.py" buttons
```

Output JSON:
```json
{
  "inline_keyboard": [
    [
      {"text": "📊 Daily Report", "callback_data": "/expense daily"},
      {"text": "📈 Monthly", "callback_data": "/expense summary --bulan 2"}
    ],
    [
      {"text": "📝 List Today", "callback_data": "/expense list --dari today"},
      {"text": "📉 Chart", "callback_data": "/expense chart"}
    ],
    [
      {"text": "💾 Export Excel", "callback_data": "/expense export"}
    ]
  ]
}
```

## Dependencies

```bash
pip install pytesseract pillow openpyxl pandas matplotlib seaborn
```

**Note**: Install Tesseract OCR:
- macOS: `brew install tesseract tesseract-lang`
- Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-ind`
