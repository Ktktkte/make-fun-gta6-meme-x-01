#!/usr/bin/env python3
"""Compose the gta6-meme-x-01 meme: 'Sick Day' — GTA 6 launch-day sick day.

Flat vector-poster style, drawn fully in code with PIL:
Vice City sunset, convertible from behind with Jason & Lucia up front,
the make.fun ghost riding in the back seat holding its magenta coin,
and the caption "13 YEARS. ONE SICK DAY. WORTH IT."
Deterministic: no randomness, fixed coordinates.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 900
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def ghost_cut():
    """Cut the official ghost out of its magenta disc (assets/ghost.png).

    The mark is a white ghost + black outline on a solid magenta disc
    (#c41c83), holding a magenta coin with a white star. Keep every pixel
    that is not disc-magenta, plus the coin (same magenta, but inside its
    own circle), drop the disc and its black outer ring, and fade the
    alpha at the colour boundary so no magenta fringe survives.
    Returns the cut ghost as an RGBA image, saved to assets/ghost-cut.png.
    """
    src = Image.open("assets/ghost.png").convert("RGBA")
    arr = np.asarray(src).astype(np.float32)
    rgb = arr[:, :, :3]
    disc = np.array([196.0, 28.0, 131.0])
    dmag = np.sqrt(((rgb - disc) ** 2).sum(axis=2))
    yy, xx = np.mgrid[0:1024, 0:1024]
    # Measured in the PNG (not the SVG): the disc's black ring sits at
    # radius 420-472 from the centre, so a plain radius cut cannot work —
    # the ghost's hand reaches radius ~435. Cut the ring band out, but
    # spare the hand's wedge (angle ~22 deg, its centre (797, 627)) and
    # the coin's zone, where the ring reads as the coin's own outline.
    R = np.sqrt((xx - 512) ** 2 + (yy - 512) ** 2)
    ang = np.degrees(np.arctan2(yy - 512, xx - 512))
    dc = np.sqrt((xx - 848) ** 2 + (yy - 428) ** 2)
    ring_band = (R >= 418) & (R <= 476)
    hand_zone = (np.sqrt((xx - 797) ** 2 + (yy - 627) ** 2) < 135) & \
        (ang > -5) & (ang < 45)
    coin_zone = dc < 180
    ghost_zone = (R < 440) & (dmag > 80) & \
        ~(ring_band & ~hand_zone & ~coin_zone)
    # Coin: centre (26.5, 13.4)/32 -> (848, 428); magenta core r 3.8/32,
    # black ring out to r 5.5/32. Keep the core whole, the ring only where
    # the pixel is actually black, so no disc-magenta crescent survives.
    coin_core = dc < 122
    coin_ring = (dc >= 122) & (dc < 178) & (rgb.sum(axis=2) < 150)
    fade = np.clip((dmag - 20) / 60.0, 0, 1)
    alpha = np.zeros((1024, 1024))
    alpha[ghost_zone] = 255.0 * fade[ghost_zone]
    alpha[coin_core] = 255.0
    alpha[coin_ring] = 255.0
    out = np.dstack([arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], alpha])
    img = Image.fromarray(out.astype(np.uint8), "RGBA")
    img.save("assets/ghost-cut.png")
    return img


def font(size):
    return ImageFont.truetype(BOLD, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(img):
    d = ImageDraw.Draw(img)
    top = (43, 16, 66)       # deep dusk purple
    mid = (168, 44, 112)     # magenta dusk
    low = (255, 122, 61)     # sunset orange
    for y in range(0, 640):
        if y < 320:
            c = lerp(top, mid, y / 320)
        else:
            c = lerp(mid, low, (y - 320) / 320)
        d.line([(0, y), (W, y)], fill=c)


def sun(img, d):
    # soft glow + disc, low on the horizon, left of centre
    cx, cy, r = 470, 500, 150
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([cx - 205, cy - 205, cx + 205, cy + 205],
              fill=(255, 214, 130, 34))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"),
              (0, 0))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 233, 168))


def skyline(d):
    # dark tower silhouettes along the horizon, a few lit windows
    base = 640
    towers = [(0, 300, 90), (80, 250, 70), (150, 330, 110), (255, 270, 60),
              (700, 290, 100), (800, 240, 70), (875, 320, 120), (1000, 260, 80),
              (1085, 310, 115)]
    for x, top, w in towers:
        d.rectangle([x, base - top, x + w, base], fill=(38, 18, 64))
        # antenna on the tallest
        if top >= 320:
            d.line([x + w // 2, base - top, x + w // 2, base - top - 34],
                   fill=(38, 18, 64), width=4)
            d.ellipse([x + w // 2 - 4, base - top - 42, x + w // 2 + 4,
                       base - top - 34], fill=(255, 90, 120))
    # lit windows, fixed positions
    wins = [(30, 420), (95, 380), (180, 350), (290, 400), (730, 400),
            (830, 360), (910, 380), (1040, 400), (1120, 350)]
    for x, y in wins:
        d.rectangle([x, y, x + 10, y + 14], fill=(255, 214, 130))


def palm(d, x, base, h, lean, flip):
    # one palm silhouette: curved trunk + 6 fronds
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((x + lean * t * t * 40, base - h * t))
    d.line(pts, fill=(24, 10, 40), width=14)
    tx, ty = pts[-1]
    # fronds: drooping arcs, fanning out from the crown
    for k in range(7):
        base_ang = -18 - k * 24
        ang = math.radians(base_ang if not flip else 180 - base_ang)
        length = 120 - abs(k - 3) * 10
        frond = []
        for i in range(13):
            t = i / 12
            fx = tx + math.cos(ang) * length * t
            fy = ty + math.sin(ang) * length * t + 52 * t * t
            frond.append((fx, fy))
        d.line(frond, fill=(24, 10, 40), width=8)
    # coconuts
    d.ellipse([tx - 16, ty + 2, tx - 2, ty + 16], fill=(24, 10, 40))
    d.ellipse([tx + 2, ty + 4, tx + 16, ty + 18], fill=(24, 10, 40))


def birds(d):
    for x, y, s in ((820, 150, 16), (880, 120, 12), (930, 165, 14),
                    (300, 130, 13), (250, 170, 11)):
        d.arc([x - s, y - s // 2, x, y + s // 2], 200, 340,
              fill=(30, 12, 48), width=4)
        d.arc([x, y - s // 2, x + s, y + s // 2], 200, 340,
              fill=(30, 12, 48), width=4)


def road(d):
    d.rectangle([0, 640, W, H], fill=(26, 14, 44))
    # centre dashes, widening toward the viewer (stop above the caption)
    y = 660
    while y < 772:
        wdt = 6 + (y - 660) // 26
        d.polygon([(600 - wdt, y), (600 + wdt, y),
                   (600 + wdt + 10, y + 26), (600 - wdt - 10, y + 26)],
                  fill=(255, 214, 130))
        y += 52
    # warm sunset reflection on the asphalt
    d.rectangle([0, 640, W, 652], fill=(255, 122, 61))


def convertible(d):
    # rear view of a convertible, flat poster style, centred
    # body
    d.rounded_rectangle([300, 560, 900, 700], radius=42, fill=(16, 92, 96))
    d.rounded_rectangle([300, 560, 900, 612], radius=42, fill=(24, 122, 126))
    d.rectangle([300, 600, 900, 612], fill=(24, 122, 126))
    # rear window / cabin opening
    d.rounded_rectangle([360, 470, 840, 566], radius=26, fill=(10, 30, 52))
    # seats (headrests)
    d.rounded_rectangle([392, 500, 478, 566], radius=16, fill=(48, 16, 64))
    d.rounded_rectangle([722, 500, 808, 566], radius=16, fill=(48, 16, 64))
    # Jason (left, cap) and Lucia (right, long hair) — heads above headrests
    d.ellipse([408, 452, 462, 508], fill=(232, 184, 148))          # Jason head
    d.pieslice([404, 440, 466, 486], 180, 360, fill=(24, 24, 30))  # cap
    d.rectangle([400, 462, 470, 474], fill=(24, 24, 30))           # cap brim
    d.ellipse([738, 452, 792, 508], fill=(214, 164, 128))          # Lucia head
    d.pieslice([732, 440, 798, 500], 180, 360, fill=(58, 30, 20))  # hair
    d.rectangle([732, 470, 742, 512], fill=(58, 30, 20))           # hair left
    d.rectangle([788, 470, 798, 512], fill=(58, 30, 20))           # hair right
    # tail lights
    d.rounded_rectangle([322, 640, 420, 668], radius=10, fill=(255, 64, 96))
    d.rounded_rectangle([780, 640, 878, 668], radius=10, fill=(255, 64, 96))
    # bumper + plate
    d.rounded_rectangle([300, 676, 900, 700], radius=18, fill=(12, 58, 62))
    d.rounded_rectangle([520, 640, 680, 676], radius=6, fill=(245, 245, 240))
    pf = font(26)
    d.text((600, 658), "MAKEFUN", font=pf, fill=(20, 20, 26), anchor="mm")
    # wheels
    d.ellipse([336, 664, 416, 710], fill=(14, 14, 18))
    d.ellipse([784, 664, 864, 710], fill=(14, 14, 18))
    # magenta underglow
    d.rounded_rectangle([330, 700, 870, 714], radius=8, fill=(255, 0, 110))


def caption(d, text, y, size):
    f = font(size)
    d.text((W // 2, y), text, font=f, fill=(255, 255, 255),
           anchor="ma", stroke_width=max(3, size // 14), stroke_fill=(20, 8, 32))


def main():
    img = Image.new("RGB", (W, H))
    sky(img)
    d = ImageDraw.Draw(img)
    sun(img, d)
    skyline(d)
    birds(d)
    palm(d, 60, 660, 300, -1, False)
    palm(d, 1150, 660, 260, 1, True)
    road(d)
    convertible(d)
    # the make.fun ghost, cut out of its disc, riding in the back seat
    # between Jason and Lucia — a passenger, not a sticker
    ghost = ghost_cut().resize((270, 270), Image.LANCZOS)
    img.paste(ghost, (465, 356), ghost)
    d = ImageDraw.Draw(img)
    caption(d, "13 YEARS.", 36, 118)
    caption(d, "ONE SICK DAY. WORTH IT.", 786, 74)
    img.save("meme.png")
    print("saved meme.png", img.size)


if __name__ == "__main__":
    main()
