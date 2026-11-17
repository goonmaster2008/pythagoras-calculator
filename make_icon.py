"""Generate the app icon (assets/pythagoras.ico) with Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 256
BG = "#0F172A"
EDGE = "#334155"
BLUE = "#38BDF8"
MUTED = "#94A3B8"

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Rounded dark tile
d.rounded_rectangle((8, 8, SIZE - 8, SIZE - 8), radius=52, fill=BG, outline=EDGE, width=6)

# Right triangle
p1, p2, p3 = (64, 192), (64, 72), (196, 192)
d.line([p1, p2, p3, p1], fill=BLUE, width=15, joint="curve")
for p in (p1, p2, p3):
    d.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), fill=BLUE)

# Right-angle marker
d.line([(64, 158), (98, 158), (98, 192)], fill=MUTED, width=7)

out = Path(__file__).with_name("assets") / "pythagoras.ico"
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(f"wrote {out}")
