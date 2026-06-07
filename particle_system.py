# ============================================================
# effects/particle_system.py — GPU-style particle engine
# Fully vectorised with NumPy for real-time performance
# ============================================================

import numpy as np
import cv2
from config import MAX_PARTICLES, PARTICLE_LIFESPAN


class ParticleSystem:
    """
    Manages a pool of particles.
    All state stored in numpy arrays → fast batch updates.

    Attributes per particle:
        x, y          — position (float)
        vx, vy        — velocity (float)
        life          — remaining frames
        max_life      — for alpha fade calc
        size          — radius in pixels
        color_idx     — index into a palette
    """

    def __init__(self, max_particles: int = MAX_PARTICLES):
        self.max_p = max_particles
        self._reset_all()

    # ----------------------------------------------------------
    def _reset_all(self):
        n = self.max_p
        self.x        = np.zeros(n, np.float32)
        self.y        = np.zeros(n, np.float32)
        self.vx       = np.zeros(n, np.float32)
        self.vy       = np.zeros(n, np.float32)
        self.life     = np.zeros(n, np.float32)
        self.max_life = np.ones(n,  np.float32) * PARTICLE_LIFESPAN
        self.size     = np.ones(n,  np.float32) * 4
        self.r        = np.zeros(n, np.float32)
        self.g        = np.zeros(n, np.float32)
        self.b        = np.zeros(n, np.float32)
        self.gravity  = np.zeros(n, np.float32)

    # ----------------------------------------------------------
    def emit(self, cx: int, cy: int, count: int,
             palette: list, style: str = "burst",
             lifespan: int = PARTICLE_LIFESPAN,
             speed: float = 6.0, gravity: float = 0.15,
             size_range: tuple = (3, 9)):
        """
        Spawn `count` particles at (cx, cy).
        style: 'burst' | 'rain' | 'orbit' | 'stream'
        """
        # Find dead slots
        dead = np.where(self.life <= 0)[0]
        count = min(count, len(dead))
        if count == 0:
            return
        slots = dead[:count]

        angles = np.random.uniform(0, 2 * np.pi, count)
        speeds = np.random.uniform(speed * 0.4, speed, count)

        if style == "burst":
            self.vx[slots] = np.cos(angles) * speeds
            self.vy[slots] = np.sin(angles) * speeds
        elif style == "rain":
            self.vx[slots] = np.random.uniform(-speed * 0.3, speed * 0.3, count)
            self.vy[slots] = np.random.uniform(speed * 0.5, speed, count)
        elif style == "orbit":
            self.vx[slots] = np.cos(angles + np.pi / 2) * speeds
            self.vy[slots] = np.sin(angles + np.pi / 2) * speeds
        elif style == "stream":
            self.vx[slots] = np.random.uniform(-1, 1, count)
            self.vy[slots] = np.random.uniform(-speed, -speed * 0.5, count)

        # Scatter spawn point slightly for natural spread
        scatter = speed * 3
        self.x[slots] = cx + np.random.uniform(-scatter, scatter, count)
        self.y[slots] = cy + np.random.uniform(-scatter, scatter, count)

        self.life[slots]     = lifespan + np.random.randint(-5, 5, count)
        self.max_life[slots] = self.life[slots]
        self.size[slots]     = np.random.uniform(*size_range, count)
        self.gravity[slots]  = gravity

        # Assign colors from palette (cycle through)
        for i, slot in enumerate(slots):
            col = palette[i % len(palette)]
            self.b[slot], self.g[slot], self.r[slot] = col  # BGR → RGB store

    # ----------------------------------------------------------
    def update(self):
        """Advance simulation one frame (vectorised)."""
        alive = self.life > 0
        if not np.any(alive):
            return

        self.vx[alive] *= 0.97          # air drag
        self.vy[alive] *= 0.97
        self.vy[alive] += self.gravity[alive]

        self.x[alive]    += self.vx[alive]
        self.y[alive]    += self.vy[alive]
        self.life[alive] -= 1

    # ----------------------------------------------------------
    def draw(self, frame: np.ndarray):
        """Render all alive particles with alpha blend + glow."""
        alive_idx = np.where(self.life > 0)[0]
        if len(alive_idx) == 0:
            return

        h, w = frame.shape[:2]
        overlay = np.zeros_like(frame, dtype=np.uint8)

        for i in alive_idx:
            px = int(self.x[i])
            py = int(self.y[i])
            if not (0 <= px < w and 0 <= py < h):
                continue

            alpha  = float(self.life[i]) / float(self.max_life[i])
            radius = max(1, int(self.size[i] * alpha))
            color  = (
                int(self.b[i] * alpha),
                int(self.g[i] * alpha),
                int(self.r[i] * alpha),
            )

            # Core dot
            cv2.circle(overlay, (px, py), radius, color, -1, cv2.LINE_AA)
            # Soft halo
            if radius > 2:
                halo_col = tuple(min(255, int(c * 0.5)) for c in color)
                cv2.circle(overlay, (px, py), radius * 2, halo_col, 1, cv2.LINE_AA)

        # Glow pass
        blurred = cv2.GaussianBlur(overlay, (15, 15), 0)
        frame[:] = cv2.addWeighted(frame, 1.0, blurred, 1.2, 0)
        frame[:] = cv2.addWeighted(frame, 1.0, overlay, 1.0, 0)

    # ----------------------------------------------------------
    def clear(self):
        self.life[:] = 0
