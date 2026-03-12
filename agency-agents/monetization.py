#!/usr/bin/env python3
"""
Skill Monetization Tracker
Track revenue, users, and growth for your OpenClaw skills
"""

import json
import os
from datetime import datetime, timedelta

DATA_FILE = os.path.expanduser("~/.openclaw/workspace/agency-agents/monetization_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "skills": {},
        "total_revenue": 0,
        "total_users": 0,
        "start_date": datetime.now().isoformat()
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_skill(name, price_monthly, price_lifetime=None):
    data = load_data()
    data["skills"][name] = {
        "name": name,
        "price_monthly": price_monthly,
        "price_lifetime": price_lifetime,
        "subscribers": 0,
        "lifetime_sales": 0,
        "revenue": 0,
        "created_at": datetime.now().isoformat()
    }
    save_data(data)
    print(f"✅ Added skill: {name} (${price_monthly}/month)")

def record_sale(skill_name, sale_type="monthly", amount=None):
    data = load_data()
    
    if skill_name not in data["skills"]:
        print(f"❌ Skill '{skill_name}' not found")
        return
    
    skill = data["skills"][skill_name]
    
    if amount is None:
        amount = skill["price_lifetime"] if sale_type == "lifetime" else skill["price_monthly"]
    
    skill["revenue"] += amount
    data["total_revenue"] += amount
    
    if sale_type == "monthly":
        skill["subscribers"] += 1
        data["total_users"] += 1
    else:
        skill["lifetime_sales"] += 1
    
    save_data(data)
    print(f"💰 Recorded {sale_type} sale for {skill_name}: ${amount}")

def show_dashboard():
    data = load_data()
    
    print("\n" + "=" * 60)
    print("💰 SKILL MONETIZATION DASHBOARD")
    print("=" * 60)
    
    print(f"\n📊 Overall Stats:")
    print(f"  Total Revenue: ${data['total_revenue']:,.2f}")
    print(f"  Total Users: {data['total_users']}")
    print(f"  Active Skills: {len(data['skills'])}")
    
    if data['total_users'] > 0:
        avg_revenue = data['total_revenue'] / data['total_users']
        print(f"  Avg Revenue/User: ${avg_revenue:.2f}")
    
    print(f"\n🎨 Skills Performance:")
    print("-" * 60)
    print(f"{'Skill':<25} {'Subs':<8} {'Revenue':<12} {'Status'}")
    print("-" * 60)
    
    for name, skill in data["skills"].items():
        status = "🟢" if skill["revenue"] > 0 else "🟡"
        print(f"{name:<25} {skill['subscribers']:<8} ${skill['revenue']:<11,.2f} {status}")
    
    print("-" * 60)
    
    # Projections
    if data["skills"]:
        monthly_recurring = sum(
            s["subscribers"] * s["price_monthly"] 
            for s in data["skills"].values()
        )
        print(f"\n📈 Monthly Recurring Revenue (MRR): ${monthly_recurring:,.2f}")
        print(f"📈 Projected Annual Revenue: ${monthly_recurring * 12:,.2f}")
    
    print("\n" + "=" * 60)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: monetization.py <command> [options]")
        print("\nCommands:")
        print("  dashboard                    Show revenue dashboard")
        print("  add <name> <monthly_price>  Add new skill")
        print("  sale <name> [monthly|lifetime]  Record a sale")
        print("\nExamples:")
        print("  monetization.py add 'expense-tracker' 9.99")
        print("  monetization.py sale 'expense-tracker' monthly")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "dashboard":
        show_dashboard()
    elif command == "add" and len(sys.argv) >= 4:
        add_skill(sys.argv[2], float(sys.argv[3]))
    elif command == "sale" and len(sys.argv) >= 3:
        sale_type = sys.argv[3] if len(sys.argv) > 3 else "monthly"
        record_sale(sys.argv[2], sale_type)
    else:
        print("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()
