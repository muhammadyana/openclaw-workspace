#!/usr/bin/env python3
"""
Expense Tracker - Sistem pencatatan keuangan otomatis
Supports: OCR from receipt photos, auto-categorization, SQLite + Excel
"""

import os
import sys

# Add virtual environment site-packages to path
VENV_PATH = os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages")
if os.path.exists(VENV_PATH) and VENV_PATH not in sys.path:
    sys.path.insert(0, VENV_PATH)
import re
import json
import sqlite3
import argparse
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import unicodedata

# Try to import optional dependencies
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
    import seaborn as sns
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

# Database path
DB_PATH = Path(os.path.expanduser("~/.openclaw/workspace/expenses.db"))
DEFAULT_EXCEL_PATH = Path(os.path.expanduser("~/expenses.xlsx"))

# Kategori dan keywords
KATEGORI_KEYWORDS = {
    "Makanan": ["restoran", "cafe", "food", "makan", "minum", "warung", "bakso", "sate", "nasi", "kopi", "coffee", "starbucks", "mcd", "kfc", "burger", "pizza"],
    "Transport": ["bbm", "gojek", "grab", "parkir", "toll", "bensin", "pertamina", "shell", "transport", "ojek", "taksi", "bus", "kereta", "go-car"],
    "Belanja": ["indomaret", "alfamart", "supermarket", "mall", "toko", "shop", "minimarket", "7-eleven", "circle k", "fresh", "grocery"],
    "Hiburan": ["bioskop", "cinema", "game", "spotify", "netflix", "youtube", "disney", "steam", "playstation", "xbox", "hiburan"],
    "Kesehatan": ["apotek", "klinik", "rumah sakit", "hospital", "obat", "pharmacy", "dokter", "medical", "kesehatan"],
    "Utilitas": ["pln", "pdam", "internet", "pulsa", "listrik", "air", "wifi", "telepon", "token", "billing"],
}

def get_db_connection() -> sqlite3.Connection:
    """Get SQLite connection with row factory"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE,
            merchant TEXT,
            total REAL,
            kategori TEXT,
            items TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tanggal ON expenses(tanggal)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kategori ON expenses(kategori)")
    conn.commit()
    conn.close()

def detect_kategori(merchant: str, items: str = "") -> str:
    """Detect kategori based on merchant name and items"""
    text = f"{merchant} {items}".lower()
    
    for kategori, keywords in KATEGORI_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return kategori
    
    return "Lainnya"

def extract_total(text: str) -> Optional[float]:
    """Extract total amount from OCR text"""
    # Common patterns for Indonesian receipts
    patterns = [
        r"(?:total|grand total|jumlah|total bayar|total harga)[\s:]*(?:rp[.\s]*)?([\d.,]+)",
        r"(?:rp[.\s]*)([\d.,]+)\s*$",
        r"total\s+([\d.,]+)",
        r"([\d.,]+)\s*total",
    ]
    
    def parse_number(num_str: str) -> Optional[float]:
        """Parse number handling both formats: 612,000.00 and 612.000,00"""
        num_str = num_str.strip()
        
        # Detect format: if last separator is comma -> ID format (612.000,00)
        # if last separator is dot -> US format (612,000.00)
        last_comma = num_str.rfind(',')
        last_dot = num_str.rfind('.')
        
        if last_comma > last_dot:
            # ID format: 612.000,00 or 612000,00
            num_str = num_str.replace('.', '').replace(',', '.')
        else:
            # US format: 612,000.00 or 612000.00
            num_str = num_str.replace(',', '')
        
        try:
            return float(num_str)
        except ValueError:
            return None
    
    for pattern in patterns:
        matches = re.findall(pattern, text.lower().replace("\n", " "))
        for match in matches:
            result = parse_number(match)
            if result and result >= 1000:  # Reasonable minimum
                return result
    
    # Fallback: find all numbers that look like prices
    numbers = re.findall(r"[\d.,]+", text)
    valid_numbers = []
    for num in numbers:
        result = parse_number(num)
        if result and 1000 <= result <= 100000000:
            valid_numbers.append(result)
    
    return max(valid_numbers) if valid_numbers else None

def extract_merchant(text: str) -> str:
    """Extract merchant name from OCR text"""
    text_clean = text.strip()
    lines = [l.strip() for l in text_clean.split("\n") if l.strip()]
    
    # Special handling for BCA transfer receipts
    if "bca" in text.lower() or "transfer successful" in text.lower():
        # Look for Product Name (exact match)
        for i, line in enumerate(lines):
            if line.lower() == "product name":
                # Product name is the next non-empty line
                if i + 1 < len(lines):
                    product = lines[i + 1].strip()
                    # Validate it's not a field label
                    if product and not any(skip in product.lower() for skip in ["source", "bill", "total"]):
                        return product
        # Fallback: look for patterns like "Product Name XXXX"
        for line in lines:
            if "product name" in line.lower():
                parts = line.split("Product Name")
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip()
    
    # Standard merchant extraction
    for line in lines[:10]:
        line_lower = line.lower()
        # Skip common headers and non-merchant lines
        skip_words = ["terima kasih", "thank you", "struk", "receipt", "invoice", 
                      "telp", "phone", "no.", "date", "tanggal", "transfer successful",
                      "bca", "payment", "transaction", "virtual account", "source of fund",
                      "name", "billdesc", "bill total", "total payment"]
        if any(skip in line_lower for skip in skip_words):
            continue
        if len(line) > 3 and not line.replace(" ", "").isdigit():
            return line.strip()
    
    return "Unknown"

def extract_date(text: str) -> date:
    """Extract date from OCR text"""
    # Try various date formats
    patterns = [
        r"(\d{2})[/\-\s](\d{2})[/\-\s](\d{4})",  # DD/MM/YYYY
        r"(\d{4})[/\-\s](\d{2})[/\-\s](\d{2})",  # YYYY/MM/DD
        r"(\d{2})[/\-\s](\d{2})[/\-\s](\d{2})",   # DD/MM/YY
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                if len(match[2]) == 4:
                    return date(int(match[2]), int(match[1]), int(match[0]))
                else:
                    year = int(match[2]) + 2000 if int(match[2]) < 50 else int(match[2]) + 1900
                    return date(year, int(match[1]), int(match[0]))
            except:
                continue
    
    return date.today()

def ocr_image(image_path: str) -> str:
    """Perform OCR on image"""
    if not OCR_AVAILABLE:
        raise ImportError("OCR not available. Install: pip install pytesseract pillow")
    
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='ind+eng')
    return text

def add_expense(image_path: Optional[str] = None, manual: bool = False):
    """Add new expense"""
    init_db()
    
    if manual or not image_path:
        print("\\n📋 Input Manual Expense")
        print("-" * 40)
        merchant = input("Merchant: ").strip()
        total_input = input("Total (Rp): ").strip().replace(".", "").replace(",", "")
        total = float(total_input) if total_input else 0
        tanggal_input = input("Tanggal (YYYY-MM-DD, kosong=hari ini): ").strip()
        tanggal = date.fromisoformat(tanggal_input) if tanggal_input else date.today()
        items = input("Items (optional): ").strip()
        kategori = input(f"Kategori (default: {detect_kategori(merchant, items)}): ").strip()
        if not kategori:
            kategori = detect_kategori(merchant, items)
    else:
        print(f"\\n📸 Processing image: {image_path}")
        print("🔍 Running OCR...")
        
        text = ocr_image(image_path)
        print("\\n--- OCR Result ---")
        print(text[:500] + "..." if len(text) > 500 else text)
        print("---\\n")
        
        merchant = extract_merchant(text)
        total = extract_total(text) or 0
        tanggal = extract_date(text)
        items = text[:500]  # Store first 500 chars as items
        kategori = detect_kategori(merchant, text)
        
        print(f"\\n📊 Detected:")
        print(f"   Merchant: {merchant}")
        print(f"   Total: Rp {total:,.0f}")
        print(f"   Tanggal: {tanggal}")
        print(f"   Kategori: {kategori}")
        
        confirm = input("\\n✅ Save? [Y/n/e=edit]: ").strip().lower()
        if confirm == 'e':
            merchant = input(f"Merchant [{merchant}]: ").strip() or merchant
            total_input = input(f"Total [{total}]: ").strip()
            total = float(total_input) if total_input else total
            kategori = input(f"Kategori [{kategori}]: ").strip() or kategori
        elif confirm == 'n':
            print("❌ Cancelled")
            return
    
    # Save to database
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO expenses (tanggal, merchant, total, kategori, items, file_path) VALUES (?, ?, ?, ?, ?, ?)",
        (tanggal, merchant, total, kategori, items, image_path)
    )
    conn.commit()
    expense_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    
    print(f"\\n✅ Expense saved! ID: {expense_id}")
    print(f"   Rp {total:,.0f} - {merchant} ({kategori})")

def list_expenses(kategori: Optional[str] = None, dari: Optional[str] = None, sampai: Optional[str] = None):
    """List expenses with filters"""
    init_db()
    
    conn = get_db_connection()
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    
    if kategori:
        query += " AND kategori = ?"
        params.append(kategori)
    if dari:
        query += " AND tanggal >= ?"
        params.append(dari)
    if sampai:
        query += " AND tanggal <= ?"
        params.append(sampai)
    
    query += " ORDER BY tanggal DESC, created_at DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    if not rows:
        print("\\n📭 No expenses found")
        return
    
    print(f"\\n📊 Expenses ({len(rows)} items)")
    print("-" * 80)
    print(f"{'ID':<5} {'Tanggal':<12} {'Kategori':<12} {'Merchant':<20} {'Total':>15}")
    print("-" * 80)
    
    total_all = 0
    for row in rows:
        total_all += row['total']
        print(f"{row['id']:<5} {row['tanggal']:<12} {row['kategori']:<12} {row['merchant'][:20]:<20} Rp {row['total']:>12,.0f}")
    
    print("-" * 80)
    print(f"{'Total':>52} Rp {total_all:>12,.0f}")

def summary(bulan: Optional[int] = None, tahun: int = datetime.now().year):
    """Show summary statistics"""
    init_db()
    conn = get_db_connection()
    
    # Build date filter
    if bulan:
        dari = f"{tahun}-{bulan:02d}-01"
        if bulan == 12:
            sampai = f"{tahun+1}-01-01"
        else:
            sampai = f"{tahun}-{bulan+1:02d}-01"
        where_clause = f"WHERE tanggal >= '{dari}' AND tanggal < '{sampai}'"
        period_label = f"{datetime(tahun, bulan, 1).strftime('%B %Y')}"
    else:
        dari = f"{tahun}-01-01"
        sampai = f"{tahun+1}-01-01"
        where_clause = f"WHERE tanggal >= '{dari}' AND tanggal < '{sampai}'"
        period_label = f"Tahun {tahun}"
    
    print(f"\\n📈 Ringkasan Pengeluaran - {period_label}")
    print("=" * 50)
    
    # Total expenses
    total = conn.execute(f"SELECT COALESCE(SUM(total), 0) FROM expenses {where_clause}").fetchone()[0]
    count = conn.execute(f"SELECT COUNT(*) FROM expenses {where_clause}").fetchone()[0]
    
    print(f"\\n📊 Total: Rp {total:,.0f} ({count} transaksi)")
    
    # By category
    print(f"\\n📂 Per Kategori:")
    print("-" * 35)
    cat_rows = conn.execute(f"""
        SELECT kategori, COUNT(*) as count, SUM(total) as total 
        FROM expenses {where_clause} 
        GROUP BY kategori 
        ORDER BY total DESC
    """).fetchall()
    
    for row in cat_rows:
        pct = (row['total'] / total * 100) if total > 0 else 0
        print(f"   {row['kategori']:<15} Rp {row['total']:>10,.0f} ({pct:5.1f}%) [{row['count']}x]")
    
    # Top merchants
    print(f"\\n🏪 Top Merchants:")
    print("-" * 35)
    merch_rows = conn.execute(f"""
        SELECT merchant, SUM(total) as total, COUNT(*) as count
        FROM expenses {where_clause}
        GROUP BY merchant
        ORDER BY total DESC
        LIMIT 5
    """).fetchall()
    
    for row in merch_rows:
        print(f"   {row['merchant'][:20]:<20} Rp {row['total']:>10,.0f} [{row['count']}x]")
    
    conn.close()

def export_to_excel(output_path: Optional[str] = None, format_type: str = "excel"):
    """Export expenses to Excel or CSV"""
    if format_type == "excel" and not EXCEL_AVAILABLE:
        print("❌ openpyxl not installed. Run: pip install openpyxl")
        return
    
    init_db()
    conn = get_db_connection()
    
    # Read all data
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY tanggal DESC", conn)
    conn.close()
    
    output = Path(output_path) if output_path else DEFAULT_EXCEL_PATH
    
    if format_type == "csv":
        output = output.with_suffix('.csv')
        df.to_csv(output, index=False)
    else:
        output = output.with_suffix('.xlsx')
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Expenses']
            
            # Format headers
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")
            
            # Auto-adjust column widths
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
            
            # Create summary sheet
            summary_df = df.groupby('kategori')['total'].agg(['sum', 'count']).reset_index()
            summary_df.columns = ['Kategori', 'Total', 'Jumlah']
            summary_df = summary_df.sort_values('Total', ascending=False)
            
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Add chart
            summary_sheet = writer.sheets['Summary']
            chart = PieChart()
            chart.title = "Pengeluaran per Kategori"
            
            labels = Reference(summary_sheet, min_col=1, min_row=2, max_row=len(summary_df)+1)
            data = Reference(summary_sheet, min_col=2, min_row=1, max_row=len(summary_df)+1)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(labels)
            chart.height = 10
            chart.width = 15
            
            summary_sheet.add_chart(chart, "E2")
    
    print(f"\\n✅ Exported to: {output}")
    print(f"   {len(df)} records exported")

def generate_chart(bulan: Optional[int] = None, tahun: int = datetime.now().year, output_path: Optional[str] = None):
    """Generate expense charts"""
    if not CHART_AVAILABLE:
        print("❌ Chart dependencies not installed. Run: pip install pandas matplotlib seaborn")
        return
    
    init_db()
    conn = get_db_connection()
    
    # Get data
    if bulan:
        dari = f"{tahun}-{bulan:02d}-01"
        if bulan == 12:
            sampai = f"{tahun+1}-01-01"
        else:
            sampai = f"{tahun}-{bulan+1:02d}-01"
        df = pd.read_sql_query(
            "SELECT * FROM expenses WHERE tanggal >= ? AND tanggal < ? ORDER BY tanggal",
            conn, params=(dari, sampai)
        )
        period_label = datetime(tahun, bulan, 1).strftime('%B %Y')
    else:
        dari = f"{tahun}-01-01"
        sampai = f"{tahun+1}-01-01"
        df = pd.read_sql_query(
            "SELECT * FROM expenses WHERE tanggal >= ? AND tanggal < ? ORDER BY tanggal",
            conn, params=(dari, sampai)
        )
        period_label = str(tahun)
    
    conn.close()
    
    if df.empty:
        print("\\n📭 No data to chart")
        return
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Expense Report - {period_label}', fontsize=16, fontweight='bold')
    
    # 1. Pie chart by category
    cat_data = df.groupby('kategori')['total'].sum().sort_values(ascending=False)
    colors = plt.cm.Set3(range(len(cat_data)))
    axes[0, 0].pie(cat_data.values, labels=cat_data.index, autopct='%1.1f%%', colors=colors)
    axes[0, 0].set_title('By Category')
    
    # 2. Bar chart by category
    cat_data.plot(kind='bar', ax=axes[0, 1], color='skyblue')
    axes[0, 1].set_title('Total by Category')
    axes[0, 1].set_ylabel('Amount (Rp)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. Timeline
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    daily = df.groupby('tanggal')['total'].sum()
    daily.plot(kind='line', ax=axes[1, 0], marker='o', color='green')
    axes[1, 0].set_title('Daily Spending')
    axes[1, 0].set_ylabel('Amount (Rp)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Top merchants
    top_merchants = df.groupby('merchant')['total'].sum().nlargest(10)
    top_merchants.plot(kind='barh', ax=axes[1, 1], color='coral')
    axes[1, 1].set_title('Top 10 Merchants')
    axes[1, 1].set_xlabel('Amount (Rp)')
    
    plt.tight_layout()
    
    # Save
    if output_path:
        output = Path(output_path)
    else:
        output = Path(os.path.expanduser(f"~/expense_chart_{tahun}_{bulan or 'full'}.png"))
    
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"\\n✅ Chart saved to: {output}")
    
    # Also show stats
    total = df['total'].sum()
    avg_daily = df.groupby('tanggal')['total'].sum().mean()
    print(f"\\n📊 Statistics:")
    print(f"   Total: Rp {total:,.0f}")
    print(f"   Transactions: {len(df)}")
    print(f"   Avg daily: Rp {avg_daily:,.0f}")

def delete_expense(expense_id: int):
    """Delete an expense by ID"""
    init_db()
    conn = get_db_connection()
    
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if not row:
        print(f"❌ Expense {expense_id} not found")
        return
    
    print(f"\\n🗑️  Will delete:")
    print(f"   ID: {row['id']}")
    print(f"   {row['tanggal']} - {row['merchant']}")
    print(f"   Rp {row['total']:,.0f} ({row['kategori']})")
    
    confirm = input("\\nConfirm delete? [y/N]: ").strip().lower()
    if confirm == 'y':
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        print("✅ Deleted")
    else:
        print("❌ Cancelled")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Expense Tracker')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add expense from image or manual')
    add_parser.add_argument('image_path', nargs='?', help='Path to receipt image')
    add_parser.add_argument('--manual', '-m', action='store_true', help='Manual input')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List expenses')
    list_parser.add_argument('--kategori', '-k', help='Filter by kategori')
    list_parser.add_argument('--dari', help='From date (YYYY-MM-DD)')
    list_parser.add_argument('--sampai', help='To date (YYYY-MM-DD)')
    
    # Summary command
    sum_parser = subparsers.add_parser('summary', help='Show summary')
    sum_parser.add_argument('--bulan', '-b', type=int, help='Month (1-12)')
    sum_parser.add_argument('--tahun', '-t', type=int, default=datetime.now().year, help='Year')
    
    # Export command
    exp_parser = subparsers.add_parser('export', help='Export to Excel/CSV')
    exp_parser.add_argument('--format', choices=['excel', 'csv'], default='excel')
    exp_parser.add_argument('--output', '-o', help='Output file path')
    
    # Chart command
    chart_parser = subparsers.add_parser('chart', help='Generate charts')
    chart_parser.add_argument('--bulan', '-b', type=int, help='Month (1-12)')
    chart_parser.add_argument('--tahun', '-t', type=int, default=datetime.now().year)
    chart_parser.add_argument('--output', '-o', help='Output PNG path')
    
    # Delete command
    del_parser = subparsers.add_parser('delete', help='Delete expense')
    del_parser.add_argument('id', type=int, help='Expense ID')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_expense(args.image_path, args.manual)
    elif args.command == 'list':
        list_expenses(args.kategori, args.dari, args.sampai)
    elif args.command == 'summary':
        summary(args.bulan, args.tahun)
    elif args.command == 'export':
        export_to_excel(args.output, args.format)
    elif args.command == 'chart':
        generate_chart(args.bulan, args.tahun, args.output)
    elif args.command == 'delete':
        delete_expense(args.id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
