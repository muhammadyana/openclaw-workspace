#!/usr/bin/env python3
"""
Expense Tracker - Sistem pencatatan keuangan otomatis
"""

import os
import sys
VENV_PATH = os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages")
if os.path.exists(VENV_PATH) and VENV_PATH not in sys.path:
    sys.path.insert(0, VENV_PATH)

import re
import json
import sqlite3
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, Dict

# OCR removed - manual input only

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.chart import PieChart, Reference
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

try:
    from telegram_format import format_daily_report, format_list
    TELEGRAM_FORMAT_AVAILABLE = True
except ImportError:
    TELEGRAM_FORMAT_AVAILABLE = False
    
    # Define fallback formatters
    def format_daily_report(rows, cat_summary, total_all, date_str, comparison=None):
        emoji_map = {"Makanan": "🍽️", "Transport": "🚗", "Belanja": "🛒",
                     "Hiburan": "🎬", "Kesehatan": "💊", "Utilitas": "⚡", "Lainnya": "📦"}
        lines = [f"📅 Daily Report - {date_str}", ""]
        lines.append(f"💰 Total: Rp {total_all:,.0f} ({len(rows)} transaksi)")
        
        if comparison:
            diff = comparison["diff"]
            diff_pct = comparison["diff_pct"]
            yest_total = comparison["yesterday_total"]
            yest_count = comparison["yesterday_count"]
            if diff > 0:
                emoji_diff, diff_text = "📈", f"+Rp {diff:,.0f} (+{diff_pct:.1f}%)"
            elif diff < 0:
                emoji_diff, diff_text = "📉", f"-Rp {abs(diff):,.0f} ({diff_pct:.1f}%)"
            else:
                emoji_diff, diff_text = "➡️", "Sama dengan kemarin"
            lines.append(f"{emoji_diff} vs Kemarin: {diff_text}")
            lines.append(f"   (Kemarin: Rp {yest_total:,.0f}, {yest_count} transaksi)")
        
        lines.append("")
        lines.append("📂 Per Kategori:")
        for row in cat_summary:
            emoji = emoji_map.get(row["kategori"], "📦")
            lines.append(f"{emoji} {row['kategori']}: Rp {row['total']:,.0f} ({row['count']}x)")
        lines.append("")
        lines.append("📝 Detail Transaksi:")
        for row in rows:
            emoji = emoji_map.get(row["kategori"], "📦")
            lines.append(f"#{row['id']} {emoji} {row['merchant'][:25]}")
            lines.append(f"└ Rp {row['total']:,.0f}")
        return "\n".join(lines)

    def format_list(rows, total_all, comparison=None):
        emoji_map = {"Makanan": "🍽️", "Transport": "🚗", "Belanja": "🛒",
                     "Hiburan": "🎬", "Kesehatan": "💊", "Utilitas": "⚡", "Lainnya": "📦"}
        lines = [f"📋 Expenses ({len(rows)} items)"]
        
        if comparison:
            diff = comparison["diff"]
            diff_pct = comparison["diff_pct"]
            yest_total = comparison["yesterday_total"]
            yest_count = comparison["yesterday_count"]
            if diff > 0:
                emoji_diff, diff_text = "📈", f"+Rp {diff:,.0f} (+{diff_pct:.1f}%)"
            elif diff < 0:
                emoji_diff, diff_text = "📉", f"-Rp {abs(diff):,.0f} ({diff_pct:.1f}%)"
            else:
                emoji_diff, diff_text = "➡️", "Sama dengan kemarin"
            lines.append(f"{emoji_diff} vs Kemarin: {diff_text}")
            lines.append(f"   (Kemarin: Rp {yest_total:,.0f}, {yest_count} transaksi)")
        
        lines.append("")
        for row in rows:
            emoji = emoji_map.get(row["kategori"], "📦")
            lines.append(f"#{row['id']} {emoji} {row['merchant'][:25]}")
            lines.append(f"   ├ {row['kategori']} • {row['tanggal']}")
            lines.append(f"   └ Rp {row['total']:,.0f}")
            lines.append("")
        lines.append(f"💰 Total: Rp {total_all:,.0f}")
        return "\n".join(lines)

DB_PATH = Path(os.path.expanduser("~/.openclaw/workspace/expenses.db"))
DEFAULT_EXCEL_PATH = Path(os.path.expanduser("~/expenses.xlsx"))

KATEGORI_KEYWORDS = {
    "Makanan": ["restoran", "cafe", "food", "makan", "minum", "warung", "bakso", "sate", "nasi", "kopi", "coffee"],
    "Transport": ["bbm", "gojek", "grab", "parkir", "toll", "bensin", "pertamina", "shell", "transport"],
    "Belanja": ["indomaret", "alfamart", "supermarket", "mall", "toko", "shop", "minimarket"],
    "Hiburan": ["bioskop", "cinema", "game", "spotify", "netflix", "youtube", "disney", "steam"],
    "Kesehatan": ["apotek", "klinik", "rumah sakit", "hospital", "obat", "pharmacy", "dokter"],
    "Utilitas": ["pln", "pdam", "internet", "pulsa", "listrik", "air", "wifi", "telepon", "token"],
}

def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE, merchant TEXT, total REAL, kategori TEXT,
            items TEXT, file_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tanggal ON expenses(tanggal)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kategori ON expenses(kategori)")
    conn.commit()
    conn.close()

def detect_kategori(merchant, items=""):
    text = f"{merchant} {items}".lower()
    for kategori, keywords in KATEGORI_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return kategori
    return "Lainnya"

def get_yesterday_comparison(conn, today_total, today_count, target_date):
    yesterday = target_date - timedelta(days=1)
    row = conn.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as total FROM expenses WHERE tanggal = ?",
        (yesterday,)
    ).fetchone()
    yesterday_total, yesterday_count = row["total"], row["count"]
    if yesterday_total == 0 and yesterday_count == 0:
        return None
    diff = today_total - yesterday_total
    diff_pct = (diff / yesterday_total * 100) if yesterday_total > 0 else 0
    return {"yesterday_total": yesterday_total, "yesterday_count": yesterday_count, "diff": diff, "diff_pct": diff_pct}

def add_expense(image_path=None, manual=False, direct_merchant=None, direct_total=None, direct_tanggal=None, direct_kategori=None, no_ocr=False):
    init_db()
    
    if direct_merchant and direct_total is not None:
        merchant, total = direct_merchant, float(direct_total)
        tanggal = date.fromisoformat(direct_tanggal) if direct_tanggal else date.today()
        kategori = direct_kategori or detect_kategori(merchant)
        items, file_path = "Direct input", image_path
        print(f"\n📸 Processing (Direct Input)")
        print(f"   Merchant: {merchant}\n   Total: Rp {total:,.0f}\n   Tanggal: {tanggal}\n   Kategori: {kategori}")
    else:
        # Manual input only - no OCR
        print("\n📋 Input Manual Expense")
        print("-" * 40)
        merchant = input("Merchant: ").strip()
        total = float(input("Total (Rp): ").strip().replace(".", "").replace(",", ""))
        tanggal_input = input("Tanggal (YYYY-MM-DD, kosong=hari ini): ").strip()
        tanggal = date.fromisoformat(tanggal_input) if tanggal_input else date.today()
        items = input("Items (optional): ").strip()
        kategori = input(f"Kategori (default: {detect_kategori(merchant, items)}): ").strip() or detect_kategori(merchant, items)
    
    conn = get_db_connection()
    conn.execute("INSERT INTO expenses (tanggal, merchant, total, kategori, items, file_path) VALUES (?, ?, ?, ?, ?, ?)",
                 (tanggal, merchant, total, kategori, items, image_path))
    conn.commit()
    expense_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    print(f"\n✅ Expense saved! ID: {expense_id}\n   Rp {total:,.0f} - {merchant} ({kategori})")

def list_expenses(kategori=None, dari=None, sampai=None, telegram_format=False, compare=True):
    init_db()
    conn = get_db_connection()
    query, params = "SELECT * FROM expenses WHERE 1=1", []
    
    from_date = None
    if kategori:
        query += " AND kategori = ?"
        params.append(kategori)
    if dari:
        from_date = date.fromisoformat(dari) if dari != "today" else date.today()
        query += " AND tanggal >= ?"
        params.append(from_date.isoformat())
    if sampai:
        to_date = date.fromisoformat(sampai) if sampai != "today" else date.today()
        query += " AND tanggal <= ?"
        params.append(to_date.isoformat())
    
    query += " ORDER BY tanggal DESC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    
    if not rows:
        print("\n📭 No expenses found")
        conn.close()
        return
    
    total_all = sum(row["total"] for row in rows)
    
    # Get comparison with yesterday
    comparison = None
    if compare and dari and not sampai:
        today = date.today()
        if from_date == today:
            comparison = get_yesterday_comparison(conn, total_all, len(rows), today)
    
    conn.close()
    
    if telegram_format:
        print(format_list(rows, total_all, comparison))
    else:
        print(f"\n📊 Expenses ({len(rows)} items)")
        if comparison:
            print(format_comparison_line(comparison))
            print()
        print("-" * 80)
        print(f"{'ID':<5} {'Tanggal':<12} {'Kategori':<12} {'Merchant':<20} {'Total':>15}")
        print("-" * 80)
        for row in rows:
            print(f"{row['id']:<5} {row['tanggal']:<12} {row['kategori']:<12} {row['merchant'][:20]:<20} Rp {row['total']:>12,.0f}")
        print("-" * 80)
        print(f"{'Total':>52} Rp {total_all:>12,.0f}")

def format_comparison_line(comparison):
    diff = comparison["diff"]
    diff_pct = comparison["diff_pct"]
    yest_total = comparison["yesterday_total"]
    yest_count = comparison["yesterday_count"]
    if diff > 0:
        return f"📈 vs Kemarin: +Rp {diff:,.0f} (+{diff_pct:.1f}%)\n   (Kemarin: Rp {yest_total:,.0f}, {yest_count} transaksi)"
    elif diff < 0:
        return f"📉 vs Kemarin: -Rp {abs(diff):,.0f} ({diff_pct:.1f}%)\n   (Kemarin: Rp {yest_total:,.0f}, {yest_count} transaksi)"
    else:
        return f"➡️ vs Kemarin: Sama\n   (Kemarin: Rp {yest_total:,.0f}, {yest_count} transaksi)"

def daily_report(tanggal=None, telegram_format=True, compare=True):
    init_db()
    conn = get_db_connection()
    
    if tanggal:
        try:
            target_date = date.fromisoformat(tanggal)
        except ValueError:
            print(f"❌ Invalid date format: {tanggal}")
            return
    else:
        target_date = date.today()
    
    rows = conn.execute("SELECT * FROM expenses WHERE tanggal = ? ORDER BY created_at DESC", (target_date,)).fetchall()
    
    if not rows:
        print("📭 No expenses today")
        conn.close()
        return
    
    cat_summary = conn.execute("""
        SELECT kategori, COUNT(*) as count, SUM(total) as total 
        FROM expenses WHERE tanggal = ? GROUP BY kategori ORDER BY total DESC
    """, (target_date,)).fetchall()
    
    total_all = sum(row["total"] for row in rows)
    
    # Get comparison
    comparison = None
    if compare:
        comparison = get_yesterday_comparison(conn, total_all, len(rows), target_date)
    
    conn.close()
    
    if telegram_format:
        date_str = target_date.strftime("%A, %d %B %Y")
        print(format_daily_report(rows, cat_summary, total_all, date_str, comparison))
    else:
        date_str = target_date.strftime("%A, %d %B %Y")
        print(f"\n📅 Daily Report - {date_str}")
        print("=" * 60)
        print(f"\n💰 Total: Rp {total_all:,.0f} ({len(rows)} transaksi)")
        if comparison:
            print(format_comparison_line(comparison))
        print()
        print("📂 Per Kategori:")
        print("-" * 40)
        emoji_map = {"Makanan": "🍽️", "Transport": "🚗", "Belanja": "🛒",
                     "Hiburan": "🎬", "Kesehatan": "💊", "Utilitas": "⚡"}
        for row in cat_summary:
            emoji = emoji_map.get(row["kategori"], "📦")
            print(f"   {emoji} {row['kategori']:<12} Rp {row['total']:>10,.0f} ({row['count']}x)")
        print(f"\n📝 Detail Transaksi:")
        print("-" * 60)
        for row in rows:
            print(f"   #{row['id']} | {row['merchant'][:20]:<20} | Rp {row['total']:>10,.0f}")

def edit_expense(expense_id, merchant=None, total=None, tanggal=None, kategori=None):
    init_db()
    conn = get_db_connection()
    
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if not row:
        print(f"❌ Expense {expense_id} not found")
        conn.close()
        return
    
    print(f"\n✏️  Editing expense #{expense_id}:")
    print(f"   Current: {row['tanggal']} | {row['merchant']} | Rp {row['total']:,.0f} | {row['kategori']}")
    
    new_merchant = merchant if merchant is not None else row["merchant"]
    new_total = total if total is not None else row["total"]
    new_tanggal = tanggal if tanggal is not None else row["tanggal"]
    new_kategori = kategori if kategori is not None else row["kategori"]
    
    print(f"\n📝 New values:")
    print(f"   Merchant: {new_merchant}\n   Total: Rp {new_total:,.0f}\n   Tanggal: {new_tanggal}\n   Kategori: {new_kategori}")
    
    conn.execute("UPDATE expenses SET merchant = ?, total = ?, tanggal = ?, kategori = ? WHERE id = ?",
                 (new_merchant, new_total, new_tanggal, new_kategori, expense_id))
    conn.commit()
    print(f"\n✅ Expense #{expense_id} updated!")
    conn.close()

def delete_expense(expense_id):
    init_db()
    conn = get_db_connection()
    
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if not row:
        print(f"❌ Expense {expense_id} not found")
        conn.close()
        return
    
    print(f"\n🗑️  Will delete:")
    print(f"   ID: {row['id']}\n   {row['tanggal']} - {row['merchant']}\n   Rp {row['total']:,.0f} ({row['kategori']})")
    
    confirm = input("\nConfirm delete? [y/N]: ").strip().lower()
    if confirm == "y":
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        print("✅ Deleted")
    else:
        print("❌ Cancelled")
    conn.close()

def summary(bulan=None, tahun=datetime.now().year):
    init_db()
    conn = get_db_connection()
    
    if bulan:
        dari = f"{tahun}-{bulan:02d}-01"
        sampai = f"{tahun+1}-01-01" if bulan == 12 else f"{tahun}-{bulan+1:02d}-01"
        where_clause = f"WHERE tanggal >= '{dari}' AND tanggal < '{sampai}'"
        period_label = f"{datetime(tahun, bulan, 1).strftime('%B %Y')}"
    else:
        dari, sampai = f"{tahun}-01-01", f"{tahun+1}-01-01"
        where_clause = f"WHERE tanggal >= '{dari}' AND tanggal < '{sampai}'"
        period_label = f"Tahun {tahun}"
    
    print(f"\n📈 Ringkasan Pengeluaran - {period_label}")
    print("=" * 50)
    
    total = conn.execute(f"SELECT COALESCE(SUM(total), 0) FROM expenses {where_clause}").fetchone()[0]
    count = conn.execute(f"SELECT COUNT(*) FROM expenses {where_clause}").fetchone()[0]
    print(f"\n📊 Total: Rp {total:,.0f} ({count} transaksi)")
    
    print(f"\n📂 Per Kategori:")
    print("-" * 35)
    cat_rows = conn.execute(f"SELECT kategori, COUNT(*) as count, SUM(total) as total FROM expenses {where_clause} GROUP BY kategori ORDER BY total DESC").fetchall()
    for row in cat_rows:
        pct = (row["total"] / total * 100) if total > 0 else 0
        print(f"   {row['kategori']:<15} Rp {row['total']:>10,.0f} ({pct:5.1f}%) [{row['count']}x]")
    
    print(f"\n🏪 Top Merchants:")
    print("-" * 35)
    merch_rows = conn.execute(f"SELECT merchant, SUM(total) as total, COUNT(*) as count FROM expenses {where_clause} GROUP BY merchant ORDER BY total DESC LIMIT 5").fetchall()
    for row in merch_rows:
        print(f"   {row['merchant'][:20]:<20} Rp {row['total']:>10,.0f} [{row['count']}x]")
    conn.close()

def export_to_excel(output_path=None, format_type="excel"):
    if format_type == "excel" and not EXCEL_AVAILABLE:
        print("❌ openpyxl not installed")
        return
    init_db()
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY tanggal DESC", conn)
    conn.close()
    
    output = Path(output_path) if output_path else DEFAULT_EXCEL_PATH
    if format_type == "csv":
        output = output.with_suffix(".csv")
        df.to_csv(output, index=False)
    else:
        output = output.with_suffix(".xlsx")
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Expenses", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Expenses"]
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            summary_df = df.groupby("kategori")["total"].agg(["sum", "count"]).reset_index()
            summary_df.columns = ["Kategori", "Total", "Jumlah"]
            summary_df = summary_df.sort_values("Total", ascending=False)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            summary_sheet = writer.sheets["Summary"]
            chart = PieChart()
            chart.title = "Pengeluaran per Kategori"
            labels = Reference(summary_sheet, min_col=1, min_row=2, max_row=len(summary_df)+1)
            data = Reference(summary_sheet, min_col=2, min_row=1, max_row=len(summary_df)+1)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(labels)
            chart.height, chart.width = 10, 15
            summary_sheet.add_chart(chart, "E2")
    print(f"\n✅ Exported to: {output}\n   {len(df)} records exported")

def generate_chart(bulan=None, tahun=datetime.now().year, output_path=None):
    if not CHART_AVAILABLE:
        print("❌ Chart dependencies not installed")
        return
    init_db()
    conn = get_db_connection()
    if bulan:
        dari = f"{tahun}-{bulan:02d}-01"
        sampai = f"{tahun+1}-01-01" if bulan == 12 else f"{tahun}-{bulan+1:02d}-01"
        df = pd.read_sql_query("SELECT * FROM expenses WHERE tanggal >= ? AND tanggal < ? ORDER BY tanggal", conn, params=(dari, sampai))
        period_label = datetime(tahun, bulan, 1).strftime("%B %Y")
    else:
        dari, sampai = f"{tahun}-01-01", f"{tahun+1}-01-01"
        df = pd.read_sql_query("SELECT * FROM expenses WHERE tanggal >= ? AND tanggal < ? ORDER BY tanggal", conn, params=(dari, sampai))
        period_label = str(tahun)
    conn.close()
    if df.empty:
        print("\n📭 No data to chart")
        return
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Expense Report - {period_label}", fontsize=16, fontweight="bold")
    cat_data = df.groupby("kategori")["total"].sum().sort_values(ascending=False)
    colors = plt.cm.Set3(range(len(cat_data)))
    axes[0, 0].pie(cat_data.values, labels=cat_data.index, autopct="%1.1f%%", colors=colors)
    axes[0, 0].set_title("By Category")
    cat_data.plot(kind="bar", ax=axes[0, 1], color="skyblue")
    axes[0, 1].set_title("Total by Category")
    axes[0, 1].set_ylabel("Amount (Rp)")
    axes[0, 1].tick_params(axis="x", rotation=45)
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    daily = df.groupby("tanggal")["total"].sum()
    daily.plot(kind="line", ax=axes[1, 0], marker="o", color="green")
    axes[1, 0].set_title("Daily Spending")
    axes[1, 0].set_ylabel("Amount (Rp)")
    axes[1, 0].tick_params(axis="x", rotation=45)
    top_merchants = df.groupby("merchant")["total"].sum().nlargest(10)
    top_merchants.plot(kind="barh", ax=axes[1, 1], color="coral")
    axes[1, 1].set_title("Top 10 Merchants")
    axes[1, 1].set_xlabel("Amount (Rp)")
    plt.tight_layout()
    output = Path(output_path) if output_path else Path(os.path.expanduser(f"~/expense_chart_{tahun}_{bulan or 'full'}.png"))
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"\n✅ Chart saved to: {output}")
    total = df["total"].sum()
    avg_daily = df.groupby("tanggal")["total"].sum().mean()
    print(f"\n📊 Statistics:\n   Total: Rp {total:,.0f}\n   Transactions: {len(df)}\n   Avg daily: Rp {avg_daily:,.0f}")

def get_buttons_json():
    buttons = {
        "inline_keyboard": [
            [{"text": "📊 Daily Report", "callback_data": "/expense daily --telegram"}, {"text": "📈 Monthly", "callback_data": "/expense summary --bulan 2"}],
            [{"text": "📝 List Today", "callback_data": "/expense list --dari today --telegram"}, {"text": "📉 Chart", "callback_data": "/expense chart"}],
            [{"text": "💾 Export Excel", "callback_data": "/expense export"}]
        ]
    }
    print(json.dumps(buttons, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Expense Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add expense from image or manual")
    add_parser.add_argument("image_path", nargs="?", help="Path to receipt image")
    add_parser.add_argument("--manual", "-m", action="store_true", help="Manual input")
    add_parser.add_argument("--no-ocr", "-n", action="store_true", help="Skip OCR, use manual input even with image")
    add_parser.add_argument("--merchant", help="Merchant name (AI vision mode)")
    add_parser.add_argument("--total", type=float, help="Total amount (AI vision mode)")
    add_parser.add_argument("--date", help="Date YYYY-MM-DD (AI vision mode)")
    add_parser.add_argument("--kategori", "-k", help="Category (AI vision mode)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List expenses")
    list_parser.add_argument("--kategori", "-k", help="Filter by kategori")
    list_parser.add_argument("--dari", help="From date (YYYY-MM-DD)")
    list_parser.add_argument("--sampai", help="To date (YYYY-MM-DD)")
    list_parser.add_argument("--telegram", "-t", action="store_true", help="Telegram-friendly format")
    list_parser.add_argument("--no-compare", action="store_true", help="Disable yesterday comparison")
    
    # Summary command
    sum_parser = subparsers.add_parser("summary", help="Show summary")
    sum_parser.add_argument("--bulan", "-b", type=int, help="Month (1-12)")
    sum_parser.add_argument("--tahun", "-t", type=int, default=datetime.now().year, help="Year")
    
    # Export command
    exp_parser = subparsers.add_parser("export", help="Export to Excel/CSV")
    exp_parser.add_argument("--format", choices=["excel", "csv"], default="excel")
    exp_parser.add_argument("--output", "-o", help="Output file path")
    
    # Chart command
    chart_parser = subparsers.add_parser("chart", help="Generate charts")
    chart_parser.add_argument("--bulan", "-b", type=int, help="Month (1-12)")
    chart_parser.add_argument("--tahun", "-t", type=int, default=datetime.now().year)
    chart_parser.add_argument("--output", "-o", help="Output PNG path")
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit expense")
    edit_parser.add_argument("id", type=int, help="Expense ID")
    edit_parser.add_argument("--merchant", "-m", help="New merchant name")
    edit_parser.add_argument("--total", "-t", type=float, help="New total amount")
    edit_parser.add_argument("--date", "-d", help="New date (YYYY-MM-DD)")
    edit_parser.add_argument("--kategori", "-k", help="New category")
    
    # Delete command
    del_parser = subparsers.add_parser("delete", help="Delete expense")
    del_parser.add_argument("id", type=int, help="Expense ID")
    
    # Daily command
    daily_parser = subparsers.add_parser("daily", help="Daily report")
    daily_parser.add_argument("--tanggal", "-d", help="Date (YYYY-MM-DD), default: today")
    daily_parser.add_argument("--standard", "-s", action="store_true", help="Use standard table format instead of Telegram format")
    daily_parser.add_argument("--no-compare", action="store_true", help="Disable yesterday comparison")
    
    # Buttons command
    buttons_parser = subparsers.add_parser("buttons", help="Get button config for Telegram")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_expense(args.image_path, args.manual, args.merchant, args.total, args.date, args.kategori, args.no_ocr)
    elif args.command == "list":
        list_expenses(args.kategori, args.dari, args.sampai, args.telegram, not args.no_compare)
    elif args.command == "summary":
        summary(args.bulan, args.tahun)
    elif args.command == "export":
        export_to_excel(args.output, args.format)
    elif args.command == "chart":
        generate_chart(args.bulan, args.tahun, args.output)
    elif args.command == "edit":
        edit_expense(args.id, args.merchant, args.total, args.date, args.kategori)
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "daily":
        daily_report(args.tanggal, not args.standard, not args.no_compare)
    elif args.command == "buttons":
        get_buttons_json()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
