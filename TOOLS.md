# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Workspace Location

**Main workspace:** `/Users/yana/works/`

**Raciq projects path:** `/Users/yana/works/raciq/`

This is where all project repositories are located:
- `/Users/yana/works/raciq/Raciqadmin` - Raciq Admin
- `/Users/yana/works/raciq/Raciqfe` - Raciq Frontend
- `/Users/yana/works/raciq/raciq-be` - Raciq Backend
- `/Users/yana/works/iot/` - IoT/Smart home control
- `/Users/yana/works/hermina/` - Hermina Workspace

Always check this directory first when looking for project repositories.

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

### CCTV Surveillance Commands (SOP - MUST FOLLOW)

**Trigger phrases:**
- "what do you see" / "apa yang kamu lihat"
- "what you hear" / "apa yang kamu dengar"
- "what do you see and hear"

**Actions for SEE:**
1. Capture snapshot: `camsnap snap tapo --out /tmp/cctv_$(date +%Y%m%d_%H%M%S).jpg`
2. Describe image in detail
3. **SEND image via Telegram** (copy to workspace first)
4. Generate TTS using **Gemini Live API** and send audio

**Actions for HEAR:**
1. Capture **10-second** audio: `camsnap clip tapo --dur 10s --out /tmp/cctv_audio.mp4`
2. Convert to audio and transcribe
3. **SEND audio file via Telegram**
4. Include transcription in text

**Actions for SEE + HEAR:**
1. Capture BOTH simultaneously
2. Process image (describe + send photo + TTS)
3. Process audio (transcribe + send audio)

**CRITICAL RULES:**
- ALWAYS send actual image file, not just description
- ALWAYS send actual audio file, not just transcription
- ALWAYS generate TTS and send voice message
- Include timestamp from camera overlay

**Camera:** Tapo C222 (192.168.31.133, 2K resolution)

**Gemini Live API Key:** `AIzaSyB24dZvCkIBV5FaxMvH6d3vBQjDLLfYbp4`

---

### Gemini Live API Setup (IN PROGRESS)

**API Key:** `AIzaSyB24dZvCkIBV5FaxMvH6d3vBQjDLLfYbp4`

**Status:** ⚠️ API Key configured but getting 404 errors

**Setup Steps:**
1. ✅ Gemini CLI installed (`gemini` v0.25.2)
2. ✅ Config file created at `~/.config/gemini/config.json`
3. ✅ Python script created at `~/.openclaw/workspace/scripts/gemini_tts.py`
4. ❌ API returning 404 - possible issues:
   - API key may need project activation
   - Gemini API may require different endpoint for TTS
   - Project may need billing enabled

**Current Workaround:** Using default TTS (ElevenLabs) until Gemini Live API is fully configured.

**Note:** Gemini Live API is different from regular Gemini chat API. For TTS, may need to use Google Cloud Text-to-Speech API instead.

---

Add whatever helps you do your job. This is your cheat sheet.
