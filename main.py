#!/usr/bin/env python3
"""The World - 23 November 2026.

A newspaper-style front page that sums up Monday 23 November 2026 in one
image. Pure Python 3.13 standard library only: the PNG is encoded by hand
with zlib, the type is a small 5x7 bitmap font drawn by this program, and
every illustration is drawn from vector shapes. No network, no files read,
no randomness, no time: two runs produce byte-identical output.

Run:  python3 main.py            (writes out/entry.png)
      MAKEFUN_OUTPUT_DIR=/x python3 main.py   (writes /x/entry.png)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (26, 26, 26)
NAVY = (30, 58, 95)
NAVY_DARK = (20, 40, 68)
RED = (185, 28, 28)
BLUE = (37, 99, 235)
GREEN = (34, 139, 60)
GOLD = (201, 162, 39)
ORANGE = (234, 88, 12)
GREY = (110, 110, 105)
LIGHT = (232, 226, 210)
WHITE = (255, 255, 255)
SKY = (176, 208, 232)
SEA = (44, 110, 160)

# ------------------------------------------------------------------- font
# 5x7 bitmap font. '#' is an ink pixel, '.' is empty.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#.###"),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(s, scale):
    """Pixel width of s at the given scale (5 px per glyph + 1 px gap)."""
    return len(s) * 6 * scale - scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                elif abs(d2 - r * r) <= r:
                    self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c, fill=True):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                v = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
                if fill and v <= 1.0:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        # Filled polygon by scanline fill.
        ys = sorted({p[1] for p in pts})
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    def star(self, cx, cy, r_out, r_in, points, c):
        import math
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi * i / points - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def text(self, x, y, s, scale, c):
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT[' '])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == '#':
                        self.rect(x + col * scale, y + row * scale,
                                  scale, scale, c)
            x += 6 * scale
        return x

    def text_centred(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def para(self, x, y, s, max_w, scale, c, leading=None):
        if leading is None:
            leading = 9 * scale
        for line in wrap_text(s, max_w, scale):
            self.text(x, y, line, scale, c)
            y += leading
        return y


# -------------------------------------------------------------- illustrations
def draw_globe(cv, x, y, s):
    """Earth with a red crack: the climate talks broke apart."""
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 6
    cv.circle(cx, cy, r, NAVY, fill=True)
    cv.circle(cx, cy, r, INK)
    # continents
    cv.ellipse(cx - r // 2, cy - r // 3, r // 3, r // 5, GREEN)
    cv.ellipse(cx + r // 3, cy + r // 6, r // 4, r // 5, GREEN)
    cv.ellipse(cx - r // 5, cy + r // 2, r // 5, r // 6, GREEN)
    cv.ellipse(cx + r // 2, cy - r // 2, r // 6, r // 6, GREEN)
    # crack zigzag across the globe
    pts = [(cx - r + 8, cy - r // 3), (cx - r // 2, cy),
           (cx - r // 6, cy - r // 4), (cx + r // 6, cy + r // 4),
           (cx + r // 2, cy), (cx + r - 8, cy + r // 3)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)
    # smoke from a factory at the foot of the globe
    cv.rect(cx - r // 2, cy + r - 2, 14, 16, GREY)
    cv.rect(cx - r // 2 + 18, cy + r - 2, 10, 12, GREY)
    cv.circle(cx - r // 2 + 7, cy + r - 10, 6, GREY, fill=True)
    cv.circle(cx - r // 2 + 24, cy + r - 8, 5, GREY, fill=True)


def draw_tanker(cv, x, y, w, h):
    """Oil tanker on fire in a strait."""
    cv.rect(x, y, w, h, SKY)
    # sea
    for k in range(3):
        yy = y + h - 26 + k * 8
        for xx in range(x, x + w, 16):
            cv.line(xx, yy, xx + 8, yy - 4, SEA, 2)
            cv.line(xx + 8, yy - 4, xx + 16, yy, SEA, 2)
    # hull and deck
    cv.rect(x + 18, y + h - 62, w - 36, 26, INK)
    cv.rect(x + 18, y + h - 62, w - 36, 6, RED)
    cv.rect(x + 30, y + h - 88, 26, 26, ORANGE)
    cv.rect(x + 62, y + h - 88, 26, 26, GOLD)
    cv.rect(x + 94, y + h - 88, 26, 26, ORANGE)
    # flames
    for fx, fh in ((x + 130, 34), (x + 150, 48), (x + 172, 30)):
        cv.poly([(fx, y + h - 62), (fx + 12, y + h - 62 - fh),
                 (fx + 24, y + h - 62)], ORANGE)
        cv.poly([(fx + 5, y + h - 62), (fx + 12, y + h - 62 - fh + 12),
                 (fx + 19, y + h - 62)], RED)
    # smoke
    cv.circle(x + 150, y + 18, 9, GREY, fill=True)
    cv.circle(x + 170, y + 10, 7, GREY, fill=True)


def draw_kyiv(cv, x, y, w, h):
    """City skyline, a drone above it, a blast star."""
    cv.rect(x, y, w, h, SKY)
    # skyline
    heights = (52, 78, 44, 66, 90, 58, 40)
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw + 4
        cv.rect(bx, y + h - 30 - hh, bw - 8, hh, NAVY_DARK)
        for wy in range(y + h - 30 - hh + 8, y + h - 34, 14):
            for wx in (bx + 4, bx + bw - 12):
                cv.rect(wx, wy, 4, 5, GOLD)
    cv.rect(x, y + h - 30, w, 30, LIGHT)
    # drone: body + four rotors
    dx, dy = x + w - 66, y + 34
    cv.rect(dx - 16, dy - 6, 32, 12, INK)
    for ox, oy in ((-22, -12), (22, -12), (-22, 10), (22, 10)):
        cv.line(dx + ox - 8, dy + oy, dx + ox + 8, dy + oy, INK, 2)
        cv.line(dx + ox, dy + oy - 2, dx + ox, dy + oy + 2, INK, 2)
    cv.line(dx - 16, dy - 6, dx - 22, dy - 12, INK, 2)
    cv.line(dx + 16, dy - 6, dx + 22, dy - 12, INK, 2)
    cv.line(dx - 16, dy + 6, dx - 22, dy + 10, INK, 2)
    cv.line(dx + 16, dy + 6, dx + 22, dy + 10, INK, 2)
    # blast star over a rooftop
    bx, by = x + 66, y + h - 62
    cv.star(bx, by, 26, 11, 8, ORANGE)
    cv.star(bx, by, 14, 6, 8, RED)


def draw_capture(cv, x, y, w, h):
    """A gold badge and handcuffs: a cartel boss is caught."""
    cv.rect(x, y, w, h, LIGHT)
    # badge
    cv.star(x + w // 2, y + h // 2 - 8, 46, 20, 5, GOLD)
    cv.circle(x + w // 2, y + h // 2 - 8, 20, NAVY, fill=True)
    cv.circle(x + w // 2, y + h // 2 - 8, 20, INK)
    cv.text_centred(x + w // 2, y + h // 2 - 18, "*", 2, GOLD)
    # handcuffs
    cv.circle(x + 52, y + h - 34, 13, INK)
    cv.circle(x + 52, y + h - 34, 8, LIGHT, fill=True)
    cv.circle(x + w - 52, y + h - 34, 13, INK)
    cv.circle(x + w - 52, y + h - 34, 8, LIGHT, fill=True)
    cv.line(x + 52, y + h - 34, x + w - 52, y + h - 34, INK, 3)


def draw_capitol(cv, x, y, w, h):
    """Capitol dome with a ballot box and a check mark."""
    cv.rect(x, y, w, h, SKY)
    # dome
    cx = x + w // 2
    cv.ellipse(cx, y + h - 44, 58, 40, WHITE)
    cv.rect(cx - 58, y + h - 44, 116, 44, WHITE)
    cv.rect(cx - 58, y + h - 44, 116, 4, INK)
    cv.rect(cx - 3, y + h - 96, 6, 12, INK)
    cv.circle(cx, y + h - 98, 4, GOLD, fill=True)
    for i in range(5):
        cv.vline(cx - 44 + i * 22, y + h - 40, 36, INK, 2)
    cv.rect(x, y + h - 8, w, 8, INK)
    # ballot box with a tick
    bx, by = x + w - 74, y + h - 44
    cv.rect(bx, by, 44, 34, NAVY)
    cv.rect(bx, by, 44, 8, GOLD)
    cv.line(bx + 8, by + 20, bx + 17, by + 28, WHITE, 3)
    cv.line(bx + 17, by + 28, bx + 36, by + 8, WHITE, 3)
    # paper slip going in
    cv.line(bx + 22, by - 12, bx + 22, by, INK, 2)


# ------------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead
    cv.rect(16, 16, 992, 118, NAVY)
    cv.rect(16, 16, 992, 4, GOLD)
    cv.rect(16, 130, 992, 4, GOLD)
    cv.text_centred(512, 30, "THE WORLD", 8, WHITE)
    cv.text_centred(512, 100, "MONDAY 23 NOVEMBER 2026", 2, WHITE)
    cv.text(28, 100, "NO. 327", 2, GOLD)
    cv.text(1024 - 28 - text_width("PRICE: ONE IMAGE", 2), 100,
            "PRICE: ONE IMAGE", 2, GOLD)

    # ---- lead story: COP31
    cv.rect(16, 148, 992, 248, WHITE)
    cv.rect(16, 148, 992, 248, INK)  # border via outline below
    cv.rect(18, 150, 988, 244, WHITE)
    draw_globe(cv, 34, 168, 200)
    tx = 262
    cv.text(tx, 168, "CLIMATE SUMMIT", 2, RED)
    cv.text(tx, 196, "COP31 COLLAPSES", 5, INK)
    cv.text(tx, 244, "NO DEAL ON FOSSIL FUELS", 3, NAVY)
    cv.para(tx, 282, "After two weeks in Antalya, the longest climate "
            "talks in history end with no agreement. The EU and island "
            "states reject a pact that never mentions fossil fuels.",
            992 - tx - 14, 2, INK)
    cv.text(tx, 372, "ANTALYA, TURKEY", 2, GREY)

    # ---- story panels (2 x 2)
    panels = [
        (16, 408, "WAR AT SEA", "TANKERS ABLAZE IN HORMUZ",
         "Iran's navy says it set fire to tankers breaking its rules. "
         "An Iranian strike wounds two in Bahrain.", draw_tanker),
        (524, 408, "UKRAINE", "DRONE HITS KYIV FLATS",
         "At least 14 people are missing after a Russian drone hits a "
         "residential building in the Kyiv region.", draw_kyiv),
        (524, 648, "MEXICO", "EL CHAPO ISIDRO CAUGHT",
         "Mexico captures the FBI's most-wanted cartel boss after gun "
         "battles in Sinaloa leave 11 dead.", draw_capture),
        (16, 648, "UNITED STATES", "DEMOCRATS TAKE THE HOUSE",
         "Democrats clinch a historic House majority of at least 258 "
         "seats, the largest since 1992.", draw_capitol),
    ]
    # order: row 1 = Hormuz, Kyiv; row 2 = Mexico, US House
    panels = [panels[0], panels[1], panels[2], panels[3]]
    for (px, py, kicker, head, cap, draw) in panels:
        pw = 484
        cv.rect(px, py, pw, 228, WHITE)
        cv.rect(px, py, pw, 228, INK)
        cv.rect(px + 2, py + 2, pw - 4, 224, WHITE)
        draw(cv, px + 14, py + 12, pw - 28, 96)
        cv.text(px + 14, py + 118, kicker, 2, RED)
        cv.text(px + 14, py + 140, head, 3, INK)
        cv.para(px + 14, py + 172, cap, pw - 28, 2, INK)

    # ---- bottom strip: also in the world
    cv.rect(16, 888, 992, 120, NAVY)
    cv.text(30, 902, "ALSO IN THE WORLD", 2, GOLD)
    cv.para(30, 930, "SEOUL: South Korea's education minister resigns "
            "over an AI exam-cheating scandal.  INDONESIA: Factory fire "
            "kills 7; dozens of workers still missing.",
            992 - 28, 2, WHITE)

    return cv


# -------------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
