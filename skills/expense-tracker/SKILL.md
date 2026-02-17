---
name: expense-tracker
description: Track expenses from receipt photos with OCR, auto-categorization, SQLite/Excel storage, and chart reporting
---

# Expense Tracker

Sistem pencatatan keuangan otomatis dari foto struk/invoice dengan OCR, kategorisasi otomatis, dan laporan grafik.

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

### Laporan Bulanan
```bash
python3 "$SKILL_DIR/scripts/expense.py" report --bulan 2 --tahun 2026
```

### Export ke Excel
```bash
python3 "$SKILL_DIR/scripts/expense.py" export --output ~/expenses_2026.xlsx
```

### Generate Chart
```bash
python3 "$SKILL_DIR/scripts/expense.py" chart --bulan 2
```

### Daily Report (Manual)
```bash
python3 "$SKILL_DIR/scripts/daily_report.py"
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

# Summary/statistics
python3 "$SKILL_DIR/scripts/expense.py" summary [--bulan N] [--tahun YYYY]

# Generate charts (PNG)
python3 "$SKILL_DIR/scripts/expense.py" chart [--bulan N] [--tahun YYYY] [--output path.png]

# Export
python3 "$SKILL_DIR/scripts/expense.py" export [--format excel|csv] [--output path]

# Delete expense
python3 "$SKILL_DIR/scripts/expense.py" delete <id>

# Daily report (manual trigger)
python3 "$SKILL_DIR/scripts/daily_report.py"
```

## Dependencies

```bash
pip install pytesseract pillow openpyxl pandas matplotlib seaborn
```

**Note**: Install Tesseract OCR:
- macOS: `brew install tesseract tesseract-lang`
- Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-ind`
