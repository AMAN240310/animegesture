# ============================================================
# hand_detector.py — MediaPipe hand tracking wrapper
# Returns normalized landmarks + world coordinates
# ============================================================

import cv2
import mediapipe as mp
import numpy as np
from config import MAX_HANDS, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE


class HandDetector:
    """
    Wraps MediaPipe Hands.
    Call detect(frame) → list of Hand objects each frame.
    """

    # MediaPipe landmark indices (constants for readability)
    WRIST           = 0
    THUMB_CMC       = 1;  THUMB_MCP  = 2;  THUMB_IP  = 3;  THUMB_TIP  = 4
    INDEX_MCP       = 5;  INDEX_PIP  = 6;  INDEX_DIP = 7;  INDEX_TIP  = 8
    MIDDLE_MCP      = 9;  MIDDLE_PIP = 10; MIDDLE_DIP= 11; MIDDLE_TIP = 12
    RING_MCP        = 13; RING_PIP   = 14; RING_DIP  = 15; RING_TIP   = 16
    PINKY_MCP       = 17; PINKY_PIP  = 18; PINKY_DIP = 19; PINKY_TIP  = 20

    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._hands    = self._mp_hands.Hands(
            static_image_mode        = False,
            max_num_hands            = MAX_HANDS,
            min_detection_confidence = DETECTION_CONFIDENCE,
            min_tracking_confidence  = TRACKING_CONFIDENCE,
        )
        self._draw     = mp.solutions.drawing_utils
        self._styles   = mp.solutions.drawing_styles

    # ----------------------------------------------------------
    def detect(self, frame: np.ndarray) -> list:
        """
        Run inference on a BGR frame.
        Returns list of dicts, one per detected hand.
        """
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)
        h, w    = frame.shape[:2]

        hands = []
        if not results.multi_hand_landmarks:
            return hands

        for idx, lm_list in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label  # 'Left' / 'Right'

            # Pixel coordinates (x, y) for all 21 landmarks
            points_px = np.array(
                [(int(lm.x * w), int(lm.y * h)) for lm in lm_list.landmark],
                dtype=np.int32,
            )

            # Normalized [0,1] coordinates
            points_norm = np.array(
                [(lm.x, lm.y, lm.z) for lm in lm_list.landmark],
                dtype=np.float32,
            )

            # Bounding box (for centering effects)
            x_coords = points_px[:, 0]
            y_coords = points_px[:, 1]
            bbox = (x_coords.min(), y_coords.min(),
                    x_coords.max(), y_coords.max())

            # Palm center = average of wrist + 5 MCP joints
            palm_indices = [self.WRIST,
                            self.INDEX_MCP, self.MIDDLE_MCP,
                            self.RING_MCP,  self.PINKY_MCP]
            palm_center = points_px[palm_indices].mean(axis=0).astype(int)

            hands.append({
                "landmarks_px":   points_px,
                "landmarks_norm": points_norm,
                "handedness":     handedness,
                "bbox":           bbox,
                "palm_center":    tuple(palm_center),
                "raw":            lm_list,   # keep for drawing
            })

        return hands

    # ----------------------------------------------------------
    def draw_skeleton(self, frame: np.ndarray, hand: dict,
                      color: tuple = (0, 255, 120)) -> None:
        """Draw glowing MediaPipe skeleton on frame (in-place)."""
        # Glow pass — draw thicker, blurred copy
        overlay = np.zeros_like(frame)
        self._draw.draw_landmarks(
            overlay,
            hand["raw"],
            self._mp_hands.HAND_CONNECTIONS,
            mp.solutions.drawing_utils.DrawingSpec(
                color=color, thickness=6, circle_radius=4),
            mp.solutions.drawing_utils.DrawingSpec(
                color=color, thickness=4),
        )
        blurred = cv2.GaussianBlur(overlay, (21, 21), 0)
        frame[:] = cv2.addWeighted(frame, 1.0, blurred, 0.8, 0)

        # Sharp pass on top
        self._draw.draw_landmarks(
            frame,
            hand["raw"],
            self._mp_hands.HAND_CONNECTIONS,
            mp.solutions.drawing_utils.DrawingSpec(
                color=(255, 255, 255), thickness=2, circle_radius=3),
            mp.solutions.drawing_utils.DrawingSpec(
                color=color, thickness=2),
        )
