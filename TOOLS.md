# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### IoT / Smart Home

Location: `/Users/yana/works/iot`
Main script: `iot_control.py` (Python 3.10.14 via pyenv)
Chat handler: `iot_chat.py` → called via `bin/iot-chat`

**Command syntax I should detect:**
- "turn on the light(s)" → lights ON
- "turn off the light(s)" → lights OFF  
- "turn on workspace/tv/dispenser" → socket ON
- "turn off all devices" → everything OFF
- "matikan lampu" (Indonesian) → lights OFF

**Available devices:**
- `lights` - All WiZ (4 lights) + Tuya lights (LED strip, teras, tengah, bathroom, kamar 2-5, 7)
- `wiz` - Just the 4 WiZ lights
- `led` / `strip` - LED Strip (Tuya)
- `workspace` - Workspace socket
- `dispenser` - Water dispenser socket
- `tv` - TV socket
- `all` - Everything

**Direct shell commands:**
```bash
# Via bin scripts
/Users/yana/works/iot/bin/iot-chat "turn off the lights"
/Users/yana/works/iot/bin/home-off    # Turn everything off
/Users/yana/works/iot/bin/home-on     # Turn everything on

# Direct Python (uses pyenv 3.10.14)
~/.pyenv/versions/3.10.14/bin/python3 ~/works/iot/iot_control.py off lights
```

**Integration:** When user sends messages like "turn off the light", I should:
1. Parse the natural language command
2. Execute: `/Users/yana/works/iot/bin/iot-chat "<message>"`
3. Or run Python directly for faster response

---

### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Smart Speakers & TVs

**Google Nest Mini** (192.168.31.63)
- Script: `/Users/yana/works/iot/bin/nest-mini`
- Commands:
  - `nest-mini volume 50` - Set volume
  - `nest-mini play|pause|stop` - Playback control
  - `nest-mini mute|unmute` - Mute control
  - `nest-mini status` - Check status
  - `nest-mini tts "Hello"` - Text-to-speech

**Samsung Q700D Soundbar** (192.168.31.21)

**Samsung TV QN90D** (192.168.31.129)
- Connected via: **SmartThings API** (works via WiFi!)
- Script: `/Users/yana/works/iot/bin/tv-samsung` → uses SmartThings
- Commands:
  - `tv-samsung on` - Turn ON (works even when offline!)
  - `tv-samsung off` - Turn OFF
  - `tv-samsung status` - Check power status
  - `tv-samsung volume 50` - Set volume
  - `tv-samsung mute/unmute` - Mute control
- SmartThings Token: `bba1035b-2114-4d05-9e4c-672413205743`

**Chat commands I should detect:**
- "set nest volume to 50" → Set Nest volume
- "play music on nest" → Start playback
- "make nest say hello" → TTS
- "turn on samsung tv" → SmartThings ON
- "turn off tv" → SmartThings OFF

---

### Cameras

**Tapo C222 (RTSP-enabled)**
- IP: `192.168.31.133`
- RTSP: `rtsp://iotcctv:SmartHome@192.168.31.133:554/stream1` (HD) or `stream2` (SD)
- Script: `/Users/yana/works/iot/bin/camera-open [stream1|stream2]`

**Xiaomi Camera (needs RTSP hack)**
- IP: `192.168.31.189`
- Token: `4d5649314a4b4452626b4b5463417a6c`
- To enable RTSP: Copy `sdcard_hack/` files to SD card root
- RTSP URL (after hack): `rtsp://192.168.31.189/live/ch00_0`

**Chat commands I should detect:**
- "open my camera" / "open cctv" → Opens Tapo C222
- "show camera" / "view cctv" → Opens Tapo C222

---

Add whatever helps you do your job. This is your cheat sheet.
