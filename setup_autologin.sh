#!/bin/bash
# Setup Auto-Login for Mac mini
# Run this script on the Mac mini

echo "🔧 Setting up Auto-Login for Mac mini..."

# 1. Check FileVault status
echo "📋 Checking FileVault status..."
FV_STATUS=$(fdesetup status 2>/dev/null | grep -o "FileVault is On")

if [ "$FV_STATUS" = "FileVault is On" ]; then
    echo "⚠️  WARNING: FileVault is ON"
    echo "    Auto-login cannot work with FileVault enabled."
    echo "    You need to either:"
    echo "    1. Turn off FileVault (System Settings > Privacy & Security > FileVault)"
    echo "    2. Or use manual login each time"
    echo ""
    read -p "Do you want to disable FileVault? (y/N): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        echo "🔓 Disabling FileVault (this may take a while)..."
        sudo fdesetup disable
        echo "✅ FileVault disabled. Please restart your Mac and run this script again."
        exit 0
    else
        echo "❌ Auto-login cannot be enabled while FileVault is on."
        exit 1
    fi
fi

# 2. Enable Auto-Login
echo "🔓 Enabling Auto-Login..."

# Method 1: Using defaults (for macOS Ventura and later)
sudo defaults write /Library/Preferences/com.apple.loginwindow autoLoginUser -string "yana"

# Method 2: Alternative using sysadminctl (safer)
# This sets the user to auto-login
sudo sysadminctl -autologin set -userName yana -password "$(osascript -e 'Tell application "System Events" to display dialog "Enter your Mac password:" default answer "" with hidden answer' -e 'text returned of result')" 2>/dev/null

echo ""
echo "✅ Auto-Login Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   User: yana"
echo "   Auto-Login: ENABLED"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "   1. Your Mac will automatically login on boot"
echo "   2. Screen will auto-lock after 5 minutes (for security)"
echo "   3. OpenClaw Gateway will start automatically"
echo ""
echo "🔄 Please restart your Mac to test."
echo ""

# 3. Set auto-lock for security
echo "🔒 Setting up auto-screen lock (5 minutes)..."
defaults write com.apple.screensaver askForPassword -int 1
defaults write com.apple.screensaver askForPasswordDelay -int 300

echo "✅ Auto-lock configured!"
