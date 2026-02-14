# Divoom Times Gate - Direct Control API Guide

Control the 5 LCD screens of a Divoom Times Gate over your local network via HTTP.

## Quick Start

```python
import requests, base64, time, io
from PIL import Image, ImageDraw, ImageFont

DEVICE_IP = "10.0.0.21"
URL = f"http://{DEVICE_IP}/post"

# Create a 128x128 image
img = Image.new("RGB", (128, 128), (255, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
draw.text((10, 40), "Hello", fill=(255, 255, 255), font=font)

# Encode as JPEG → base64
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
pic_data = base64.b64encode(buf.getvalue()).decode("utf-8")

# Send to screen 0
requests.post(URL, json={
    "Command": "Draw/SendHttpGif",
    "LcdArray": [1, 0, 0, 0, 0],  # target screen 0
    "PicNum": 1,
    "PicWidth": 128,
    "PicOffset": 0,
    "PicID": int(time.time()),
    "PicSpeed": 1000,
    "PicData": pic_data,
})
```

## Connection Details

| Setting | Value |
|---------|-------|
| **Protocol** | HTTP POST |
| **Endpoint** | `http://<device-ip>/post` |
| **Port** | 80 (default) |
| **Content-Type** | `application/json` |
| **Authentication** | None (local network only) |

All commands return `{"error_code": 0}` on success.

## Critical: Times Gate vs Pixoo 64

The Times Gate is **NOT** the same as a Pixoo 64. Many online examples target the Pixoo 64 and will silently fail on the Times Gate:

| | Pixoo 64 | Times Gate |
|---|---|---|
| **Screens** | 1 | 5 (indexed 0–4) |
| **Resolution** | 64×64 | **128×128** per screen |
| **PicData format** | Raw RGB bytes | **JPEG encoded** |
| **PicWidth** | 64 | **128** |
| **Screen targeting** | N/A | `LcdArray` field |
| **PicID** | Small integers OK | **Must use timestamps** (device caches by ID) |

### Common Pitfalls

- **Wrong image size**: Sending 64×64 raw RGB produces garbled output (blue lines, speaker icons)
- **Raw RGB instead of JPEG**: The device accepts the command (error_code 0) but displays garbage
- **Reusing PicIDs**: The device caches frames by PicID. Always use `int(time.time()) + offset` to guarantee uniqueness
- **No error feedback**: The device returns `error_code: 0` for almost everything, even when the payload is wrong

## Screen Layout

The 5 screens are arranged in a horizontal row. Screen indices 0–4 map left-to-right (verify with a color test on your specific unit).

```
┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
│ 0 │ │ 1 │ │ 2 │ │ 3 │ │ 4 │
└───┘ └───┘ └───┘ └───┘ └───┘
```

### LcdArray Targeting

`LcdArray` is a 5-element array of 0/1 values. Set `1` to target that screen:

```python
[1, 0, 0, 0, 0]  # screen 0 only
[0, 0, 1, 0, 0]  # screen 2 only
[1, 1, 1, 1, 1]  # all screens
[1, 0, 0, 0, 1]  # screens 0 and 4
```

## Commands Reference

### Draw/SendHttpGif — Send Image to Screen(s)

The primary command. Sends a static image or animation frame to one or more screens.

```json
{
    "Command": "Draw/SendHttpGif",
    "LcdArray": [1, 0, 0, 0, 0],
    "PicNum": 1,
    "PicWidth": 128,
    "PicOffset": 0,
    "PicID": 1771085172,
    "PicSpeed": 1000,
    "PicData": "<base64-encoded JPEG>"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `LcdArray` | int[5] | Which screens to target (0 or 1 per screen) |
| `PicNum` | int | Total number of frames (1 = static image) |
| `PicWidth` | int | **Must be 128** for Times Gate |
| `PicOffset` | int | Frame index (0-based). For static images, always 0 |
| `PicID` | int | Unique ID. **Use `int(time.time())`** to avoid cache hits |
| `PicSpeed` | int | Frame duration in milliseconds (for animations) |
| `PicData` | string | Base64-encoded **JPEG** image data |

#### PicData Encoding (Python)

```python
import io, base64
from PIL import Image

def image_to_picdata(img):
    """Convert PIL Image to Times Gate PicData string."""
    img = img.convert("RGB").resize((128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
```

#### Helper: Send to One Screen

```python
def send_to_screen(screen_id, pil_image):
    lcd = [0] * 5
    lcd[screen_id] = 1
    payload = {
        "Command": "Draw/SendHttpGif",
        "LcdArray": lcd,
        "PicNum": 1,
        "PicWidth": 128,
        "PicOffset": 0,
        "PicID": int(time.time()) + screen_id,
        "PicSpeed": 1000,
        "PicData": image_to_picdata(pil_image),
    }
    return requests.post(f"http://{DEVICE_IP}/post", json=payload, timeout=8)
```

### Sending Animations (Multi-Frame)

Send multiple frames with the same `PicID` but incrementing `PicOffset`:

```python
def send_animation(screen_id, frames, speed_ms=200):
    lcd = [0] * 5
    lcd[screen_id] = 1
    pic_id = int(time.time()) + screen_id

    for i, frame in enumerate(frames):
        payload = {
            "Command": "Draw/SendHttpGif",
            "LcdArray": lcd,
            "PicNum": len(frames),
            "PicWidth": 128,
            "PicOffset": i,
            "PicID": pic_id,
            "PicSpeed": speed_ms,
            "PicData": image_to_picdata(frame),
        }
        requests.post(URL, json=payload, timeout=8)

    time.sleep(0.3)  # let device process
```

**Limits**: ~40 frames max before device may crash. Each JPEG frame is ~5-15 KB base64.

### Draw/ResetHttpGifId — Clear Image Cache

Call before sending new images to avoid stale cached frames.

```json
{"Command": "Draw/ResetHttpGifId"}
```

### Channel/SetBrightness — Set Display Brightness

```json
{"Command": "Channel/SetBrightness", "Brightness": 80}
```

Value: 0–100.

### Channel/OnOffScreen — Screen Power

```json
{"Command": "Channel/OnOffScreen", "OnOff": 1}
```

1 = on, 0 = off.

### Channel/GetIndex — Get Current Channel Per Screen

```json
{"Command": "Channel/GetIndex"}
```

Returns:
```json
{"error_code": 0, "SelectIndex": [0, 0, 0, 0, 0]}
```

Each element is the channel index for that screen (0 = clock/faces).

### Channel/GetAllConf — Get Device Configuration

```json
{"Command": "Channel/GetAllConf"}
```

Returns brightness, date format, temperature mode, etc.

### Device/GetDeviceTime — Get Device Clock

```json
{"Command": "Device/GetDeviceTime"}
```

Returns UTC and local time.

### Draw/SendHttpItemList — Text Overlay with Background (Times Gate Specific)

This command uses `LcdIndex` (single int) instead of `LcdArray`:

```json
{
    "Command": "Draw/SendHttpItemList",
    "LcdIndex": 0,
    "NewFlag": 1,
    "BackgroudGif": "http://YOUR_SERVER:PORT/bg.gif",
    "ItemList": [
        {
            "TextId": 1,
            "type": 22,
            "x": 10,
            "y": 50,
            "dir": 0,
            "font": 4,
            "TextWidth": 128,
            "Textheight": 16,
            "TextString": "Hello!",
            "speed": 100,
            "color": "#FFFFFF"
        }
    ]
}
```

| ItemList type | Description |
|---------------|-------------|
| 6 | Time display (HH:MM:SS) |
| 22 | Static text |
| 23 | Dynamic text from URL (polls `TextString` URL, expects `{"DispData": "text"}`) |

Note: `BackgroudGif` (with the typo) must be a URL the device can reach on your network.

## Full Working Example: 5 Screens

```python
"""Send a different image to each of the 5 Times Gate screens."""

import requests, base64, time, io
from PIL import Image, ImageDraw, ImageFont

DEVICE_IP = "10.0.0.21"
URL = f"http://{DEVICE_IP}/post"
SIZE = 128


def send_command(payload):
    r = requests.post(URL, json=payload, timeout=8)
    return r.json()


def image_to_picdata(img):
    img = img.convert("RGB").resize((SIZE, SIZE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def send_to_screen(screen_id, img):
    lcd = [0] * 5
    lcd[screen_id] = 1
    return send_command({
        "Command": "Draw/SendHttpGif",
        "LcdArray": lcd,
        "PicNum": 1,
        "PicWidth": SIZE,
        "PicOffset": 0,
        "PicID": int(time.time()) + screen_id,
        "PicSpeed": 1000,
        "PicData": image_to_picdata(img),
    })


# Reset cache
send_command({"Command": "Draw/ResetHttpGifId"})
time.sleep(0.5)

# Send to each screen
for i in range(5):
    img = Image.new("RGB", (SIZE, SIZE), (i * 50, 100, 255 - i * 50))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    draw.text((30, 35), str(i), fill=(255, 255, 255), font=font)
    send_to_screen(i, img)
    time.sleep(0.5)
```

## References

- [adiastra/divoom-gaming-gate](https://github.com/adiastra/divoom-gaming-gate) — Python, confirmed working with 128px JPEG
- [johnpc/divoom-time-gate](https://github.com/johnpc/divoom-time-gate) — TypeScript HA status display
- [Grayda/pixoo_api NOTES.md](https://github.com/Grayda/pixoo_api/blob/main/NOTES.md) — Reverse-engineered protocol docs
- [DivoomDevelop/DivoomPCMonitorTool](https://github.com/DivoomDevelop/DivoomPCMonitorTool) — Official C# tool
