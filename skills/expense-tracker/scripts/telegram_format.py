#!/usr/bin/env python3
"""
Telegram Formatter for Expense Tracker
Mobile-friendly output format
"""

def format_daily_report(rows, cat_summary, total_all, date_str, comparison=None):
    """Format daily report for Telegram (mobile-friendly)
    
    Args:
        comparison: dict with 'yesterday_total', 'yesterday_count', 'diff', 'diff_pct'
    """
    emoji_map = {
        "Makanan": "🍽️", "Transport": "🚗", "Belanja": "🛒",
        "Hiburan": "🎬", "Kesehatan": "💊", "Utilitas": "⚡", "Lainnya": "📦"
    }
    
    lines = []
    lines.append(f"📅 Daily Report - {date_str}")
    lines.append("")
    lines.append(f"💰 Total: Rp {total_all:,.0f} ({len(rows)} transaksi)")
    
    # Add comparison with yesterday
    if comparison:
        diff = comparison['diff']
        diff_pct = comparison['diff_pct']
        yesterday_total = comparison['yesterday_total']
        yesterday_count = comparison['yesterday_count']
        
        if diff > 0:
            emoji_diff = "📈"
            diff_text = f"+Rp {diff:,.0f} (+{diff_pct:.1f}%)"
        elif diff < 0:
            emoji_diff = "📉"
            diff_text = f"-Rp {abs(diff):,.0f} ({diff_pct:.1f}%)"
        else:
            emoji_diff = "➡️"
            diff_text = "Sama dengan kemarin"
        
        lines.append(f"{emoji_diff} vs Kemarin: {diff_text}")
        lines.append(f"   (Kemarin: Rp {yesterday_total:,.0f}, {yesterday_count} transaksi)")
    
    lines.append("")
    
    # Category breakdown
    lines.append("📂 Per Kategori:")
    for row in cat_summary:
        emoji = emoji_map.get(row['kategori'], "📦")
        lines.append(f"{emoji} {row['kategori']}: Rp {row['total']:,.0f} ({row['count']}x)")
    
    # Transaction list
    lines.append("")
    lines.append("📝 Detail Transaksi:")
    for row in rows:
        emoji = emoji_map.get(row['kategori'], "📦")
        lines.append(f"#{row['id']} {emoji} {row['merchant'][:25]}")
        lines.append(f"└ Rp {row['total']:,.0f}")
    
    return "\n".join(lines)

def format_list(rows, total_all, comparison=None):
    """Format list for Telegram (mobile-friendly)
    
    Args:
        comparison: dict with 'yesterday_total', 'yesterday_count', 'diff', 'diff_pct'
    """
    emoji_map = {
        "Makanan": "🍽️", "Transport": "🚗", "Belanja": "🛒",
        "Hiburan": "🎬", "Kesehatan": "💊", "Utilitas": "⚡", "Lainnya": "📦"
    }
    
    lines = []
    lines.append(f"📋 Expenses ({len(rows)} items)")
    
    # Add comparison with yesterday
    if comparison:
        diff = comparison['diff']
        diff_pct = comparison['diff_pct']
        yesterday_total = comparison['yesterday_total']
        yesterday_count = comparison['yesterday_count']
        
        if diff > 0:
            emoji_diff = "📈"
            diff_text = f"+Rp {diff:,.0f} (+{diff_pct:.1f}%)"
        elif diff < 0:
            emoji_diff = "📉"
            diff_text = f"-Rp {abs(diff):,.0f} ({diff_pct:.1f}%)"
        else:
            emoji_diff = "➡️"
            diff_text = "Sama dengan kemarin"
        
        lines.append(f"{emoji_diff} vs Kemarin: {diff_text}")
        lines.append(f"   (Kemarin: Rp {yesterday_total:,.0f}, {yesterday_count} transaksi)")
    
    lines.append("")
    
    for row in rows:
        emoji = emoji_map.get(row['kategori'], "📦")
        lines.append(f"#{row['id']} {emoji} {row['merchant'][:25]}")
        lines.append(f"   ├ {row['kategori']} • {row['tanggal']}")
        lines.append(f"   └ Rp {row['total']:,.0f}")
        lines.append("")
    
    lines.append(f"💰 Total: Rp {total_all:,.0f}")
    return "\n".join(lines)

if __name__ == "__main__":
    # Test
    print("Telegram formatters loaded")
