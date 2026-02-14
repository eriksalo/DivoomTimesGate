"""
Divoom Times Gate - Fixed test with JPEG encoding at 128x128
"""

import requests
import base64
import time
import io
from PIL import Image, ImageDraw, ImageFont

DEVICE_IP = "10.0.0.21"
URL = f"http://{DEVICE_IP}/post"
SIZE = 128


def send_command(payload):
    try:
        r = requests.post(URL, json=payload, timeout=8)
        data = r.json()
        print(f"  -> {data}")
        return data
    except Exception as e:
        print(f"  -> Error: {e}")
        return None


def image_to_picdata(img):
    """Encode as JPEG and base64 - the format Times Gate expects."""
    img = img.convert("RGB").resize((SIZE, SIZE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def send_to_screen(screen_id, img, pic_id=None):
    """Send a 128x128 JPEG image to a specific screen (0-4)."""
    if pic_id is None:
        pic_id = int(time.time()) + screen_id

    lcd = [0, 0, 0, 0, 0]
    lcd[screen_id] = 1
    payload = {
        "Command": "Draw/SendHttpGif",
        "LcdArray": lcd,
        "PicNum": 1,
        "PicWidth": SIZE,
        "PicOffset": 0,
        "PicID": pic_id,
        "PicSpeed": 1000,
        "PicData": image_to_picdata(img),
    }
    print(f"Sending to screen {screen_id} (PicID={pic_id})...")
    return send_command(payload)


def make_test_screen(index, color, label):
    """Big number + color to identify screens."""
    img = Image.new("RGB", (SIZE, SIZE), color)
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 72)
        font_sm = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
    except:
        font_big = ImageFont.load_default()
        font_sm = font_big

    text = str(index)
    bbox = draw.textbbox((0, 0), text, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (SIZE - tw) // 2
    ty = (SIZE - th) // 2 - 10

    # Black outline + white text
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            draw.text((tx + dx, ty + dy), text, fill=(0, 0, 0), font=font_big)
    draw.text((tx, ty), text, fill=(255, 255, 255), font=font_big)

    # Label at bottom
    bbox2 = draw.textbbox((0, 0), label, font=font_sm)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((SIZE - tw2) // 2, SIZE - 30), label, fill=(255, 255, 255), font=font_sm)

    return img


def main():
    print("=" * 50)
    print("  Times Gate Test - 128x128 JPEG format")
    print("=" * 50)

    print("\nResetting GIF cache...")
    send_command({"Command": "Draw/ResetHttpGifId"})
    time.sleep(0.5)

    screens = [
        (0, (255, 0, 0),     "RED"),
        (1, (0, 180, 0),     "GREEN"),
        (2, (0, 80, 255),    "BLUE"),
        (3, (255, 200, 0),   "YELLOW"),
        (4, (255, 0, 200),   "PINK"),
    ]

    for idx, color, label in screens:
        print(f"\nScreen {idx}: {label}")
        img = make_test_screen(idx, color, label)
        img.save(f"test128_{idx}.png")
        send_to_screen(idx, img)
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("Look at your device!")
    print("  0=RED  1=GREEN  2=BLUE  3=YELLOW  4=PINK")
    print("Tell me the order from LEFT to RIGHT")
    print("=" * 50)


if __name__ == "__main__":
    main()
