"""
Divoom Times Gate Direct Control - "Erik Salo" on all 5 screens
Each screen gets a unique fun style!

Key specs: 128x128 per screen, JPEG-encoded PicData, timestamp PicIDs.
"""

import requests
import base64
import time
import io
import math
import random
from PIL import Image, ImageDraw, ImageFont

DEVICE_IP = "10.0.0.21"
URL = f"http://{DEVICE_IP}/post"
SIZE = 128


def send_command(payload):
    try:
        r = requests.post(URL, json=payload, timeout=8)
        print(f"  -> {r.json()}")
        return r.json()
    except Exception as e:
        print(f"  -> Error: {e}")
        return None


def image_to_picdata(img):
    """Convert PIL Image to base64 JPEG for Times Gate."""
    img = img.convert("RGB").resize((SIZE, SIZE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def send_to_screen(screen_id, img):
    lcd = [0] * 5
    lcd[screen_id] = 1
    pic_id = int(time.time()) + screen_id
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
    print(f"Sending to screen {screen_id}...")
    return send_command(payload)


def send_animation(screen_id, frames, speed_ms=200):
    lcd = [0] * 5
    lcd[screen_id] = 1
    pic_id = int(time.time()) + screen_id + 100
    print(f"Sending {len(frames)}-frame animation to screen {screen_id}...")
    for i, frame in enumerate(frames):
        payload = {
            "Command": "Draw/SendHttpGif",
            "LcdArray": lcd,
            "PicNum": len(frames),
            "PicWidth": SIZE,
            "PicOffset": i,
            "PicID": pic_id,
            "PicSpeed": speed_ms,
            "PicData": image_to_picdata(frame),
        }
        send_command(payload)
    print(f"  Done!")


def get_font(name, size):
    """Try to load a Windows font by name."""
    paths = {
        "bold": ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"],
        "regular": ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"],
        "script": [
            "C:/Windows/Fonts/MISTRAL.TTF",
            "C:/Windows/Fonts/PRISTINA.TTF",
            "C:/Windows/Fonts/segoesc.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ],
        "impact": ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"],
    }
    for p in paths.get(name, paths["regular"]):
        try:
            return ImageFont.truetype(p, size)
        except:
            pass
    return ImageFont.load_default()


def draw_text_centered(draw, text, y, font, fill, outline=None, outline_width=2):
    """Draw text centered horizontally with optional outline."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (SIZE - tw) // 2
    if outline:
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx * dx + dy * dy <= outline_width * outline_width:
                    draw.text((x + dx, y + dy), text, fill=outline, font=font)
    draw.text((x, y), text, fill=fill, font=font)


# ==============================================================================
# Screen 0: Neon Glow - cyan ERIK, magenta SALO
# ==============================================================================
def make_screen_neon():
    img = Image.new("RGB", (SIZE, SIZE), (5, 5, 20))
    draw = ImageDraw.Draw(img)

    font = get_font("bold", 44)

    # ERIK - cyan neon glow
    glow_layers = [
        (6, (0, 30, 60)), (5, (0, 50, 100)), (4, (0, 80, 160)),
        (3, (0, 130, 220)), (2, (50, 180, 255)), (1, (150, 230, 255)),
    ]
    bbox = draw.textbbox((0, 0), "ERIK", font=font)
    tw = bbox[2] - bbox[0]
    tx = (SIZE - tw) // 2

    for radius, color in glow_layers:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    draw.text((tx + dx, 10 + dy), "ERIK", fill=color, font=font)
    draw.text((tx, 10), "ERIK", fill=(220, 250, 255), font=font)

    # SALO - magenta neon glow
    font2 = get_font("bold", 40)
    glow_layers2 = [
        (6, (50, 0, 30)), (5, (80, 0, 50)), (4, (130, 0, 80)),
        (3, (190, 0, 130)), (2, (240, 40, 180)), (1, (255, 120, 220)),
    ]
    bbox2 = draw.textbbox((0, 0), "SALO", font=font2)
    tw2 = bbox2[2] - bbox2[0]
    tx2 = (SIZE - tw2) // 2

    for radius, color in glow_layers2:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    draw.text((tx2 + dx, 68 + dy), "SALO", fill=color, font=font2)
    draw.text((tx2, 68), "SALO", fill=(255, 220, 250), font=font2)

    # Subtle bottom bar
    for x in range(16, 112):
        b = int(60 + 40 * math.sin(x * 0.15))
        draw.point((x, 118), fill=(0, b, b))
        draw.point((x, 119), fill=(0, b // 2, b // 2))

    return img


# ==============================================================================
# Screen 1: Rainbow Arcade - each letter a different color, starfield
# ==============================================================================
def make_screen_arcade():
    img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Starfield
    random.seed(42)
    for _ in range(100):
        x, y = random.randint(0, 127), random.randint(0, 127)
        b = random.randint(40, 180)
        draw.point((x, y), fill=(b, b, b))

    font = get_font("impact", 34)

    # ERIK - each letter rainbow colored
    colors_top = [(255, 50, 50), (255, 220, 0), (50, 255, 50), (50, 180, 255)]
    letters_top = list("ERIK")
    # Measure total width
    total_w = sum(draw.textbbox((0, 0), c, font=font)[2] - draw.textbbox((0, 0), c, font=font)[0] for c in letters_top)
    spacing = 4
    total_w += spacing * (len(letters_top) - 1)
    cx = (SIZE - total_w) // 2
    for letter, color in zip(letters_top, colors_top):
        bbox = draw.textbbox((0, 0), letter, font=font)
        lw = bbox[2] - bbox[0]
        # Shadow
        draw.text((cx + 2, 14), letter, fill=(color[0] // 5, color[1] // 5, color[2] // 5), font=font)
        draw.text((cx, 12), letter, fill=color, font=font)
        cx += lw + spacing

    # SALO - complementary colors
    colors_bot = [(255, 100, 255), (0, 255, 200), (255, 150, 50), (150, 100, 255)]
    letters_bot = list("SALO")
    total_w2 = sum(draw.textbbox((0, 0), c, font=font)[2] - draw.textbbox((0, 0), c, font=font)[0] for c in letters_bot)
    total_w2 += spacing * (len(letters_bot) - 1)
    cx2 = (SIZE - total_w2) // 2
    for letter, color in zip(letters_bot, colors_bot):
        bbox = draw.textbbox((0, 0), letter, font=font)
        lw = bbox[2] - bbox[0]
        draw.text((cx2 + 2, 60), letter, fill=(color[0] // 5, color[1] // 5, color[2] // 5), font=font)
        draw.text((cx2, 58), letter, fill=color, font=font)
        cx2 += lw + spacing

    # Rainbow bar at bottom
    for x in range(SIZE):
        hue = (x * 4) % 360
        r = int(127 + 127 * math.sin(math.radians(hue)))
        g = int(127 + 127 * math.sin(math.radians(hue + 120)))
        b = int(127 + 127 * math.sin(math.radians(hue + 240)))
        for y in range(100, 108):
            draw.point((x, y), fill=(r, g, b))

    # Pixel border
    for i in range(0, SIZE, 6):
        draw.rectangle([i, 0, i + 2, 2], fill=(80, 80, 80))
        draw.rectangle([i, 125, i + 2, 127], fill=(80, 80, 80))

    return img


# ==============================================================================
# Screen 2: Elegant Gold on Purple - ornamental frame, script font
# ==============================================================================
def make_screen_gold():
    img = Image.new("RGB", (SIZE, SIZE), (25, 8, 40))
    draw = ImageDraw.Draw(img)

    # Gradient purple background
    for y in range(SIZE):
        r = int(25 + 10 * math.sin(y * 0.03))
        g = int(8 + 5 * math.sin(y * 0.03))
        b = int(40 + 15 * math.sin(y * 0.03))
        draw.line([(0, y), (127, y)], fill=(r, g, b))

    gold = (255, 210, 60)
    gold_dim = (160, 130, 40)

    # Ornamental double border
    draw.rectangle([4, 4, 123, 123], outline=gold_dim, width=1)
    draw.rectangle([8, 8, 119, 119], outline=gold, width=2)

    # Corner flourishes
    for cx, cy in [(8, 8), (119, 8), (8, 119), (119, 119)]:
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=gold)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 240, 150))

    # "Erik" in script font
    font_script = get_font("script", 40)
    draw_text_centered(draw, "Erik", 22, font_script, gold, outline=(80, 50, 10), outline_width=2)

    # Decorative divider
    mid_y = 68
    draw.line([(20, mid_y), (108, mid_y)], fill=gold_dim, width=1)
    draw.ellipse([58, mid_y - 4, 70, mid_y + 4], fill=gold)
    draw.ellipse([60, mid_y - 2, 68, mid_y + 2], fill=(255, 240, 150))
    # Side diamonds
    for dx in [-25, 25]:
        draw.polygon([(64 + dx, mid_y - 3), (64 + dx + 3, mid_y),
                       (64 + dx, mid_y + 3), (64 + dx - 3, mid_y)], fill=gold)

    # "Salo" in script font
    draw_text_centered(draw, "Salo", 76, font_script, gold, outline=(80, 50, 10), outline_width=2)

    return img


# ==============================================================================
# Screen 3: Matrix Rain animation
# ==============================================================================
def make_screen_matrix(num_frames=10):
    random.seed(123)
    frames = []

    # Pre-generate rain columns
    columns = []
    for c in range(20):
        columns.append({
            "chars": [chr(random.randint(0x30A0, 0x30FF)) if random.random() > 0.3
                      else chr(random.randint(33, 126)) for _ in range(30)],
            "speed": random.uniform(0.5, 2.0),
            "offset": random.uniform(0, 30),
        })

    font_small = get_font("regular", 10)
    font_name = get_font("bold", 30)

    for frame_idx in range(num_frames):
        img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        t = frame_idx

        # Matrix rain
        for col_idx, col in enumerate(columns):
            x = col_idx * 7
            pos = (col["offset"] + t * col["speed"]) % 30
            for row in range(20):
                char_idx = int(pos + row) % len(col["chars"])
                y = row * 7
                dist = row - int(pos) % 20
                if dist < 0:
                    dist += 20
                if dist == 0:
                    color = (180, 255, 180)
                elif dist < 3:
                    color = (0, max(0, 200 - dist * 60), 0)
                elif dist < 7:
                    color = (0, max(0, 80 - (dist - 3) * 20), 0)
                else:
                    continue
                try:
                    draw.text((x, y), col["chars"][char_idx], fill=color, font=font_small)
                except:
                    draw.text((x, y), "?", fill=color, font=font_small)

        # Name overlay with dark background for readability
        pulse = 0.7 + 0.3 * math.sin(frame_idx * math.pi / 3)
        bright = int(255 * pulse)

        # Background boxes
        draw.rectangle([10, 30, 118, 62], fill=(0, 10, 0))
        draw.rectangle([10, 68, 118, 100], fill=(0, 10, 0))

        draw_text_centered(draw, "ERIK", 32, font_name, (bright, 255, bright),
                          outline=(0, 40, 0), outline_width=2)
        draw_text_centered(draw, "SALO", 70, font_name, (bright, 255, bright),
                          outline=(0, 40, 0), outline_width=2)

        frames.append(img)

    return frames


# ==============================================================================
# Screen 4: Fire & Lava animation
# ==============================================================================
def make_screen_fire(num_frames=10):
    frames = []

    for frame_idx in range(num_frames):
        random.seed(frame_idx * 7 + 99)
        img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fire gradient from bottom
        for y in range(SIZE):
            for x in range(0, SIZE, 2):  # step by 2 for speed, fill 2px wide
                heat = max(0, (SIZE - y) / SIZE)
                noise = random.uniform(0.6, 1.0)
                flicker = 0.8 + 0.2 * math.sin(x * 0.3 + frame_idx * 1.2)
                intensity = heat * noise * flicker

                if intensity > 0.7:
                    r, g, b = 255, int(220 * intensity), int(80 * intensity)
                elif intensity > 0.4:
                    r, g, b = int(255 * intensity), int(130 * intensity), 0
                elif intensity > 0.15:
                    r, g, b = int(200 * intensity), int(50 * intensity), 0
                else:
                    r, g, b = int(80 * intensity), 0, 0

                r, g, b = min(255, r), min(255, g), min(255, b)
                draw.rectangle([x, y, x + 1, y], fill=(r, g, b))

        # Name text - white/yellow, bold with dark outline
        font = get_font("bold", 36)
        draw_text_centered(draw, "ERIK", 20, font, (255, 255, 220),
                          outline=(50, 10, 0), outline_width=3)
        draw_text_centered(draw, "SALO", 70, font, (255, 255, 220),
                          outline=(50, 10, 0), outline_width=3)

        frames.append(img)

    return frames


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 60)
    print("  Divoom Times Gate - Erik Salo Display Controller")
    print(f"  Device: {DEVICE_IP} | Resolution: {SIZE}x{SIZE} JPEG")
    print("=" * 60)

    print("\n[1] Resetting GIF cache...")
    send_command({"Command": "Draw/ResetHttpGifId"})
    time.sleep(0.5)

    print("\n[2] Setting brightness...")
    send_command({"Command": "Channel/SetBrightness", "Brightness": 80})
    time.sleep(0.3)

    # Generate and send each screen
    print("\n[3] Screen 0: Neon Glow")
    img0 = make_screen_neon()
    img0.save("screen0_neon.png")
    send_to_screen(0, img0)
    time.sleep(0.5)

    print("\n[4] Screen 1: Retro Arcade")
    img1 = make_screen_arcade()
    img1.save("screen1_arcade.png")
    send_to_screen(1, img1)
    time.sleep(0.5)

    print("\n[5] Screen 2: Elegant Gold")
    img2 = make_screen_gold()
    img2.save("screen2_gold.png")
    send_to_screen(2, img2)
    time.sleep(0.5)

    print("\n[6] Screen 3: Matrix Rain (animated)")
    frames3 = make_screen_matrix(num_frames=10)
    frames3[0].save("screen3_matrix.png")
    send_animation(3, frames3, speed_ms=300)
    time.sleep(0.5)

    print("\n[7] Screen 4: Fire & Lava (animated)")
    frames4 = make_screen_fire(num_frames=10)
    frames4[0].save("screen4_fire.png")
    send_animation(4, frames4, speed_ms=250)

    print("\n" + "=" * 60)
    print("  All 5 screens updated!")
    print("  0: Neon Glow (cyan + magenta)")
    print("  1: Rainbow Arcade (starfield)")
    print("  2: Elegant Gold (purple + gold frame)")
    print("  3: Matrix Rain (animated green)")
    print("  4: Fire & Lava (animated flames)")
    print("=" * 60)


if __name__ == "__main__":
    main()
