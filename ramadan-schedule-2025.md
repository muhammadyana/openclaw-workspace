# Ramadan Reminder Schedule - 2025

## Daily Reminders (Active Now)
| Time | Reminder |
|------|----------|
| 08:00 | 🌅 Breakfast |
| 12:00 | 🍽️ Lunch |
| 18:00 | 🌙 Dinner |

## Ramadan Sahur Reminder
**Active Period:** Feb 28 - March 29, 2025
**Time:** 04:00 AM daily

### Manual Enable/Disable Commands:

**To enable Sahur reminder (Feb 28):**
```
cron:update:Ramadan Sahur Reminder:enabled:true
```

**To disable Sahur reminder (March 29):**
```
cron:update:Ramadan Sahur Reminder:enabled:false
```

## Alternative: Set as One-Time Reminders
If the scheduler has issues, I can set up one-time reminders for specific dates during Ramadan instead.

## Current Active Jobs:
Check with: `cron:list`
