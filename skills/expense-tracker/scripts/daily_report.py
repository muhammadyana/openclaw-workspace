#!/usr/bin/env python3
"""
Daily Expense Report - Generate and send daily expense summary via Telegram
"""

import os
import sys

# Add virtual environment site-packages to path
VENV_PATH = os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages")
if os.path.exists(VENV_PATH) and VENV_PATH not in sys.path:
    sys.path.insert(0, VENV_PATH)

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(os.path.expanduser("~/.openclaw/workspace/expenses.db"))

def get_db_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_daily_summary(report_date=None):
    """Generate daily expense summary"""
    if report_date is None:
        report_date = date.today()
    
    conn = get_db_connection()
    
    # Get today's expenses
    rows = conn.execute(
        "SELECT * FROM expenses WHERE tanggal = ? ORDER BY created_at DESC",
        (report_date,)
    ).fetchall()
    
    if not rows:
        return None, f"📭 Tidak ada pengeluaran hari ini ({report_date.strftime('%d %b %Y')})"
    
    # Calculate totals
    total = sum(row['total'] for row in rows)
    
    # Group by category
    categories = {}
    for row in rows:
        cat = row['kategori']
        if cat not in categories:
            categories[cat] = {'total': 0, 'count': 0}
        categories[cat]['total'] += row['total']
        categories[cat]['count'] += 1
    
    # Get previous day for comparison
    prev_date = report_date - timedelta(days=1)
    prev_total = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM expenses WHERE tanggal = ?",
        (prev_date,)
    ).fetchone()[0]
    
    # Get this month total
    month_start = report_date.replace(day=1)
    month_total = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM expenses WHERE tanggal >= ? AND tanggal <= ?",
        (month_start, report_date)
    ).fetchone()[0]
    
    conn.close()
    
    # Format report
    day_name = report_date.strftime('%A').replace('Monday', 'Senin').replace('Tuesday', 'Selasa').replace('Wednesday', 'Rabu').replace('Thursday', 'Kamis').replace('Friday', 'Jumat').replace('Saturday', 'Sabtu').replace('Sunday', 'Minggu')
    
    report = f"""📊 **Daily Expense Report**
📅 {day_name}, {report_date.strftime('%d %B %Y')}

💰 **Total Hari Ini: Rp {total:,.0f}** ({len(rows)} transaksi)
"""
    
    # Add category breakdown
    report += "\n📂 **Per Kategori:**\n"
    for cat, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
        pct = (data['total'] / total * 100)
        report += f"  • {cat}: Rp {data['total']:,.0f} ({pct:.1f}%) [{data['count']}x]\n"
    
    # Add transactions
    report += "\n📝 **Detail Transaksi:**\n"
    for row in rows:
        report += f"  • {row['merchant'][:25]:<25} Rp {row['total']:>10,.0f}\n"
    
    # Add comparison
    report += f"\n📈 **Perbandingan:**\n"
    if prev_total > 0:
        diff = total - prev_total
        diff_pct = (diff / prev_total * 100)
        emoji = "📈" if diff > 0 else "📉"
        report += f"  {emoji} vs Kemarin: Rp {abs(diff):,.0f} ({abs(diff_pct):.1f}%)\n"
    
    report += f"  📊 Bulan Ini: Rp {month_total:,.0f}\n"
    
    # Add budget reminder (optional)
    avg_daily = month_total / report_date.day
    projected_month = avg_daily * 30
    report += f"  🔮 Proyeksi Bulan: Rp {projected_month:,.0f}\n"
    
    return rows, report

def send_telegram_message(message):
    """Send message via Telegram using openclaw"""
    import subprocess
    
    # Use openclaw message command
    cmd = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", "210669138",
        "--message", message
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    """Main function"""
    # Check if database exists
    if not DB_PATH.exists():
        print("❌ Database not found")
        sys.exit(1)
    
    # Generate report
    rows, report = get_daily_summary()
    
    # Print to console (for cron logging)
    print(report)
    
    # Send via Telegram
    if send_telegram_message(report):
        print("\n✅ Report sent to Telegram")
    else:
        print("\n❌ Failed to send to Telegram")
        sys.exit(1)

if __name__ == '__main__':
    main()
