# ============================================================
# main.py — Entry point for Anime Gesture FX
#
# Run:  python main.py
# Keys: Q = quit   C = clear particles   S = screenshot
# ============================================================

import cv2
import numpy as np
import time
import sys
import os

from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TARGET_FPS,
)
from hand_detector    import HandDetector
from gesture_recognizer import GestureRecognizer, GESTURE_UNKNOWN
from effects.effect_manager import EffectManager
from effects.hud            import HUD


# ─── Optional: vignette for cinematic look ────────────────────

def _make_vignette(h: int, w: int) -> np.ndarray:
    """Pre-compute a dark vignette mask."""
    mask = np.zeros((h, w), dtype=np.float32)
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            dist = np.sqrt(((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2)
            mask[y, x] = np.clip(1.0 - dist * 0.7, 0, 1)
    return np.stack([mask, mask, mask], axis=2)


def apply_vignette(frame: np.ndarray, vignette: np.ndarray) -> np.ndarray:
    return np.clip(frame.astype(np.float32) * vignette, 0, 255).astype(np.uint8)


# ─── Splash screen ───────────────────────────────────────────

def show_splash(cap, wait: float = 2.5):
    deadline = time.time() + wait
    while time.time() < deadline:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Dark overlay
        overlay = np.zeros_like(frame)
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.35, overlay, 0.65, 0)

        # Title
        title = "ANIME GESTURE FX"
        (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1.8, 3)
        cv2.putText(frame, title, ((w - tw) // 2, h // 2 - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 200, 255), 3, cv2.LINE_AA)

        subtitle = "Show your hand to begin"
        (sw, _), _ = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)
        cv2.putText(frame, subtitle, ((w - sw) // 2, h // 2 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 180, 180), 1, cv2.LINE_AA)

        cv2.imshow("Anime Gesture FX", frame)
        if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
            return False
    return True


# ─── Main loop ───────────────────────────────────────────────

def main():
    # ── Camera init ───────────────────────────────────────────
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam. Check CAMERA_INDEX in config.py")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,          TARGET_FPS)

    # Read actual resolution (camera may cap it)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Camera: {actual_w}×{actual_h}")

    # ── System modules ────────────────────────────────────────
    detector   = HandDetector()
    recognizer = GestureRecognizer()
    fx_manager = EffectManager()
    hud        = HUD(actual_w, actual_h)

    # Pre-compute vignette
    vignette = _make_vignette(actual_h, actual_w)

    # ── Window ────────────────────────────────────────────────
    cv2.namedWindow("Anime Gesture FX", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Anime Gesture FX", actual_w, actual_h)

    if not show_splash(cap):
        cap.release()
        cv2.destroyAllWindows()
        return

    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    print("[INFO] Running — Q to quit, C to clear, S for screenshot")

    # ── Frame loop ────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame grab failed — retrying...")
            continue

        # Mirror so hand movement feels natural
        frame = cv2.flip(frame, 1)

        # ── Hand detection ────────────────────────────────────
        hands = detector.detect(frame)

        # ── Per-hand processing ───────────────────────────────
        gesture = GESTURE_UNKNOWN
        for hand in hands:
            g = recognizer.classify(hand)
            if g != GESTURE_UNKNOWN:
                gesture = g  # use first confident hand

            # Draw glowing skeleton
            detector.draw_skeleton(frame, hand)

            # Apply anime effect
            frame = fx_manager.render(frame, gesture, hand)

        # Vignette for cinematic feel
        frame = apply_vignette(frame, vignette)

        # ── HUD ───────────────────────────────────────────────
        frame = hud.draw(frame, gesture, len(hands))

        # ── Display ───────────────────────────────────────────
        cv2.imshow("Anime Gesture FX", frame)

        # ── Key handling ──────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):       # Q / ESC → quit
            break
        elif key == ord('c'):           # C → clear particles
            fx_manager.clear_particles()
            print("[INFO] Particles cleared")
        elif key == ord('s'):           # S → screenshot
            fname = os.path.join(screenshot_dir,
                                 f"capture_{int(time.time())}.png")
            cv2.imwrite(fname, frame)
            print(f"[INFO] Screenshot saved: {fname}")

    # ── Cleanup ───────────────────────────────────────────────
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Exited cleanly.")


if __name__ == "__main__":
    main()
