# ============================================================
# effects/hud.py — Heads-up display: gesture label + FPS + tips
# ============================================================

import cv2
import numpy as np
import time
from gesture_recognizer import (
    GESTURE_OPEN_PALM, GESTURE_FIST, GESTURE_PEACE,
    GESTURE_THUMBS_UP, GESTURE_POINTING, GESTURE_SPIDER, GESTURE_UNKNOWN,
)

# Color per gesture (BGR)
GESTURE_COLORS = {
    GESTURE_OPEN_PALM: (0,   210, 255),
    GESTURE_FIST:      (0,   80,  255),
    GESTURE_PEACE:     (50,  220, 50),
    GESTURE_THUMBS_UP: (180, 180, 255),
    GESTURE_POINTING:  (180, 0,   220),
    GESTURE_SPIDER:    (255, 200, 0),
    GESTURE_UNKNOWN:   (160, 160, 160),
}

GESTURE_EFFECT_DESC = {
    GESTURE_OPEN_PALM: "✦ ENERGY AURA",
    GESTURE_FIST:      "🔥 FIRE BURST",
    GESTURE_PEACE:     "✧ SPIRIT SUMMON",
    GESTURE_THUMBS_UP: "⚡ LIGHTNING STRIKE",
    GESTURE_POINTING:  "◈ CURSED BEAM",
    GESTURE_SPIDER:    "❋ WEB BLAST",
    GESTURE_UNKNOWN:   "— Detecting...",
}


class HUD:
    def __init__(self, frame_w: int, frame_h: int):
        self.fw = frame_w
        self.fh = frame_h
        self._fps_times = []
        self._last_gesture = GESTURE_UNKNOWN
        self._label_anim  = 0.0

    # ----------------------------------------------------------
    def update_fps(self):
        now = time.time()
        self._fps_times.append(now)
        # Keep only last 30 timestamps
        cutoff = now - 1.0
        self._fps_times = [t for t in self._fps_times if t > cutoff]

    def get_fps(self) -> int:
        return len(self._fps_times)

    # ----------------------------------------------------------
    def draw(self, frame: np.ndarray, gesture: str,
             num_hands: int) -> np.ndarray:
        """Draw HUD elements on frame (returns modified frame)."""
        self.update_fps()
        fps = self.get_fps()

        # Animate label when gesture changes
        if gesture != self._last_gesture:
            self._label_anim  = 1.0
            self._last_gesture = gesture
        self._label_anim = max(0.0, self._label_anim - 0.04)

        col   = GESTURE_COLORS.get(gesture, (200, 200, 200))
        label = GESTURE_EFFECT_DESC.get(gesture, gesture)

        # ── Semi-transparent top bar ──────────────────────────
        bar = np.zeros((70, self.fw, 3), dtype=np.uint8)
        cv2.rectangle(bar, (0, 0), (self.fw, 70), (10, 10, 10), -1)
        frame[:70] = cv2.addWeighted(frame[:70], 0.4, bar, 0.6, 0)

        # ── Gesture label (with pop-in scale animation) ───────
        scale   = 0.9 + self._label_anim * 0.4
        thickness = 2
        text    = f"{label}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
        tx = (self.fw - tw) // 2
        ty = 45

        # Glow shadow
        cv2.putText(frame, text, (tx + 2, ty + 2),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        # Colored text
        cv2.putText(frame, text, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, col, thickness, cv2.LINE_AA)

        # ── FPS counter ───────────────────────────────────────
        fps_color = (0, 255, 80) if fps >= 25 else (0, 165, 255) if fps >= 15 else (0, 60, 255)
        cv2.putText(frame, f"FPS: {fps}", (12, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, fps_color, 1, cv2.LINE_AA)

        # ── Hand count ────────────────────────────────────────
        cv2.putText(frame, f"Hands: {num_hands}", (12, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

        # ── Legend (bottom-right corner) ─────────────────────
        legend_items = [
            ("Open Palm",  "Energy Aura",     GESTURE_COLORS[GESTURE_OPEN_PALM]),
            ("Fist",       "Fire Burst",       GESTURE_COLORS[GESTURE_FIST]),
            ("Peace ✌",   "Spirit Summon",    GESTURE_COLORS[GESTURE_PEACE]),
            ("Thumbs Up",  "Lightning",        GESTURE_COLORS[GESTURE_THUMBS_UP]),
            ("Point ☝",   "Cursed Beam",      GESTURE_COLORS[GESTURE_POINTING]),
            ("Spider 🤟",  "Web Blast",        GESTURE_COLORS[GESTURE_SPIDER]),
        ]
        lx = self.fw - 250
        ly_start = self.fh - len(legend_items) * 24 - 10
        for i, (g_name, eff_name, c) in enumerate(legend_items):
            ly = ly_start + i * 24
            cv2.circle(frame, (lx, ly - 4), 6, c, -1, cv2.LINE_AA)
            cv2.putText(frame, f"{g_name}: {eff_name}",
                        (lx + 14, ly),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                        (220, 220, 220), 1, cv2.LINE_AA)

        # ── Quit hint ─────────────────────────────────────────
        cv2.putText(frame, "Press Q to quit | C to clear",
                    (12, self.fh - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1, cv2.LINE_AA)

        return frame
