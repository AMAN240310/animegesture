# ============================================================
# effects/effect_manager.py
# Central dispatcher: gesture → effect instance
# Handles per-gesture cooldown + smooth transition overlay
# ============================================================

import time
import cv2
import numpy as np

from gesture_recognizer import (
    GESTURE_OPEN_PALM, GESTURE_FIST, GESTURE_PEACE,
    GESTURE_THUMBS_UP, GESTURE_POINTING, GESTURE_SPIDER, GESTURE_UNKNOWN,
)
from effects.anime_effects import (
    AuraEffect, FireEffect, LightningEffect,
    PeaceEffect, CurseEffect, SpiderEffect,
)
from effects.particle_system import ParticleSystem
from config import GESTURE_COOLDOWN


class EffectManager:
    """
    Owns one ParticleSystem + one instance of each effect class.
    Call render(frame, gesture, hand) each frame.
    """

    def __init__(self):
        self.particles = ParticleSystem()

        # One effect instance per gesture (stateful — keep frame counters)
        self._effects = {
            GESTURE_OPEN_PALM: AuraEffect(),
            GESTURE_FIST:      FireEffect(),
            GESTURE_THUMBS_UP: LightningEffect(),
            GESTURE_PEACE:     PeaceEffect(),
            GESTURE_POINTING:  CurseEffect(),
            GESTURE_SPIDER:    SpiderEffect(),
        }

        self._last_gesture    = GESTURE_UNKNOWN
        self._cooldown_until  = 0.0
        self._transition_alpha = 0.0   # fade-in on gesture change

    # ----------------------------------------------------------
    def render(self, frame: np.ndarray, gesture: str, hand: dict) -> np.ndarray:
        """
        Apply the correct effect for `gesture` and update particles.
        Returns the modified frame.
        """
        now = time.time()

        # ── Cooldown check ─────────────────────────────────────
        if gesture != self._last_gesture:
            if now < self._cooldown_until:
                gesture = self._last_gesture  # hold previous during cooldown
            else:
                self._cooldown_until  = now + GESTURE_COOLDOWN
                self._transition_alpha = 1.0  # start fade-in
                self._last_gesture    = gesture

        # ── Fade-in blend (smooth transition) ─────────────────
        self._transition_alpha = max(0.0, self._transition_alpha - 0.06)

        # ── Run the matched effect ─────────────────────────────
        effect = self._effects.get(gesture)
        if effect and gesture != GESTURE_UNKNOWN:
            frame = effect.render(frame, hand, self.particles)

        # ── Particle simulation ────────────────────────────────
        self.particles.update()
        self.particles.draw(frame)

        # ── Transition flash (white-in on gesture switch) ──────
        if self._transition_alpha > 0.01:
            flash = np.ones_like(frame, dtype=np.uint8) * 255
            frame = cv2.addWeighted(frame, 1.0, flash,
                                    self._transition_alpha * 0.15, 0)

        return frame

    # ----------------------------------------------------------
    def clear_particles(self):
        self.particles.clear()
