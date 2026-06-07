# ============================================================
# gesture_recognizer.py — Rule-based gesture classification
# with temporal smoothing to eliminate flicker
# ============================================================

import numpy as np
from collections import deque
from config import GESTURE_BUFFER_SIZE


# ─── Gesture names ───────────────────────────────────────────
GESTURE_OPEN_PALM  = "Open Palm"    # → Energy Aura
GESTURE_FIST       = "Fist"         # → Fire Burst
GESTURE_PEACE      = "Peace Sign"   # → Spirit Summon
GESTURE_THUMBS_UP  = "Thumbs Up"   # → Lightning Strike
GESTURE_POINTING   = "Pointing"    # → Cursed Energy beam
GESTURE_SPIDER     = "Spider-Man"  # → Web / Cursed blast
GESTURE_UNKNOWN    = "Unknown"


class FingerState:
    """Helper: determine which fingers are extended for a hand."""

    # Landmark index pairs (tip, pip) used to test if finger is open
    FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky
    FINGER_PIPS = [6, 10, 14, 18]

    @staticmethod
    def get_extended(landmarks_norm: np.ndarray) -> list:
        """
        Returns [thumb, index, middle, ring, pinky] as booleans.
        landmarks_norm shape: (21, 3)  — normalized x,y,z
        """
        lm = landmarks_norm

        # Thumb — compare tip x vs ip x (mirrored for left/right)
        # Use wrist-to-thumb-mcp direction as reference
        thumb_extended = abs(lm[4][0] - lm[2][0]) > 0.07

        fingers = [thumb_extended]
        for tip, pip in zip(FingerState.FINGER_TIPS, FingerState.FINGER_PIPS):
            # Finger open when tip is above (lower y value) its PIP joint
            fingers.append(lm[tip][1] < lm[pip][1])

        return fingers  # [thumb, index, middle, ring, pinky]

    @staticmethod
    def curl_ratio(landmarks_norm: np.ndarray, tip: int, mcp: int) -> float:
        """Euclidean distance between tip and MCP (proxy for curl)."""
        return float(np.linalg.norm(landmarks_norm[tip][:2] - landmarks_norm[mcp][:2]))


class GestureRecognizer:
    """
    Classifies a hand's landmarks into a gesture label.
    Uses a rolling buffer to smooth out frame-to-frame noise.
    """

    def __init__(self):
        # One buffer per hand slot (left / right)
        self._buffers = {
            "Left":  deque(maxlen=GESTURE_BUFFER_SIZE),
            "Right": deque(maxlen=GESTURE_BUFFER_SIZE),
        }

    # ----------------------------------------------------------
    def classify(self, hand: dict) -> str:
        """
        Run classification and return smoothed gesture name.
        """
        raw_gesture = self._classify_raw(hand["landmarks_norm"])
        side        = hand["handedness"]

        self._buffers[side].append(raw_gesture)
        return self._smooth(side)

    # ----------------------------------------------------------
    def _smooth(self, side: str) -> str:
        """Return the most common gesture in the buffer."""
        buf = self._buffers[side]
        if not buf:
            return GESTURE_UNKNOWN
        # Majority vote
        from collections import Counter
        return Counter(buf).most_common(1)[0][0]

    # ----------------------------------------------------------
    def _classify_raw(self, lm: np.ndarray) -> str:
        """
        Pure geometry — no ML needed for these 7 gestures.
        lm: (21, 3) float array of normalized coords.
        """
        f = FingerState.get_extended(lm)
        thumb, index, middle, ring, pinky = f

        # ── Open Palm (all 5 fingers up)
        if all(f):
            return GESTURE_OPEN_PALM

        # ── Fist (all fingers closed, thumb tucked)
        if not any(f):
            return GESTURE_FIST

        # ── Thumbs Up (only thumb extended, rest closed)
        if thumb and not index and not middle and not ring and not pinky:
            # Extra check: thumb tip above wrist
            if lm[4][1] < lm[0][1] - 0.05:
                return GESTURE_THUMBS_UP

        # ── Peace / Victory (index + middle up, rest down)
        if not thumb and index and middle and not ring and not pinky:
            return GESTURE_PEACE

        # ── Pointing (only index up)
        if not thumb and index and not middle and not ring and not pinky:
            return GESTURE_POINTING

        # ── Spider-Man (thumb + index + pinky up = web-shooter)
        if thumb and index and not middle and not ring and pinky:
            return GESTURE_SPIDER

        return GESTURE_UNKNOWN
