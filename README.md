# Divoom Times Gate - Direct Screen Control

Control the 5 LCD screens of your Divoom Times Gate directly over your local network, no app required.

![Screen Previews](screenshots/preview.png)

## Why This Exists

The Divoom Times Gate has 5 beautiful 128x128 IPS screens, but the only official way to control them is through the Divoom app. If you want to push custom images, text, or animations programmatically, you're on your own - and the existing documentation is mostly for the Pixoo 64, which uses a **different protocol** that silently fails on the Times Gate.

This repo provides working Python code and a complete API reference for the Times Gate, figured out through reverse engineering and testing.

## Times Gate vs Pixoo 64 - Read This First

Most Divoom code you'll find online targets the Pixoo 64. It will appear to work (the device returns `error_code: 0`) but **nothing will show up**. Here's why:

| | Pixoo 64 | **Times Gate** |
|---|---|---|
| Screens | 1 | **5** (indexed 0-4) |
| Resolution | 64x64 | **128x128** |
| PicData format | Raw RGB bytes | **JPEG base64** |
| PicWidth | 64 | **128** |
| PicID | Small integers OK | **Must use timestamps** |
| Screen targeting | N/A | **LcdArray** field |

The device returns `error_code: 0` for *everything*, even completely wrong payloads. If your screens show garbled blue lines or just don't change - you're probably sending the wrong format.

## Quick Start

### Requirements

```
pip install requests Pillow
```

### Find Your Device

Your Times Gate must be on the same network. Find its IP in the Divoom app under device settings, or check your router's DHCP table.

### Send an Image to a Screen

```python
import requests, base64, time, io
from PIL import Image, ImageDraw, ImageFont

DEVICE_IP = "10.0.0.21"  # <- change to your device IP

# Create a 128x128 image
img = Image.new("RGB", (128, 128), (255, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("arial.ttf", 40)
draw.text((10, 40), "Hello", fill=(255, 255, 255), font=font)

# Encode as JPEG -> base64 (NOT raw RGB!)
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
pic_data = base64.b64encode(buf.getvalue()).decode("utf-8")

# Send to screen 0
requests.post(f"http://{DEVICE_IP}/post", json={
    "Command": "Draw/SendHttpGif",
    "LcdArray": [1, 0, 0, 0, 0],   # screen 0 only
    "PicNum": 1,
    "PicWidth": 128,
    "PicOffset": 0,
    "PicID": int(time.time()),       # must be unique!
    "PicSpeed": 1000,
    "PicData": pic_data,
})
```

### Target Specific Screens

`LcdArray` is a 5-element array. Set `1` for each screen you want to update:

```python
[1, 0, 0, 0, 0]  # screen 0 (leftmost)
[0, 0, 1, 0, 0]  # screen 2 (center)
[1, 1, 1, 1, 1]  # all screens at once
```

### Send Animations

Send multiple frames with the same `PicID` but incrementing `PicOffset`:

```python
for i, frame in enumerate(frames):
    requests.post(f"http://{DEVICE_IP}/post", json={
        "Command": "Draw/SendHttpGif",
        "LcdArray": [1, 0, 0, 0, 0],
        "PicNum": len(frames),      # total frame count
        "PicWidth": 128,
        "PicOffset": i,              # frame index
        "PicID": int(time.time()),   # same ID for all frames
        "PicSpeed": 200,             # ms per frame
        "PicData": encode_jpeg(frame),
    })
```

Keep animations under ~40 frames.

## Files

| File | Description |
|------|-------------|
| [`DIVOOM_TIMESGATE_API.md`](DIVOOM_TIMESGATE_API.md) | Complete API reference with all commands |
| [`divoom_erik.py`](divoom_erik.py) | Example: 5 different styles across all screens (neon, arcade, gold, matrix, fire) |
| [`divoom_test2.py`](divoom_test2.py) | Screen mapping test - sends colored numbers to identify which index is which physical screen |

## API Reference

See [`DIVOOM_TIMESGATE_API.md`](DIVOOM_TIMESGATE_API.md) for the full command reference, including:

- `Draw/SendHttpGif` - send images and animations
- `Draw/ResetHttpGifId` - clear image cache
- `Channel/SetBrightness` - adjust brightness
- `Channel/OnOffScreen` - power on/off
- `Draw/SendHttpItemList` - text overlays with backgrounds
- And more

## Common Issues

**Screens don't change but device returns success**
- You're probably sending 64x64 raw RGB (Pixoo 64 format). Use 128x128 JPEG.

**Garbled blue lines or speaker icon**
- Wrong image format. Must be JPEG-encoded, not raw RGB pixel bytes.

**Same image won't update**
- PicID is cached. Use `int(time.time())` to generate unique IDs.

**Screen shows "loading" animation**
- Reset the cache first: `{"Command": "Draw/ResetHttpGifId"}`

## Useful Resources

- [adiastra/divoom-gaming-gate](https://github.com/adiastra/divoom-gaming-gate) - Python GUI app for Times Gate / Gaming Gate (confirmed working)
- [johnpc/divoom-time-gate](https://github.com/johnpc/divoom-time-gate) - TypeScript, displays Home Assistant status
- [Grayda/pixoo_api NOTES.md](https://github.com/Grayda/pixoo_api/blob/main/NOTES.md) - Reverse-engineered protocol notes

## License

MIT
