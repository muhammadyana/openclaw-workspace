#!/bin/bash
# Quick setup for OpenClaw Daemon (One-liner version)
# Run on Mac mini with: curl -fsSL ... | sudo bash

sudo tee /Library/LaunchDaemons/ai.openclaw.gateway.system.plist > /dev/null << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.gateway.system</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
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
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/yana</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
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
    <string>/var/log/openclaw.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/openclaw.err</string>
</dict>
</plist>
EOF

sudo chmod 644 /Library/LaunchDaemons/ai.openclaw.gateway.system.plist
sudo launchctl load /Library/LaunchDaemons/ai.openclaw.gateway.system.plist
sudo launchctl start ai.openclaw.gateway.system

echo "✅ OpenClaw Gateway now runs at boot without login!"
