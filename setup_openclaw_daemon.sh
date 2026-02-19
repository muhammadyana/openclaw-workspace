#!/bin/bash
# Setup OpenClaw Gateway as System Launch Daemon
# This allows OpenClaw to run WITHOUT user login
# Run with: sudo bash setup_openclaw_daemon.sh

set -e

echo "🚀 Setting up OpenClaw Gateway as System Service..."
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run with sudo: sudo bash $0"
    exit 1
fi

# Get username
USERNAME="yana"
USER_HOME="/Users/$USERNAME"

echo "📋 Configuration:"
echo "   User: $USERNAME"
echo "   Home: $USER_HOME"
echo ""

# 1. Stop existing user LaunchAgent
echo "🛑 Stopping existing user LaunchAgent..."
su - $USERNAME -c "launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist 2>/dev/null || true"

# 2. Create LaunchDaemon plist
echo "📄 Creating LaunchDaemon..."
cat > /Library/LaunchDaemons/ai.openclaw.gateway.system.plist << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.gateway.system</string>
    
    <key>Comment</key>
    <string>OpenClaw Gateway (System-wide, no login required)</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/node</string>
        <string>/opt/homebrew/lib/node_modules/openclaw/dist/index.js</string>
        <string>gateway</string>
        <string>--port</string>
        <string>18789</string>
    </array>
    
    <key>UserName</key>
    <string>yana</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/yana</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/yana</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>OPENCLAW_GATEWAY_PORT</key>
        <string>18789</string>
        <key>OPENCLAW_GATEWAY_TOKEN</key>
        <string>75ec23288b23a0c6dc207a5363d421fdd847652c2c4b6690</string>
        <key>MOMO_API_KEY</key>
        <string>momo_jU4VniEjDvO7ax4pqQWL_j1s1bLg2dCKguwgjxVBYI4</string>
        <key>MOMO_API_URL</key>
        <string>https://app.usemomo.com</string>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/var/log/openclaw-gateway.log</string>
    
    <key>StandardErrorPath</key>
    <string>/var/log/openclaw-gateway.error.log</string>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
PLIST_EOF

# 3. Set permissions
echo "🔐 Setting permissions..."
chown root:wheel /Library/LaunchDaemons/ai.openclaw.gateway.system.plist
chmod 644 /Library/LaunchDaemons/ai.openclaw.gateway.system.plist

# 4. Create log files
echo "📝 Creating log files..."
touch /var/log/openclaw-gateway.log
touch /var/log/openclaw-gateway.error.log
chown $USERNAME:admin /var/log/openclaw-gateway.log
chown $USERNAME:admin /var/log/openclaw-gateway.error.log
chmod 644 /var/log/openclaw-gateway.log
chmod 644 /var/log/openclaw-gateway.error.log

# 5. Load and start the daemon
echo "▶️  Starting OpenClaw Gateway..."
launchctl load /Library/LaunchDaemons/ai.openclaw.gateway.system.plist
sleep 2
launchctl start ai.openclaw.gateway.system

# 6. Verify
echo ""
echo "🔍 Verifying..."
sleep 3
if launchctl list | grep -q "ai.openclaw.gateway.system"; then
    PID=$(launchctl list | grep "ai.openclaw.gateway.system" | awk '{print $1}')
    echo "✅ SUCCESS! OpenClaw Gateway is running (PID: $PID)"
    echo ""
    echo "📊 Status:"
    launchctl list | grep "ai.openclaw.gateway.system"
else
    echo "⚠️  Warning: Daemon may not have started properly"
    echo "   Check logs: tail -f /var/log/openclaw-gateway.error.log"
fi

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   Service: ai.openclaw.gateway.system"
echo "   Status: Auto-starts at boot (no login required)"
echo "   Port: 18789"
echo "   Logs: /var/log/openclaw-gateway*.log"
echo ""
echo "🧹 Cleanup:"
echo "   Old user LaunchAgent disabled"
echo ""
echo "🔄 Test:"
echo "   1. Restart your Mac"
echo "   2. Don't login"
echo "   3. Check if OpenClaw is running:"
echo "      sudo launchctl list | grep openclaw"
echo ""
echo "📱 Telegram should work immediately after boot!"
echo ""
