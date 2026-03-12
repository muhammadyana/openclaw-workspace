#!/usr/bin/env python3
"""
Ramadan Tracker - Prayer times and reminders for Ramadan
Location: Bandung (Jl. Tubagus Ismail VII No.11 ASekeloa)
"""

import json
import requests
from datetime import datetime, timedelta
import sys
import os

# Default location (Bandung - Jl. Tubagus Ismail VII)
DEFAULT_LOCATION = {
    "city": "Bandung",
    "country": "Indonesia",
    "latitude": -6.8735,
    "longitude": 107.6190,
    "timezone": "Asia/Jakarta"
}

# API for prayer times - Using Al-Adhan API with Kemenag method
PRAYER_API_URL = "https://api.aladhan.com/v1/timingsByCity"

def get_prayer_times(date=None, lat=None, lon=None):
    """Fetch prayer times from Al-Adhan API using city-based lookup (Kemenag Indonesia)"""
    if date is None:
        date = datetime.now()
    
    # Use timingsByCity for better accuracy with Kemenag method
    url = f"{PRAYER_API_URL}"
    
    params = {
        "city": "Bandung",
        "country": "Indonesia",
        "method": 11,  # Kemenag Indonesia
        "tune": "3,3,3,0,0,7,7,0,0",  # Adjust to match Kemenag Bandung (+3 imsak/fajr, +7 maghrib)
        "date": date.strftime("%d-%m-%Y")
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("code") == 200:
            timings = data["data"]["timings"]
            # Al-Adhan uses "Fajr" but Kemenag uses Imsak/Subuh distinction
            # The API returns Imsak separately with method 11
            return {
                "Imsak": timings.get("Imsak", timings["Fajr"]),
                "Fajr": timings["Fajr"],
                "Sunrise": timings["Sunrise"],
                "Dhuhr": timings["Dhuhr"],
                "Asr": timings["Asr"],
                "Maghrib": timings["Maghrib"],
                "Isha": timings["Isha"]
            }
        return None
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        return None

def calculate_reminder_times(timings):
    """Calculate all reminder times based on prayer times"""
    reminders = {}
    
    # Parse times - now Imsak comes directly from API (Kemenag official)
    imsak = datetime.strptime(timings["Imsak"], "%H:%M")
    maghrib = datetime.strptime(timings["Maghrib"], "%H:%M")
    
    # 1. Reminder 5 min before buka (Maghrib)
    reminders["buka_5min"] = (maghrib - timedelta(minutes=5)).strftime("%H:%M")
    
    # 2. Ucapan buka puasa (Maghrib time)
    reminders["buka_time"] = maghrib.strftime("%H:%M")
    
    # 3. Sahur reminder 1 hour before imsak
    reminders["sahur_1h"] = (imsak - timedelta(hours=1)).strftime("%H:%M")
    
    # 4. Sahur reminder 30 min before imsak
    reminders["sahur_30min"] = (imsak - timedelta(minutes=30)).strftime("%H:%M")
    
    # 5. Reminder 5 min before imsak
    reminders["imsak_5min"] = (imsak - timedelta(minutes=5)).strftime("%H:%M")
    
    # 6. Imsak time
    reminders["imsak_time"] = imsak.strftime("%H:%M")
    
    # Store actual times for reference
    reminders["fajr"] = timings["Fajr"]
    reminders["maghrib"] = timings["Maghrib"]
    reminders["imsak"] = imsak.strftime("%H:%M")
    reminders["dzuhur"] = timings["Dhuhr"]
    reminders["ashar"] = timings["Asr"]
    reminders["isya"] = timings["Isha"]
    reminders["terbit"] = timings.get("Sunrise", "")
    
    return reminders

def get_iftar_menus():
    """Healthy iftar menu recommendations"""
    menus = [
        {
            "name": "Menu Buka Puasa Sehat #1",
            "items": ["Air putih + kurma (3 biji)", "Sop ayam dengan sayuran", "Nasi merah (1/2 porsi)", "Buah segar (semangka/pir)"]
        },
        {
            "name": "Menu Buka Puasa Sehat #2", 
            "items": ["Kurma + air kelapa", "Ikan bakar", "Sayur lodeh (sedikit santan)", "Kolak pisang (sedikit gula)"]
        },
        {
            "name": "Menu Buka Puasa Sehat #3",
            "items": ["Air putih hangat + kurma", "Ayam panggang", "Gado-gado", "Buah alpukat"]
        },
        {
            "name": "Menu Buka Puasa Sehat #4",
            "items": ["Susu + kurma", "Soto ayam (sedikit minyak)", "Tahu tempe", "Es buah (sedikit gula)"]
        }
    ]
    
    # Rotate menu based on day
    day = datetime.now().day
    return menus[day % len(menus)]

def format_schedule_output(reminders, telegram_format=False):
    """Format schedule for display"""
    menu = get_iftar_menus()
    
    if telegram_format:
        # Mobile-friendly format for Telegram
        output = f"📅 *{datetime.now().strftime('%A, %d %B %Y')}*\n"
        output += f"📍 {DEFAULT_LOCATION['city']}, {DEFAULT_LOCATION['country']}\n\n"
        
        output += "🌅 *Waktu Sholat:*\n"
        output += f"• Imsak: `{reminders['imsak']}`\n"
        output += f"• Subuh: `{reminders['fajr']}`\n"
        output += f"• Dzuhur: `{reminders['dzuhur']}`\n"
        output += f"• Ashar: `{reminders['ashar']}`\n"
        output += f"• Maghrib: `{reminders['maghrib']}`\n"
        output += f"• Isya: `{reminders['isya']}`\n\n"
        
        output += "⏰ *Jadwal Reminder:*\n"
        output += f"• Sahur 1 jam: `{reminders['sahur_1h']}`\n"
        output += f"• Sahur 30 menit: `{reminders['sahur_30min']}`\n"
        output += f"• 5 menit sebelum imsak: `{reminders['imsak_5min']}`\n"
        output += f"• 5 menit sebelum buka: `{reminders['buka_5min']}`\n\n"
        
        output += f"🍽️ *{menu['name']}:*\n"
        for item in menu['items']:
            output += f"• {item}\n"
        
        output += "\n✨ Semoga puasa lancar!"
        return output
    else:
        # Standard format
        output = f"""
📅 **Jadwal Ramadan Hari Ini** ({datetime.now().strftime('%d %B %Y')})
📍 Lokasi: {DEFAULT_LOCATION['city']}, {DEFAULT_LOCATION['country']}

🌅 **Waktu Sholat:**
• Imsak: {reminders['imsak']}
• Subuh: {reminders['fajr']}
• Dzuhur: {reminders['dzuhur']}
• Ashar: {reminders['ashar']}
• Maghrib (Buka): {reminders['maghrib']}
• Isya: {reminders['isya']}

⏰ **Jadwal Reminder:**
• Sahur (1 jam sebelum imsak): {reminders['sahur_1h']}
• Sahur (30 menit sebelum imsak): {reminders['sahur_30min']}
• 5 menit sebelum imsak: {reminders['imsak_5min']}
• 5 menit sebelum buka: {reminders['buka_5min']}

🍽️ **{menu['name']}:**
"""
        for item in menu['items']:
            output += f"• {item}\n"
        
        output += "\n✨ Semoga puasa lancar!"
        return output

def handle_callback(callback_data):
    """Handle Telegram button callbacks"""
    if callback_data == "ramadan_today":
        timings = get_prayer_times()
        if timings:
            reminders = calculate_reminder_times(timings)
            return format_schedule_output(reminders, telegram_format=True)
        return "Failed to fetch prayer times"
    
    elif callback_data == "ramadan_menu":
        menu = get_iftar_menus()
        output = f"🍽️ *{menu['name']}:*\n\n"
        for item in menu['items']:
            output += f"• {item}\n"
        return output
    
    elif callback_data == "ramadan_location":
        return f"""📍 *Lokasi:*
{DEFAULT_LOCATION['city']}, {DEFAULT_LOCATION['country']}
Koordinat: {DEFAULT_LOCATION['latitude']}, {DEFAULT_LOCATION['longitude']}

Alamat lengkap:
Jl. Tubagus Ismail VII No.11 ASekeloa, Coblong, Bandung"""
    
    return None

def get_buttons_json():
    """Generate button configuration for Telegram bot integration"""
    buttons = {
        "inline_keyboard": [
            [
                {"text": "📅 Jadwal Hari Ini", "callback_data": "ramadan_today"},
                {"text": "🍽️ Menu Buka", "callback_data": "ramadan_menu"}
            ],
            [
                {"text": "📍 Lokasi", "callback_data": "ramadan_location"}
            ]
        ]
    }
    print(json.dumps(buttons, indent=2))

def create_cron_jobs():
    """Create cron jobs for all reminders"""
    timings = get_prayer_times()
    if not timings:
        print("Failed to fetch prayer times")
        return
    
    reminders = calculate_reminder_times(timings)
    
    # Get tomorrow's date for cron scheduling
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    cron_jobs = []
    
    # 1. Sahur 1 hour before imsak
    sahur_1h = reminders['sahur_1h'].split(':')
    cron_jobs.append({
        "name": "Ramadan Sahur 1h",
        "schedule": f"{sahur_1h[1]} {sahur_1h[0]} * * *",
        "message": "🌅 **Reminder Sahur!**\n\nImsak dalam 1 jam ({reminders['imsak']}). Jangan lupa sahur!\n\n💡 Saran menu sahur:\n• Nasi uduk/nasi goreng\n• Telur (rebus/goreng)\n• Susu/oatmeal\n• Kurma + air putih\n\nSemangat puasanya! 💪"
    })
    
    # 2. Sahur 30 min before imsak
    sahur_30 = reminders['sahur_30min'].split(':')
    cron_jobs.append({
        "name": "Ramadan Sahur 30min",
        "schedule": f"{sahur_30[1]} {sahur_30[0]} * * *",
        "message": f"⚠️ **Waktu Sahur Sisa 30 Menit!**\n\nImsak jam {reminders['imsak']}. Cepat makan dan minum!\n\n⏰ Sisa waktu sedikit, segera selesaikan sahur!"
    })
    
    # 3. 5 min before imsak
    imsak_5 = reminders['imsak_5min'].split(':')
    cron_jobs.append({
        "name": "Ramadan Imsak 5min",
        "schedule": f"{imsak_5[1]} {imsak_5[0]} * * *",
        "message": f"⏰ **5 Menit Lagi Imsak!**\n\nSegera selesaikan makan dan minum. Imsak jam {reminders['imsak']}.\n\n🤲 Persiapkan niat puasa!"
    })
    
    # 4. 5 min before buka (Maghrib)
    buka_5 = reminders['buka_5min'].split(':')
    menu = get_iftar_menus()
    menu_text = "\n".join([f"• {item}" for item in menu['items']])
    
    cron_jobs.append({
        "name": "Ramadan Buka 5min",
        "schedule": f"{buka_5[1]} {buka_5[0]} * * *",
        "message": f"🌙 **5 Menit Lagi Buka Puasa!**\n\nMaghrib jam {reminders['maghrib']}. Siapkan menu buka:\n\n{menu_text}\n\n🤲 Doa buka puasa: \"Allahumma laka shumtu wa bika aamantu wa 'ala rizqika aftartu\""
    })
    
    # 5. Buka puasa time (Maghrib)
    maghrib_time = reminders['maghrib'].split(':')
    cron_jobs.append({
        "name": "Ramadan Buka Time",
        "schedule": f"{maghrib_time[1]} {maghrib_time[0]} * * *",
        "message": f"🌙 **SELAMAT BERBUKA PUASA!**\n\nAlhamdulillah, waktu Maghrib telah tiba ({reminders['maghrib']}).\n\n🤲 Semoga puasa hari ini diterima. Selamat berbuka!\n\nJangan lupa sholat Maghrib ya! 🕌"
    })
    
    # Save cron jobs to file
    output_file = os.path.expanduser("~/.openclaw/workspace/ramadan_cron_jobs.json")
    with open(output_file, 'w') as f:
        json.dump(cron_jobs, f, indent=2)
    
    print(f"✅ Cron jobs saved to: {output_file}")
    print(f"\n📅 Prayer times for today:")
    print(f"   Imsak: {reminders['imsak']}")
    print(f"   Fajr: {reminders['fajr']}")
    print(f"   Maghrib: {reminders['maghrib']}")
    
    return cron_jobs

def main():
    if len(sys.argv) < 2:
        print("Usage: ramadan.py <command>")
        print("")
        print("Commands:")
        print("  today [--telegram]  - Show today's schedule")
        print("  setup               - Create cron jobs for reminders")
        print("  menu                - Show healthy iftar menu")
        print("  location            - Show current location settings")
        print("  buttons             - Get Telegram button config")
        print("  callback <data>     - Handle Telegram button callback")
        sys.exit(1)
    
    command = sys.argv[1]
    telegram_format = "--telegram" in sys.argv
    
    if command == "today":
        timings = get_prayer_times()
        if timings:
            reminders = calculate_reminder_times(timings)
            print(format_schedule_output(reminders, telegram_format))
        else:
            print("Failed to fetch prayer times")
    
    elif command == "setup":
        create_cron_jobs()
        print("\n📝 Next: Run 'openclaw cron add' for each job in ramadan_cron_jobs.json")
    
    elif command == "menu":
        menu = get_iftar_menus()
        print(f"\n🍽️ {menu['name']}:")
        for item in menu['items']:
            print(f"  • {item}")
    
    elif command == "location":
        print(f"\n📍 Current Location:")
        print(f"   City: {DEFAULT_LOCATION['city']}")
        print(f"   Country: {DEFAULT_LOCATION['country']}")
        print(f"   Coordinates: {DEFAULT_LOCATION['latitude']}, {DEFAULT_LOCATION['longitude']}")
        print(f"   Timezone: {DEFAULT_LOCATION['timezone']}")
        print(f"\n   Full Address: Jl. Tubagus Ismail VII No.11 ASekeloa, Kecamatan Coblong, Kota Bandung, Jawa Barat 40134")
    
    elif command == "buttons":
        get_buttons_json()
    
    elif command == "callback" and len(sys.argv) >= 3:
        result = handle_callback(sys.argv[2])
        if result:
            print(result)
        else:
            print(f"Unknown callback: {sys.argv[2]}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
