#!/usr/bin/env python3
"""Gravity Birds v1.5 — Moss Ledger art elevation (original, soft painted)."""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUT = Path("/workspace/gravity-birds-art/assets/art")
VFX = OUT / "vfx"
OUT.mkdir(parents=True, exist_ok=True)
VFX.mkdir(parents=True, exist_ok=True)

# Palette
SKY = (232, 223, 200, 255)
FOG = (197, 212, 184, 255)
MOSS = (95, 122, 74, 255)
MOSS_HI = (122, 154, 94, 255)
MOSS_SH = (62, 82, 50, 255)
BIRD = (74, 143, 168, 255)
BELLY = (217, 232, 238, 255)
BEAK = (224, 160, 74, 255)
EYE = (26, 26, 26, 255)
FRUIT = (224, 122, 42, 255)
LEAF = (95, 122, 74, 255)
EXIT_L = (138, 138, 122, 255)
EXIT_O = (111, 191, 106, 255)
SPIKE_I = (107, 58, 58, 255)
SPIKE_T = (196, 90, 74, 255)
VOID = (42, 46, 56, 255)
UI_P = (243, 234, 214, 255)
UI_B = (107, 90, 62, 255)
UI_T = (44, 36, 24, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def hex_rgba(h: str, a: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def new_rgba(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), TRANSPARENT)


def soft_ellipse(draw, xy, fill, outline=None, width=1):
    draw.ellipse(xy, fill=fill, outline=outline, width=width)


def paint_blob(img: Image.Image, cx, cy, rx, ry, color, blur=2.2, alpha=1.0):
    """Soft painted elliptical blob layered with blur."""
    layer = new_rgba(*img.size)
    d = ImageDraw.Draw(layer)
    c = list(color)
    if len(c) == 3:
        c.append(255)
    c[3] = int(c[3] * alpha)
    soft_ellipse(d, [cx - rx, cy - ry, cx + rx, cy + ry], tuple(c))
    if blur > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
    return Image.alpha_composite(img, layer)


def add_grain(img: Image.Image, amount: float = 0.08, seed: int = 42) -> Image.Image:
    rng = random.Random(seed)
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            n = int((rng.random() - 0.5) * 255 * amount)
            px[x, y] = (
                max(0, min(255, r + n)),
                max(0, min(255, g + n)),
                max(0, min(255, b + n)),
                a,
            )
    return img


def rounded_rect_mask(w, h, radius):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    return m


def tile_solid() -> Image.Image:
    img = new_rgba(64, 64)
    # moss block with soft rounded corners via blobs
    img = paint_blob(img, 32, 34, 28, 26, MOSS_SH, blur=1.5)
    img = paint_blob(img, 32, 30, 26, 24, MOSS, blur=1.8)
    img = paint_blob(img, 32, 18, 22, 10, MOSS_HI, blur=2.5, alpha=0.85)
    # moss speckles / lichen
    rng = random.Random(7)
    for _ in range(18):
        x, y = rng.randint(10, 54), rng.randint(14, 52)
        r = rng.uniform(1.2, 2.8)
        col = MOSS_HI if rng.random() > 0.5 else MOSS_SH
        img = paint_blob(img, x, y, r, r * 0.8, col, blur=1.0, alpha=0.55)
    # soft rim
    rim = new_rgba(64, 64)
    d = ImageDraw.Draw(rim)
    d.rounded_rectangle([4, 6, 59, 58], radius=12, outline=MOSS_SH[:3] + (90,), width=2)
    rim = rim.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img, rim)
    return add_grain(img, 0.07, seed=11)


def tile_empty() -> Image.Image:
    img = new_rgba(64, 64)
    # subtle parchment wash
    wash = new_rgba(64, 64)
    d = ImageDraw.Draw(wash)
    d.rectangle([0, 0, 63, 63], fill=SKY[:3] + (40,))
    wash = wash.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, wash)
    img = paint_blob(img, 32, 40, 30, 18, FOG[:3] + (35,), blur=4, alpha=1.0)
    # tiny grass tufts
    rng = random.Random(3)
    for i in range(5):
        x = 12 + i * 10 + rng.randint(-2, 2)
        y = 48 + rng.randint(-2, 2)
        img = paint_blob(img, x, y, 1.5, 4, MOSS_HI[:3] + (140,), blur=0.8)
        img = paint_blob(img, x + 2, y - 1, 1.2, 3.5, MOSS[:3] + (120,), blur=0.8)
    return add_grain(img, 0.04, seed=3)


def tile_void() -> Image.Image:
    img = new_rgba(64, 64)
    base = new_rgba(64, 64)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([2, 2, 61, 61], radius=10, fill=VOID)
    img = Image.alpha_composite(img, base)
    # vignette
    for i in range(8):
        a = int(40 + i * 12)
        img = paint_blob(img, 32, 32, 34 - i * 2, 34 - i * 2, (20, 22, 28, a), blur=2.5)
    # faint stars
    rng = random.Random(99)
    for _ in range(12):
        x, y = rng.randint(8, 56), rng.randint(8, 56)
        s = rng.uniform(0.6, 1.4)
        img = paint_blob(img, x, y, s, s, (220, 225, 240, 180), blur=0.6)
    return add_grain(img, 0.05, seed=99)


def tile_spike() -> Image.Image:
    img = new_rgba(64, 64)
    # base bar
    img = paint_blob(img, 32, 54, 26, 6, SPIKE_I, blur=1.2)
    img = paint_blob(img, 32, 52, 24, 4, (90, 48, 48, 255), blur=1.0)
    # three spikes pointing up
    pts = [(16, 50), (32, 50), (48, 50)]
    for cx, by in pts:
        spike = new_rgba(64, 64)
        d = ImageDraw.Draw(spike)
        tip_y = 10
        d.polygon(
            [(cx - 7, by), (cx + 7, by), (cx, tip_y)],
            fill=SPIKE_I,
        )
        spike = spike.filter(ImageFilter.GaussianBlur(0.8))
        img = Image.alpha_composite(img, spike)
        # tip gleam
        img = paint_blob(img, cx, tip_y + 6, 3, 5, SPIKE_T, blur=1.2, alpha=0.9)
        img = paint_blob(img, cx - 1, tip_y + 10, 2, 8, (140, 70, 60, 160), blur=1.0)
    return add_grain(img, 0.06, seed=21)


def bird_head() -> Image.Image:
    img = new_rgba(64, 64)
    # chubby head facing RIGHT
    img = paint_blob(img, 30, 34, 20, 18, BIRD, blur=1.6)
    img = paint_blob(img, 28, 30, 16, 12, (90, 160, 180, 200), blur=2.0, alpha=0.7)
    # belly patch under chin
    img = paint_blob(img, 28, 42, 12, 8, BELLY, blur=1.8, alpha=0.9)
    # beak pointing right
    beak = new_rgba(64, 64)
    d = ImageDraw.Draw(beak)
    d.polygon([(42, 30), (58, 34), (42, 40)], fill=BEAK)
    beak = beak.filter(ImageFilter.GaussianBlur(0.7))
    img = Image.alpha_composite(img, beak)
    img = paint_blob(img, 48, 33, 4, 2.5, (240, 190, 120, 200), blur=1.0)
    # eye
    img = paint_blob(img, 36, 28, 4.5, 4.5, WHITE[:3] + (240,), blur=0.5)
    img = paint_blob(img, 37, 28, 2.4, 2.4, EYE, blur=0.3)
    img = paint_blob(img, 38, 27, 0.9, 0.9, WHITE, blur=0.2)
    return add_grain(img, 0.05, seed=5)


def bird_body() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 34, 22, 20, BIRD, blur=1.8)
    img = paint_blob(img, 32, 28, 16, 10, (95, 165, 185, 180), blur=2.2)
    img = paint_blob(img, 32, 42, 14, 10, BELLY, blur=1.6, alpha=0.95)
    # soft side shading for chain readability
    img = paint_blob(img, 18, 34, 6, 14, MOSS_SH[:3] + (40,), blur=2.5, alpha=0.5)
    img = paint_blob(img, 46, 34, 6, 14, (255, 255, 255, 35), blur=2.5)
    return add_grain(img, 0.05, seed=6)


def bird_tail() -> Image.Image:
    img = new_rgba(64, 64)
    # body nub on right, feathers taper LEFT
    img = paint_blob(img, 40, 34, 14, 14, BIRD, blur=1.5)
    img = paint_blob(img, 40, 40, 9, 7, BELLY, blur=1.4, alpha=0.85)
    for i, (ox, oy, rx, ry) in enumerate([
        (22, 28, 12, 5),
        (18, 34, 14, 5),
        (22, 40, 12, 5),
    ]):
        col = BIRD if i != 1 else (60, 120, 145, 255)
        img = paint_blob(img, ox, oy, rx, ry, col, blur=1.2)
    img = paint_blob(img, 12, 34, 6, 3, (55, 110, 135, 200), blur=1.0)
    return add_grain(img, 0.05, seed=8)


def fruit() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 36, 18, 17, FRUIT, blur=1.6)
    img = paint_blob(img, 26, 28, 8, 6, (240, 160, 90, 200), blur=2.0)
    img = paint_blob(img, 38, 42, 7, 6, (180, 90, 30, 160), blur=1.8)
    # leaf
    leaf = new_rgba(64, 64)
    d = ImageDraw.Draw(leaf)
    d.ellipse([34, 12, 52, 28], fill=LEAF)
    leaf = leaf.filter(ImageFilter.GaussianBlur(0.9))
    img = Image.alpha_composite(img, leaf)
    img = paint_blob(img, 40, 18, 5, 3, MOSS_HI, blur=1.0, alpha=0.7)
    # stem
    img = paint_blob(img, 34, 16, 1.5, 4, MOSS_SH, blur=0.5)
    return add_grain(img, 0.06, seed=12)


def exit_locked() -> Image.Image:
    img = new_rgba(64, 64)
    # stone arch
    arch = new_rgba(64, 64)
    d = ImageDraw.Draw(arch)
    d.rounded_rectangle([10, 14, 54, 56], radius=8, fill=EXIT_L)
    d.ellipse([14, 10, 50, 42], fill=EXIT_L)
    # hollow
    d.rounded_rectangle([20, 28, 44, 56], radius=6, fill=(0, 0, 0, 0))
    # punch hole properly via mask
    arch = arch.filter(ImageFilter.GaussianBlur(0.5))
    img = Image.alpha_composite(img, arch)
    # cut opening
    cut = new_rgba(64, 64)
    cd = ImageDraw.Draw(cut)
    cd.rounded_rectangle([20, 30, 44, 58], radius=6, fill=(0, 0, 0, 255))
    # apply cut: clear those pixels
    px = img.load()
    cm = cut.load()
    for y in range(64):
        for x in range(64):
            if cm[x, y][3] > 128:
                px[x, y] = (0, 0, 0, 0)
    # rebuild with proper arch using layers
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 40, 22, 20, EXIT_L, blur=1.2)
    img = paint_blob(img, 32, 28, 20, 16, (150, 150, 135, 255), blur=1.5)
    # dark doorway
    door = new_rgba(64, 64)
    dd = ImageDraw.Draw(door)
    dd.ellipse([22, 26, 42, 50], fill=(60, 60, 55, 230))
    dd.rectangle([24, 36, 40, 56], fill=(60, 60, 55, 230))
    door = door.filter(ImageFilter.GaussianBlur(0.8))
    img = Image.alpha_composite(img, door)
    # padlock
    img = paint_blob(img, 32, 40, 7, 6, (90, 90, 80, 255), blur=0.8)
    img = paint_blob(img, 32, 34, 5, 5, TRANSPARENT, blur=0)
    lock = new_rgba(64, 64)
    ld = ImageDraw.Draw(lock)
    ld.arc([26, 28, 38, 40], 180, 0, fill=(70, 70, 65, 255), width=3)
    ld.rounded_rectangle([25, 36, 39, 48], radius=3, fill=(100, 95, 85, 255))
    ld.ellipse([30, 40, 34, 44], fill=(50, 50, 45, 255))
    lock = lock.filter(ImageFilter.GaussianBlur(0.4))
    img = Image.alpha_composite(img, lock)
    return add_grain(img, 0.06, seed=15)


def exit_open() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 40, 22, 20, EXIT_O, blur=1.2)
    img = paint_blob(img, 32, 28, 20, 16, (140, 210, 130, 255), blur=1.5)
    # glow core
    img = paint_blob(img, 32, 38, 12, 14, (200, 255, 190, 180), blur=3.0)
    img = paint_blob(img, 32, 38, 7, 9, (255, 255, 240, 200), blur=2.0)
    # arch rim highlight
    rim = new_rgba(64, 64)
    d = ImageDraw.Draw(rim)
    d.arc([12, 14, 52, 54], 200, 340, fill=(180, 230, 160, 180), width=3)
    rim = rim.filter(ImageFilter.GaussianBlur(1.0))
    img = Image.alpha_composite(img, rim)
    return add_grain(img, 0.05, seed=16)


def ui_panel() -> Image.Image:
    w, h = 256, 48
    img = new_rgba(w, h)
    base = new_rgba(w, h)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=UI_P)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=11, outline=UI_B, width=3)
    # inner soft highlight
    d.rounded_rectangle([4, 3, w - 5, 18], radius=8, fill=(255, 252, 240, 90))
    base = base.filter(ImageFilter.GaussianBlur(0.4))
    img = Image.alpha_composite(img, base)
    # wood grain hint
    rng = random.Random(40)
    grain = new_rgba(w, h)
    gd = ImageDraw.Draw(grain)
    for _ in range(30):
        y = rng.randint(6, h - 6)
        x0 = rng.randint(8, w - 40)
        gd.line([(x0, y), (x0 + rng.randint(20, 50), y)], fill=UI_B[:3] + (25,), width=1)
    grain = grain.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.alpha_composite(img, grain)
    return add_grain(img, 0.04, seed=40)


def ui_button() -> Image.Image:
    w, h = 96, 48
    img = new_rgba(w, h)
    base = new_rgba(w, h)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=UI_P)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=11, outline=UI_B, width=3)
    d.rounded_rectangle([4, 3, w - 5, 16], radius=8, fill=(255, 252, 240, 100))
    # bottom shadow edge
    d.rounded_rectangle([4, h - 12, w - 5, h - 4], radius=6, fill=UI_B[:3] + (35,))
    base = base.filter(ImageFilter.GaussianBlur(0.35))
    img = Image.alpha_composite(img, base)
    return add_grain(img, 0.04, seed=41)


def fruit_icon() -> Image.Image:
    img = new_rgba(28, 28)
    img = paint_blob(img, 14, 16, 9, 8, FRUIT, blur=0.9)
    img = paint_blob(img, 11, 12, 4, 3, (240, 160, 90, 200), blur=1.0)
    leaf = new_rgba(28, 28)
    d = ImageDraw.Draw(leaf)
    d.ellipse([14, 4, 24, 14], fill=LEAF)
    leaf = leaf.filter(ImageFilter.GaussianBlur(0.5))
    img = Image.alpha_composite(img, leaf)
    return add_grain(img, 0.05, seed=13)


# --- VFX ---

def vfx_move_dust() -> Image.Image:
    img = new_rgba(64, 64)
    rng = random.Random(50)
    for i in range(8):
        x = 20 + i * 4 + rng.randint(-3, 3)
        y = 48 - i * 2 + rng.randint(-2, 2)
        r = rng.uniform(2, 5)
        img = paint_blob(img, x, y, r, r * 0.6, FOG[:3] + (140,), blur=1.5, alpha=0.8)
        img = paint_blob(img, x + 2, y - 3, r * 0.5, r * 0.4, SKY[:3] + (100,), blur=1.2)
    return img


def vfx_fall_dust() -> Image.Image:
    img = new_rgba(64, 64)
    for i, (x, y, r) in enumerate([(20, 50, 6), (32, 52, 8), (44, 50, 6), (26, 44, 4), (38, 44, 4)]):
        img = paint_blob(img, x, y, r, r * 0.5, MOSS_SH[:3] + (120,), blur=2.0)
        img = paint_blob(img, x, y - 4, r * 0.7, r * 0.4, FOG[:3] + (100,), blur=1.8)
    return img


def vfx_fruit_burst() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 32, 8, 8, FRUIT[:3] + (200,), blur=2.0)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x = 32 + math.cos(rad) * 16
        y = 32 + math.sin(rad) * 16
        img = paint_blob(img, x, y, 4, 3, FRUIT[:3] + (180,), blur=1.5)
        img = paint_blob(img, 32 + math.cos(rad) * 22, 32 + math.sin(rad) * 22, 2.5, 2, (240, 180, 100, 150), blur=1.2)
    img = paint_blob(img, 32, 32, 4, 4, (255, 220, 160, 200), blur=1.5)
    return img


def vfx_grow_glow() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 32, 26, 26, BIRD[:3] + (60,), blur=6)
    img = paint_blob(img, 32, 32, 18, 18, (140, 200, 220, 100), blur=4)
    img = paint_blob(img, 32, 32, 10, 10, BELLY[:3] + (160,), blur=2.5)
    # soft ring
    ring = new_rgba(64, 64)
    d = ImageDraw.Draw(ring)
    d.ellipse([10, 10, 54, 54], outline=BIRD[:3] + (120,), width=3)
    ring = ring.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, ring)
    return img


def vfx_exit_unlock() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 32, 22, 22, EXIT_O[:3] + (80,), blur=5)
    img = paint_blob(img, 32, 32, 12, 12, (200, 255, 180, 160), blur=3)
    # sparkles
    for x, y in [(18, 20), (46, 22), (20, 44), (44, 42), (32, 14)]:
        img = paint_blob(img, x, y, 2, 2, WHITE[:3] + (200,), blur=0.8)
    # broken lock shards soft
    img = paint_blob(img, 24, 36, 3, 2, (180, 180, 150, 150), blur=1.0)
    img = paint_blob(img, 40, 38, 3, 2, (180, 180, 150, 150), blur=1.0)
    return img


def vfx_death_spike() -> Image.Image:
    img = new_rgba(64, 64)
    # red flash shards
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        x = 32 + math.cos(rad) * 14
        y = 32 + math.sin(rad) * 14
        img = paint_blob(img, x, y, 5, 2.5, SPIKE_T[:3] + (180,), blur=1.5)
    img = paint_blob(img, 32, 32, 10, 10, SPIKE_I[:3] + (140,), blur=3)
    img = paint_blob(img, 32, 28, 4, 6, SPIKE_T, blur=1.2)
    return img


def vfx_death_void() -> Image.Image:
    img = new_rgba(64, 64)
    img = paint_blob(img, 32, 32, 28, 28, VOID[:3] + (180,), blur=4)
    img = paint_blob(img, 32, 32, 16, 16, (20, 22, 30, 200), blur=3)
    # swirl fade dots
    for i in range(8):
        ang = i * 45 + 10
        rad = math.radians(ang)
        dist = 10 + i
        x = 32 + math.cos(rad) * dist
        y = 32 + math.sin(rad) * dist
        img = paint_blob(img, x, y, 3, 3, (100, 110, 140, 120), blur=1.5)
    return img


def vfx_undo_ghost() -> Image.Image:
    img = new_rgba(64, 64)
    # translucent bird-shaped ghost
    img = paint_blob(img, 32, 34, 18, 16, BIRD[:3] + (70,), blur=3)
    img = paint_blob(img, 32, 40, 10, 7, BELLY[:3] + (60,), blur=2.5)
    img = paint_blob(img, 40, 30, 5, 4, BIRD[:3] + (50,), blur=2)
    # soft outline
    ring = new_rgba(64, 64)
    d = ImageDraw.Draw(ring)
    d.ellipse([14, 16, 50, 52], outline=(200, 220, 230, 90), width=2)
    ring = ring.filter(ImageFilter.GaussianBlur(1.5))
    img = Image.alpha_composite(img, ring)
    return img


def vfx_win_flourish() -> Image.Image:
    """Soft glow rays — readable, not carnival confetti spam."""
    img = new_rgba(64, 64)
    # soft radial glow
    img = paint_blob(img, 32, 32, 28, 28, EXIT_O[:3] + (50,), blur=6)
    img = paint_blob(img, 32, 32, 14, 14, (220, 245, 200, 120), blur=3)
    img = paint_blob(img, 32, 32, 6, 6, (255, 255, 240, 180), blur=1.5)
    # soft rays (few, gentle)
    rays = new_rgba(64, 64)
    d = ImageDraw.Draw(rays)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x2 = 32 + math.cos(rad) * 28
        y2 = 32 + math.sin(rad) * 28
        d.line([(32, 32), (x2, y2)], fill=(180, 220, 150, 70), width=3)
    rays = rays.filter(ImageFilter.GaussianBlur(2.5))
    img = Image.alpha_composite(img, rays)
    # two soft sparkles only
    img = paint_blob(img, 18, 18, 2, 2, WHITE[:3] + (160,), blur=0.8)
    img = paint_blob(img, 46, 20, 2, 2, WHITE[:3] + (140,), blur=0.8)
    return img


def build_atlas(sprites: dict[str, Image.Image]) -> tuple[Image.Image, dict]:
    """Same layout as existing atlas.json."""
    order_row0 = ["tile_solid", "tile_empty", "tile_void", "tile_spike", "fruit"]
    order_row1 = ["exit_locked", "exit_open", "bird_head", "bird_body", "bird_tail"]
    atlas = new_rgba(320, 128)
    frames = {}
    for i, name in enumerate(order_row0):
        x, y = i * 64, 0
        atlas.paste(sprites[name], (x, y), sprites[name])
        frames[name] = {"x": x, "y": y, "w": 64, "h": 64}
    for i, name in enumerate(order_row1):
        x, y = i * 64, 64
        atlas.paste(sprites[name], (x, y), sprites[name])
        frames[name] = {"x": x, "y": y, "w": 64, "h": 64}
    meta = {"tile_size": 64, "frames": frames}
    return atlas, meta


def main():
    generators = {
        "tile_solid.png": tile_solid,
        "tile_void.png": tile_void,
        "tile_spike.png": tile_spike,
        "tile_empty.png": tile_empty,
        "bird_head.png": bird_head,
        "bird_body.png": bird_body,
        "bird_tail.png": bird_tail,
        "fruit.png": fruit,
        "exit_locked.png": exit_locked,
        "exit_open.png": exit_open,
        "ui_panel.png": ui_panel,
        "ui_button.png": ui_button,
        "fruit_icon.png": fruit_icon,
    }
    sprites = {}
    for name, fn in generators.items():
        im = fn()
        path = OUT / name
        im.save(path, "PNG")
        print(f"wrote {path} {im.size}")
        key = name.replace(".png", "")
        if key in {
            "tile_solid", "tile_empty", "tile_void", "tile_spike", "fruit",
            "exit_locked", "exit_open", "bird_head", "bird_body", "bird_tail",
        }:
            sprites[key] = im

    vfx_gens = {
        "vfx_move_dust.png": vfx_move_dust,
        "vfx_fall_dust.png": vfx_fall_dust,
        "vfx_fruit_burst.png": vfx_fruit_burst,
        "vfx_grow_glow.png": vfx_grow_glow,
        "vfx_exit_unlock.png": vfx_exit_unlock,
        "vfx_death_spike.png": vfx_death_spike,
        "vfx_death_void.png": vfx_death_void,
        "vfx_undo_ghost.png": vfx_undo_ghost,
        "vfx_win_flourish.png": vfx_win_flourish,
    }
    for name, fn in vfx_gens.items():
        im = fn()
        path = VFX / name
        im.save(path, "PNG")
        print(f"wrote {path} {im.size}")

    atlas, meta = build_atlas(sprites)
    atlas.save(OUT / "atlas.png", "PNG")
    import json
    (OUT / "atlas.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"wrote atlas {atlas.size}")


if __name__ == "__main__":
    main()
