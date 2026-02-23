"""
Divoom Times Gate Direct Control - "Erik Salo" on all 5 screens
Each screen gets a unique fun style with rich, detailed backgrounds!

Key specs: 128x128 per screen, JPEG-encoded PicData, timestamp PicIDs.
"""

import requests
import base64
import time
import io
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops

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
# Screen 0: Synthwave Neon - retro sunset, grid floor, neon glow text
# ==============================================================================
def make_screen_neon():
    img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    horizon_y = 58

    # Sky gradient: deep indigo at top -> warm magenta/orange at horizon
    for y in range(horizon_y + 1):
        t = y / horizon_y
        r = int(10 + 150 * (t ** 2.5))
        g = int(2 + 20 * (t ** 3))
        b = int(50 + 30 * t - 40 * (t ** 2))
        draw.line([(0, y), (SIZE - 1, y)], fill=(r, g, b))

    # Retro striped sun at horizon
    sun_cx = SIZE // 2
    for sy in range(max(0, horizon_y - 22), horizon_y + 1):
        dist = horizon_y - sy
        # Horizontal stripe gaps for retro look
        if dist > 4 and (dist % 4) < 2:
            continue
        width = int(22 * math.sqrt(max(0, 1.0 - (dist / 22) ** 2)))
        intensity = 1.0 - (dist / 22) ** 0.5
        r = min(255, int(255 * intensity))
        g = min(255, int(100 * intensity))
        b = min(255, int(60 * intensity))
        draw.line([(sun_cx - width, sy), (sun_cx + width, sy)], fill=(r, g, b))

    # Floor: dark purple base
    for y in range(horizon_y + 1, SIZE):
        t = (y - horizon_y) / (SIZE - horizon_y)
        r = int(25 * (1 - t * 0.7))
        g = 3
        b = int(45 * (1 - t * 0.5))
        draw.line([(0, y), (SIZE - 1, y)], fill=(r, g, b))

    # Perspective horizontal grid lines
    for i in range(1, 18):
        gy = horizon_y + int((i ** 1.5) * 1.8)
        if gy >= SIZE:
            break
        brightness = max(20, 90 - i * 5)
        draw.line([(0, gy), (SIZE - 1, gy)], fill=(brightness, 0, brightness))

    # Perspective vertical grid lines radiating from horizon center
    cx = SIZE // 2
    for i in range(-12, 13):
        if i == 0:
            continue
        bot_x = cx + i * 16
        brightness = max(15, 70 - abs(i) * 5)
        draw.line([(cx, horizon_y + 1), (bot_x, SIZE - 1)],
                  fill=(brightness, 0, brightness))

    # Stars in sky
    random.seed(77)
    for _ in range(60):
        sx = random.randint(0, SIZE - 1)
        sy = random.randint(0, horizon_y - 25)
        b = random.randint(80, 230)
        s = random.choice([1, 1, 1, 2])
        if s == 1:
            draw.point((sx, sy), fill=(b, b, int(b * 0.8)))
        else:
            draw.rectangle([sx, sy, sx + 1, sy + 1], fill=(b, b, int(b * 0.8)))

    # --- Neon glow text ---
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
                    draw.text((tx + dx, 6 + dy), "ERIK", fill=color, font=font)
    draw.text((tx, 6), "ERIK", fill=(220, 250, 255), font=font)

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

    return img


# ==============================================================================
# Screen 1: Cosmic Nebula Arcade - gas clouds, bright stars, rainbow letters
# ==============================================================================
def make_screen_arcade():
    img = Image.new("RGB", (SIZE, SIZE), (2, 2, 8))

    # Nebula clouds via additive blending of soft radial blobs
    nebula_data = [
        (30, 95, 55, (90, 20, 130)),    # purple blob bottom-left
        (105, 25, 48, (20, 45, 140)),   # blue blob top-right
        (55, 55, 60, (70, 10, 55)),     # dark magenta center
        (12, 18, 42, (10, 85, 95)),     # teal blob top-left
        (115, 105, 45, (110, 30, 85)),  # pink blob bottom-right
    ]
    for cx, cy, radius, (nr, ng, nb) in nebula_data:
        blob = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
        blob_draw = ImageDraw.Draw(blob)
        for r in range(radius, 0, -1):
            t = (1.0 - r / radius) ** 1.5
            color = (int(nr * t), int(ng * t), int(nb * t))
            blob_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        img = ImageChops.add(img, blob)

    draw = ImageDraw.Draw(img)

    # Varied starfield
    random.seed(42)
    for _ in range(160):
        sx = random.randint(0, SIZE - 1)
        sy = random.randint(0, SIZE - 1)
        brightness = random.randint(60, 255)
        size = random.choices([1, 2, 3], weights=[20, 3, 1])[0]
        tint = random.choice([
            (1.0, 1.0, 1.0), (1.0, 0.9, 0.7), (0.7, 0.85, 1.0), (1.0, 0.75, 0.75),
        ])
        sr = min(255, int(brightness * tint[0]))
        sg = min(255, int(brightness * tint[1]))
        sb = min(255, int(brightness * tint[2]))
        if size == 1:
            draw.point((sx, sy), fill=(sr, sg, sb))
        elif size == 2:
            draw.rectangle([sx, sy, sx + 1, sy + 1], fill=(sr, sg, sb))
        else:
            # Cross shape for bright stars
            draw.point((sx, sy), fill=(sr, sg, sb))
            for dp in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = sx + dp[0], sy + dp[1]
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    draw.point((nx, ny), fill=(sr // 2, sg // 2, sb // 2))

    # Rainbow letters - ERIK
    font = get_font("impact", 34)
    colors_top = [(255, 50, 50), (255, 220, 0), (50, 255, 50), (50, 180, 255)]
    letters_top = list("ERIK")
    spacing = 4
    total_w = sum(
        draw.textbbox((0, 0), c, font=font)[2] - draw.textbbox((0, 0), c, font=font)[0]
        for c in letters_top
    )
    total_w += spacing * (len(letters_top) - 1)
    cx = (SIZE - total_w) // 2
    for letter, color in zip(letters_top, colors_top):
        bbox = draw.textbbox((0, 0), letter, font=font)
        lw = bbox[2] - bbox[0]
        draw.text((cx + 2, 14), letter,
                  fill=(color[0] // 5, color[1] // 5, color[2] // 5), font=font)
        draw.text((cx, 12), letter, fill=color, font=font)
        cx += lw + spacing

    # Rainbow letters - SALO
    colors_bot = [(255, 100, 255), (0, 255, 200), (255, 150, 50), (150, 100, 255)]
    letters_bot = list("SALO")
    total_w2 = sum(
        draw.textbbox((0, 0), c, font=font)[2] - draw.textbbox((0, 0), c, font=font)[0]
        for c in letters_bot
    )
    total_w2 += spacing * (len(letters_bot) - 1)
    cx2 = (SIZE - total_w2) // 2
    for letter, color in zip(letters_bot, colors_bot):
        bbox = draw.textbbox((0, 0), letter, font=font)
        lw = bbox[2] - bbox[0]
        draw.text((cx2 + 2, 60), letter,
                  fill=(color[0] // 5, color[1] // 5, color[2] // 5), font=font)
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
# Screen 2: Art Deco Gold - sunburst, diamonds, gold shimmer
# ==============================================================================
def make_screen_gold():
    img = Image.new("RGB", (SIZE, SIZE), (25, 8, 40))
    draw = ImageDraw.Draw(img)

    # Rich purple gradient base
    for y in range(SIZE):
        r = int(30 + 15 * math.sin(y * 0.04))
        g = int(8 + 8 * math.sin(y * 0.04))
        b = int(50 + 20 * math.sin(y * 0.04))
        draw.line([(0, y), (SIZE - 1, y)], fill=(r, g, b))

    # Art deco sunburst rays from center
    mid_x, mid_y = SIZE // 2, SIZE // 2
    num_rays = 24
    for i in range(num_rays):
        angle = (i / num_rays) * 2 * math.pi
        if i % 2 == 0:
            color = (38, 14, 60)
        else:
            color = (22, 7, 38)
        a1 = angle - math.pi / num_rays * 0.85
        a2 = angle + math.pi / num_rays * 0.85
        far = 100
        x1 = mid_x + int(far * math.cos(a1))
        y1 = mid_y + int(far * math.sin(a1))
        x2 = mid_x + int(far * math.cos(a2))
        y2 = mid_y + int(far * math.sin(a2))
        draw.polygon([(mid_x, mid_y), (x1, y1), (x2, y2)], fill=color)

    # Concentric diamond shapes
    for sz in [52, 40, 28]:
        pts = [
            (mid_x, mid_y - sz), (mid_x + sz, mid_y),
            (mid_x, mid_y + sz), (mid_x - sz, mid_y),
        ]
        draw.polygon(pts, outline=(110, 80, 28))

    # Gold shimmer dots
    random.seed(99)
    for _ in range(50):
        sx = random.randint(10, SIZE - 10)
        sy = random.randint(10, SIZE - 10)
        b = random.randint(120, 210)
        draw.point((sx, sy), fill=(b, int(b * 0.78), int(b * 0.2)))

    # --- Ornamental frame and text (same content) ---
    gold = (255, 210, 60)
    gold_dim = (160, 130, 40)

    # Double border
    draw.rectangle([4, 4, 123, 123], outline=gold_dim, width=1)
    draw.rectangle([8, 8, 119, 119], outline=gold, width=2)

    # Corner flourishes
    for ccx, ccy in [(8, 8), (119, 8), (8, 119), (119, 119)]:
        draw.ellipse([ccx - 4, ccy - 4, ccx + 4, ccy + 4], fill=gold)
        draw.ellipse([ccx - 2, ccy - 2, ccx + 2, ccy + 2], fill=(255, 240, 150))

    # "Erik" in script font
    font_script = get_font("script", 40)
    draw_text_centered(draw, "Erik", 22, font_script, gold,
                       outline=(80, 50, 10), outline_width=2)

    # Decorative divider
    div_y = 68
    draw.line([(20, div_y), (108, div_y)], fill=gold_dim, width=1)
    draw.ellipse([58, div_y - 4, 70, div_y + 4], fill=gold)
    draw.ellipse([60, div_y - 2, 68, div_y + 2], fill=(255, 240, 150))
    for dx in [-25, 25]:
        draw.polygon([(64 + dx, div_y - 3), (64 + dx + 3, div_y),
                       (64 + dx, div_y + 3), (64 + dx - 3, div_y)], fill=gold)

    # "Salo" in script font
    draw_text_centered(draw, "Salo", 76, font_script, gold,
                       outline=(80, 50, 10), outline_width=2)

    return img


# ==============================================================================
# Screen 3: Matrix City - skyline silhouette with lit windows + rain
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

    # Pre-generate city skyline
    random.seed(456)
    buildings = []
    bx = 0
    while bx < SIZE:
        bw = random.randint(6, 16)
        bh = random.randint(18, 60)
        buildings.append((bx, bw, bh))
        bx += bw + random.randint(1, 4)

    font_small = get_font("regular", 10)
    font_name = get_font("bold", 30)

    for frame_idx in range(num_frames):
        img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        t = frame_idx

        # City skyline silhouette with flickering windows
        for bx, bw, bh in buildings:
            top = SIZE - bh
            # Building body (very dark green)
            draw.rectangle([bx, top, bx + bw, SIZE - 1], fill=(0, 8, 0))
            # Roof accent line
            draw.line([(bx, top), (bx + bw, top)], fill=(0, 25, 0))
            # Lit windows (flickering per frame)
            random.seed(frame_idx * 13 + bx * 7)
            for wy in range(top + 4, SIZE - 3, 6):
                for wx in range(bx + 2, bx + bw - 2, 4):
                    if random.random() > 0.4:
                        brightness = random.randint(18, 50)
                        draw.rectangle([wx, wy, wx + 1, wy + 2],
                                       fill=(0, brightness, 0))

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

        draw.rectangle([10, 30, 118, 62], fill=(0, 10, 0))
        draw.rectangle([10, 68, 118, 100], fill=(0, 10, 0))

        draw_text_centered(draw, "ERIK", 32, font_name, (bright, 255, bright),
                          outline=(0, 40, 0), outline_width=2)
        draw_text_centered(draw, "SALO", 70, font_name, (bright, 255, bright),
                          outline=(0, 40, 0), outline_width=2)

        frames.append(img)

    return frames


# ==============================================================================
# Screen 4: Volcanic Fire - smoke, rocky ground, lava cracks, embers
# ==============================================================================
def make_screen_fire(num_frames=10):
    # Pre-generate ember particles
    random.seed(8888)
    embers = [
        (random.randint(5, SIZE - 5), random.randint(0, SIZE - 1),
         random.uniform(1.5, 4.0), random.randint(160, 255))
        for _ in range(30)
    ]

    # Pre-generate rocky ground profile
    random.seed(555)
    ground_profile = [random.randint(88, 105) for _ in range(SIZE)]
    # Smooth it
    smoothed = ground_profile[:]
    for i in range(1, SIZE - 1):
        smoothed[i] = (ground_profile[i - 1] + ground_profile[i] + ground_profile[i + 1]) // 3
    ground_profile = smoothed

    # Pre-generate lava cracks
    random.seed(777)
    cracks = []
    for _ in range(5):
        cx = random.randint(8, SIZE - 8)
        cy = random.randint(95, 115)
        segs = []
        for _ in range(random.randint(4, 8)):
            nx = max(2, min(SIZE - 2, cx + random.randint(-8, 8)))
            ny = max(88, min(SIZE - 2, cy + random.randint(-4, 4)))
            segs.append((cx, cy, nx, ny))
            cx, cy = nx, ny
        cracks.append(segs)

    frames = []

    for frame_idx in range(num_frames):
        random.seed(frame_idx * 7 + 99)
        img = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fire gradient from bottom with smoke dampening at top
        for y in range(SIZE):
            for x in range(0, SIZE, 2):
                heat = max(0, (SIZE - y) / SIZE)
                noise = random.uniform(0.6, 1.0)
                flicker = 0.8 + 0.2 * math.sin(x * 0.3 + frame_idx * 1.2)
                intensity = heat * noise * flicker

                # Smoke dampening at top
                if y < 30:
                    smoke_fade = y / 30
                    intensity *= smoke_fade

                if intensity > 0.7:
                    r, g, b = 255, int(220 * intensity), int(80 * intensity)
                elif intensity > 0.4:
                    r, g, b = int(255 * intensity), int(130 * intensity), 0
                elif intensity > 0.15:
                    r, g, b = int(200 * intensity), int(50 * intensity), 0
                else:
                    r, g, b = int(80 * intensity), 0, 0

                # Smoky gray tint at top
                if y < 25:
                    smoke_t = (25 - y) / 25
                    r = min(255, r + int(30 * smoke_t * noise))
                    g = min(255, g + int(25 * smoke_t * noise))
                    b = min(255, b + int(22 * smoke_t * noise))

                r, g, b = min(255, r), min(255, g), min(255, b)
                draw.rectangle([x, y, x + 1, y], fill=(r, g, b))

        # Rocky ground silhouette
        for x in range(SIZE):
            gy = ground_profile[x]
            draw.line([(x, gy), (x, SIZE - 1)], fill=(22, 7, 2))

        # Ground texture dots
        random.seed(frame_idx + 5000)
        for _ in range(180):
            rx = random.randint(0, SIZE - 1)
            gy = ground_profile[rx]
            ry = random.randint(gy, SIZE - 1)
            v = random.randint(12, 38)
            draw.point((rx, ry), fill=(v, v // 4, 0))

        # Pulsing lava cracks
        crack_pulse = 0.6 + 0.4 * math.sin(frame_idx * 0.7)
        for crack in cracks:
            for cx1, cy1, cx2, cy2 in crack:
                cr = min(255, int(255 * crack_pulse))
                cg = min(255, int(100 * crack_pulse))
                draw.line([(cx1, cy1), (cx2, cy2)], fill=(cr, cg, 0), width=1)
                # Glow around crack
                draw.line([(cx1, cy1 - 1), (cx2, cy2 - 1)],
                          fill=(cr // 4, cg // 4, 0), width=1)
                draw.line([(cx1, cy1 + 1), (cx2, cy2 + 1)],
                          fill=(cr // 4, cg // 4, 0), width=1)

        # Floating embers drifting upward
        for ex, base_ey, speed, brightness in embers:
            ey = int(base_ey - frame_idx * speed) % SIZE
            # Only show embers above the ground
            if ey < ground_profile[min(ex, SIZE - 1)]:
                bright_mod = 0.6 + 0.4 * math.sin(frame_idx * 1.5 + ex * 0.3)
                er = min(255, int(brightness * bright_mod))
                eg = min(255, int(brightness * 0.4 * bright_mod))
                draw.point((ex, ey), fill=(er, eg, 0))
                # Small glow
                if er > 150:
                    for dp in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        gx, gy = ex + dp[0], ey + dp[1]
                        if 0 <= gx < SIZE and 0 <= gy < SIZE:
                            draw.point((gx, gy), fill=(er // 4, eg // 4, 0))

        # Name text
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
    print("\n[3] Screen 0: Synthwave Neon")
    img0 = make_screen_neon()
    img0.save("screen0_neon.png")
    send_to_screen(0, img0)
    time.sleep(0.5)

    print("\n[4] Screen 1: Cosmic Nebula Arcade")
    img1 = make_screen_arcade()
    img1.save("screen1_arcade.png")
    send_to_screen(1, img1)
    time.sleep(0.5)

    print("\n[5] Screen 2: Art Deco Gold")
    img2 = make_screen_gold()
    img2.save("screen2_gold.png")
    send_to_screen(2, img2)
    time.sleep(0.5)

    print("\n[6] Screen 3: Matrix City (animated)")
    frames3 = make_screen_matrix(num_frames=10)
    frames3[0].save("screen3_matrix.png")
    send_animation(3, frames3, speed_ms=300)
    time.sleep(0.5)

    print("\n[7] Screen 4: Volcanic Fire (animated)")
    frames4 = make_screen_fire(num_frames=10)
    frames4[0].save("screen4_fire.png")
    send_animation(4, frames4, speed_ms=250)

    print("\n" + "=" * 60)
    print("  All 5 screens updated!")
    print("  0: Synthwave Neon (retro sun + grid floor)")
    print("  1: Cosmic Nebula (gas clouds + starfield)")
    print("  2: Art Deco Gold (sunburst + diamonds)")
    print("  3: Matrix City (skyline + rain)")
    print("  4: Volcanic Fire (lava cracks + embers)")
    print("=" * 60)


if __name__ == "__main__":
    main()
