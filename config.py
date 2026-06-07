# ============================================================
# config.py — Central configuration for the entire project
# ============================================================

# --- Camera ---
CAMERA_INDEX = 0
FRAME_WIDTH  = 1280
FRAME_HEIGHT = 720
TARGET_FPS   = 30

# --- Hand Detection ---
MAX_HANDS            = 2
DETECTION_CONFIDENCE = 0.75
TRACKING_CONFIDENCE  = 0.75

# --- Gesture Smoothing ---
# How many frames to buffer before confirming a gesture change
GESTURE_BUFFER_SIZE = 8
# Seconds before the same gesture can retrigger its effect
GESTURE_COOLDOWN    = 1.2

# --- Effects ---
MAX_PARTICLES     = 600   # cap to keep FPS healthy
PARTICLE_LIFESPAN = 45    # frames
GLOW_BLUR_KERNEL  = 31    # must be odd

# --- Color palettes (BGR) ---
COLORS = {
    "fire":      [(0, 0, 255), (0, 60, 255), (0, 120, 255), (0, 200, 255)],
    "aura":      [(255, 180, 0), (255, 220, 80), (180, 255, 255), (255, 255, 255)],
    "lightning": [(255, 255, 200), (255, 255, 100), (200, 180, 255), (255, 255, 255)],
    "peace":     [(80, 255, 120), (0, 200, 80), (120, 255, 200), (255, 255, 255)],
    "curse":     [(120, 0, 180), (200, 0, 255), (60, 0, 120), (255, 100, 255)],
}

# --- UI ---
FONT_SCALE = 1.0
HUD_COLOR  = (255, 255, 255)  # white HUD text
