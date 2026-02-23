"""Generate a combined preview image for the README."""
from PIL import Image

imgs = [
    Image.open(f"screen{i}_{name}.png")
    for i, name in enumerate(["neon", "arcade", "gold", "matrix", "fire"])
]

# Scale each up to 200x200 for visibility, arrange horizontally with gaps
scale = 200
gap = 10
total_w = scale * 5 + gap * 4
combined = Image.new("RGB", (total_w, scale), (24, 24, 24))

for i, img in enumerate(imgs):
    resized = img.resize((scale, scale), Image.NEAREST)
    combined.paste(resized, (i * (scale + gap), 0))

combined.save("screenshots/preview.png")
print("Created screenshots/preview.png")
