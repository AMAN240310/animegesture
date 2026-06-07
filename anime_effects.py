# ============================================================
# effects/anime_effects.py
# Six distinct anime-style visual effects, each triggered
# by a different gesture.
# ============================================================

import cv2
import numpy as np
import math
import random
from config import COLORS, GLOW_BLUR_KERNEL


# ─── Utility helpers ─────────────────────────────────────────

def _add_glow(frame: np.ndarray, overlay: np.ndarray,
              strength: float = 1.4, kernel: int = GLOW_BLUR_KERNEL) -> np.ndarray:
    """Blur overlay and additive-blend onto frame."""
    k = kernel if kernel % 2 == 1 else kernel + 1
    blurred = cv2.GaussianBlur(overlay, (k, k), 0)
    return cv2.addWeighted(frame, 1.0, blurred, strength, 0)


def _draw_lightning_bolt(canvas: np.ndarray, x1, y1, x2, y2,
                          color, width=2, branches=4, depth=3):
    """Recursive fractal lightning bolt."""
    if depth == 0:
        cv2.line(canvas, (int(x1), int(y1)), (int(x2), int(y2)), color, width, cv2.LINE_AA)
        return
    mx = (x1 + x2) / 2 + random.uniform(-40, 40)
    my = (y1 + y2) / 2 + random.uniform(-40, 40)
    _draw_lightning_bolt(canvas, x1, y1, mx, my, color, width, 0, depth - 1)
    _draw_lightning_bolt(canvas, mx, my, x2, y2, color, width, 0, depth - 1)
    if branches > 0 and random.random() < 0.6:
        bx = mx + random.uniform(-60, 60)
        by = my + random.uniform(20, 80)
        _draw_lightning_bolt(canvas, mx, my, bx, by, color, max(1, width - 1), 0, depth - 1)


def _polar_to_xy(cx, cy, r, theta):
    return (int(cx + r * math.cos(theta)),
            int(cy + r * math.sin(theta)))


# ─── Effect 1 — Energy Aura (Open Palm) ──────────────────────

class AuraEffect:
    """
    Pulsing golden/white energy rings around the hand — Naruto chakra mode.
    """

    def __init__(self):
        self.frame_count = 0

    def render(self, frame: np.ndarray, hand: dict, particles) -> np.ndarray:
        cx, cy   = hand["palm_center"]
        t        = self.frame_count * 0.12
        palette  = COLORS["aura"]
        overlay  = np.zeros_like(frame)

        # Emit upward-streaming particles from each fingertip
        tips = [4, 8, 12, 16, 20]
        for tip in tips:
            tx, ty = hand["landmarks_px"][tip]
            particles.emit(tx, ty, count=4, palette=palette,
                           style="stream", speed=5.0, gravity=-0.1,
                           size_range=(2, 7), lifespan=35)

        # Concentric pulsing rings
        num_rings = 4
        for i in range(num_rings):
            phase  = t + i * (math.pi / 2)
            radius = int(55 + i * 28 + math.sin(phase) * 15)
            alpha  = int(160 + math.sin(phase) * 80)
            col    = palette[i % len(palette)]
            cv2.circle(overlay, (cx, cy), radius, col, 2, cv2.LINE_AA)

        # Rotating energy triangle
        for j in range(3):
            angle = t * 1.5 + j * (2 * math.pi / 3)
            r     = 70 + math.sin(t * 2) * 15
            px, py = _polar_to_xy(cx, cy, r, angle)
            cv2.circle(overlay, (px, py), 8, palette[0], -1, cv2.LINE_AA)

        # Central core glow
        cv2.circle(overlay, (cx, cy), 20, (255, 255, 220), -1, cv2.LINE_AA)

        self.frame_count += 1
        result = _add_glow(frame, overlay, strength=1.8)
        return cv2.addWeighted(result, 1.0, overlay, 0.6, 0)


# ─── Effect 2 — Fire Burst (Fist) ────────────────────────────

class FireEffect:
    """
    Rising fire columns from the fist — Dragon Ball Kaioken.
    """

    def __init__(self):
        self.frame_count = 0

    def render(self, frame: np.ndarray, hand: dict, particles) -> np.ndarray:
        cx, cy  = hand["palm_center"]
        palette = COLORS["fire"]
        bbox    = hand["bbox"]
        w_box   = bbox[2] - bbox[0]

        # Burst from fist knuckles
        knuckles = [5, 9, 13, 17]
        for k in knuckles:
            kx, ky = hand["landmarks_px"][k]
            particles.emit(kx, ky, count=8, palette=palette,
                           style="stream", speed=7.0, gravity=-0.3,
                           size_range=(4, 12), lifespan=40)

        # Expanding fire ring on fist clench
        overlay = np.zeros_like(frame)
        t       = self.frame_count
        ring_r  = int(60 + (t % 20) * 4)
        ring_a  = max(0, 200 - (t % 20) * 10)
        cv2.circle(overlay, (cx, cy), ring_r,
                   (0, int(ring_a * 0.5), ring_a), 3, cv2.LINE_AA)

        # Vertical fire column
        for i in range(8):
            yy = cy - i * 18 - (self.frame_count * 3 % 18)
            intensity = max(0, 1.0 - i * 0.12)
            col = (0, int(60 * intensity), int(255 * intensity))
            cv2.circle(overlay, (cx, yy), max(1, int(18 * intensity)), col, -1, cv2.LINE_AA)

        self.frame_count += 1
        result = _add_glow(frame, overlay, strength=2.0)
        return cv2.addWeighted(result, 1.0, overlay, 0.7, 0)


# ─── Effect 3 — Lightning Strike (Thumbs Up) ─────────────────

class LightningEffect:
    """
    Crackling lightning bolts from the sky — Sasuke Chidori.
    """

    def __init__(self):
        self.frame_count  = 0
        self.bolt_timer   = 0

    def render(self, frame: np.ndarray, hand: dict, particles) -> np.ndarray:
        cx, cy   = hand["palm_center"]
        palette  = COLORS["lightning"]
        overlay  = np.zeros_like(frame)
        h, w     = frame.shape[:2]
        thumb_tip = hand["landmarks_px"][4]

        # Emit sparks from thumb tip
        particles.emit(thumb_tip[0], thumb_tip[1], count=6, palette=palette,
                       style="burst", speed=8.0, gravity=0.2,
                       size_range=(2, 6), lifespan=25)

        # Primary bolt from top of screen to thumb
        if self.bolt_timer % 3 == 0:   # new bolt every 3 frames
            _draw_lightning_bolt(overlay,
                                 cx + random.randint(-30, 30), 0,
                                 thumb_tip[0], thumb_tip[1],
                                 (200, 200, 255), width=3, depth=4)

        # Secondary ambient bolts
        if self.frame_count % 5 == 0:
            sx = random.randint(cx - 100, cx + 100)
            _draw_lightning_bolt(overlay, sx, 0, cx, cy,
                                 (100, 100, 200), width=1, depth=3)

        # Electric circle at palm
        for ring in range(3):
            r = 30 + ring * 20 + random.randint(-5, 5)
            cv2.circle(overlay, (cx, cy), r,
                       (220, 220, 255), 1, cv2.LINE_AA)

        self.frame_count += 1
        self.bolt_timer  += 1
        result = _add_glow(frame, overlay, strength=2.5, kernel=21)
        return cv2.addWeighted(result, 1.0, overlay, 0.9, 0)


# ─── Effect 4 — Spirit Summon (Peace Sign) ───────────────────

class PeaceEffect:
    """
    Spiral summoning circle + emerald energy beams — Jujutsu Kaisen domain.
    """

    def __init__(self):
        self.frame_count = 0

    def render(self, frame: np.ndarray, hand: dict, particles) -> np.ndarray:
        cx, cy   = hand["palm_center"]
        palette  = COLORS["peace"]
        overlay  = np.zeros_like(frame)
        t        = self.frame_count * 0.1

        # Emit from index + middle fingertips
        for tip in [8, 12]:
            tx, ty = hand["landmarks_px"][tip]
            particles.emit(tx, ty, count=5, palette=palette,
                           style="orbit", speed=4.0, gravity=-0.05,
                           size_range=(3, 8), lifespan=45)

        # Rotating summoning circle (concentric rings + rotating markers)
        radii = [40, 65, 90]
        for r in radii:
            cv2.circle(overlay, (cx, cy), r, palette[1], 1, cv2.LINE_AA)

        num_marks = 8
        for i in range(num_marks):
            angle  = t * 2 + i * (2 * math.pi / num_marks)
            px, py = _polar_to_xy(cx, cy, radii[-1] - 5, angle)
            cv2.circle(overlay, (px, py), 4, palette[0], -1, cv2.LINE_AA)

        # Rotating inner cross
        for i in range(4):
            angle  = t + i * (math.pi / 2)
            px, py = _polar_to_xy(cx, cy, radii[1], angle)
            cv2.line(overlay, (cx, cy), (px, py), palette[2], 1, cv2.LINE_AA)

        # Central flash
        flash_r = int(10 + math.sin(t * 3) * 8)
        cv2.circle(overlay, (cx, cy), flash_r, (255, 255, 255), -1, cv2.LINE_AA)

        self.frame_count += 1
        result = _add_glow(frame, overlay, strength=2.0)
        return cv2.addWeighted(result, 1.0, overlay, 0.8, 0)


# ─── Effect 5 — Cursed Energy (Pointing) ─────────────────────

class CurseEffect:
    """
    Purple cursed energy beam from index finger — Gojo Satoru.
    """

    def __init__(self):
        self.frame_count = 0

    def render(self, frame: np.ndarray, hand: dict, particles) -> np.ndarray:
        h, w    = frame.shape[:2]
        palette = COLORS["curse"]
        overlay = np.zeros_like(frame)

        # Direction: wrist → index tip
        wrist = hand["landmarks_px"][0].astype(float)
        tip   = hand["landmarks_px"][8].astype(float)
        direction = tip - wrist
        length    = np.linalg.norm(direction)
        if length < 1:
            return frame
        direction /= length

        # Extend beam across screen
        beam_end = tip + direction * max(w, h)
        bx, by   = int(beam_end[0]), int(beam_end[1])
        tx, ty   = int(tip[0]), int(tip[1])

        # Beam layers (thick → thin, outer → inner)
        beam_layers = [
            (20, (60, 0, 80),    0.3),
            (12, (120, 0, 160),  0.6),
            (6,  (180, 0, 230),  0.8),
            (2,  (255, 200, 255), 1.0),
        ]
        for thickness, col, alpha_mult in beam_layers:
            cv2.line(overlay, (tx, ty), (bx, by), col, thickness, cv2.LINE_AA)

        # Swirling particles along beam
        for i in range(6):
            t_frac = (i / 6 + self.frame_count * 0.05) % 1.0
            px = int(tx + direction[0] * t_frac * 300)
            py = int(ty + direction[1] * t_frac * 300)
            particles.emit(px, py, count=2, palette=palette,
                           style="orbit", speed=3.0, gravity=0.0,
                           size_range=(2, 5), lifespan=20)

        # Muzzle flash at fingertip
        t = self.frame_count * 0.2
        for i in range(6):
            angle  = t * 3 + i * math.pi / 3
            px, py = _polar_to_xy(tx, ty, 18 + math.sin(t + i) * 8, angle)
            cv2.circle(overlay, (px, py), 5, palette[1], -1, cv2.LINE_AA)

        self.frame_count += 1
        result = _add_glow(frame, overlay, strength=2.5, kernel=25)
        return cv2.addWeighted(result, 1.0, overlay, 0.9, 0)


# ─── Effect 6 — Web Blast (Spider-Man hand) ──────────────────

class SpiderEffect:
    """
    Multi-directional cursed blast / web — Spider-Man + Black Flash.
    """

    def __init__(self):
        self.frame_count = 0

    def render(self, frame: np.ndarray, hand: dict, particles) -> np.ndarray:
        cx, cy   = hand["palm_center"]
        palette  = COLORS["aura"]
        overlay  = np.zeros_like(frame)
        t        = self.frame_count * 0.15

        # 6 energy streams in rotating directions
        for i in range(6):
            angle = t * 0.5 + i * (math.pi / 3)
            ex, ey = _polar_to_xy(cx, cy, 180, angle)
            col_idx = i % len(palette)
            col     = palette[col_idx]
            cv2.line(overlay, (cx, cy), (ex, ey), col, 3, cv2.LINE_AA)
            cv2.circle(overlay, (ex, ey), 8, col, -1, cv2.LINE_AA)

            particles.emit(ex, ey, count=3, palette=palette,
                           style="burst", speed=5.0, gravity=0.0,
                           size_range=(2, 6), lifespan=25)

        # Central explosion ring
        ring_r = int(40 + math.sin(t * 3) * 20)
        cv2.circle(overlay, (cx, cy), ring_r, (255, 255, 200), 3, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), ring_r // 2, (200, 255, 255), -1, cv2.LINE_AA)

        self.frame_count += 1
        result = _add_glow(frame, overlay, strength=2.2)
        return cv2.addWeighted(result, 1.0, overlay, 0.85, 0)
