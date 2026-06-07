# 🎌 Anime Gesture FX

Real-time hand gesture recognition with anime-style visual effects.
Inspired by Naruto, Dragon Ball Z, and Jujutsu Kaisen.

---

## ✨ Gesture → Effect Map

| Gesture         | Hand Shape           | Effect                        | Anime Inspiration          |
|----------------|----------------------|-------------------------------|----------------------------|
| Open Palm      | All 5 fingers up     | ✦ Golden Energy Aura          | Naruto Chakra Mode         |
| Fist           | All fingers closed   | 🔥 Fire Burst                 | Dragon Ball Kaioken        |
| Thumbs Up      | Only thumb up        | ⚡ Lightning Strike           | Sasuke Chidori             |
| Peace Sign ✌   | Index + Middle up    | ✧ Summoning Circle            | Jujutsu Kaisen Domain      |
| Pointing ☝     | Only index up        | ◈ Cursed Energy Beam          | Gojo Infinity              |
| Spider-Man 🤟  | Thumb+Index+Pinky up | ❋ Web / Energy Blast          | Black Flash                |

---

## 📦 Installation

```bash
# 1. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Run

```bash
python main.py
```

### Keys
| Key | Action              |
|-----|---------------------|
| `Q` | Quit                |
| `C` | Clear all particles |
| `S` | Save screenshot     |
| `ESC` | Quit              |

---

## 📁 Project Structure

```
anime_gesture/
├── main.py                  ← Entry point
├── config.py                ← All tunable settings
├── hand_detector.py         ← MediaPipe wrapper + glowing skeleton
├── gesture_recognizer.py    ← Rule-based gesture classifier + smoothing
├── requirements.txt
├── screenshots/             ← Auto-created by pressing S
└── effects/
    ├── __init__.py
    ├── particle_system.py   ← NumPy vectorised GPU-style particles
    ├── anime_effects.py     ← 6 effect classes (aura/fire/lightning/etc.)
    ├── effect_manager.py    ← Dispatcher + cooldown + transitions
    └── hud.py               ← FPS counter + gesture label + legend
```

---

## ⚙️ Tuning (config.py)

| Setting              | Default | Effect                              |
|---------------------|---------|-------------------------------------|
| `MAX_PARTICLES`     | 600     | Increase for denser effects (costs FPS) |
| `GESTURE_BUFFER_SIZE` | 8    | Higher = more stable, slower response |
| `GESTURE_COOLDOWN`  | 1.2s    | Seconds before same gesture retriggered |
| `GLOW_BLUR_KERNEL`  | 31      | Larger = softer/wider glow          |
| `CAMERA_INDEX`      | 0       | Change if using external webcam     |
| `FRAME_WIDTH/HEIGHT`| 1280×720| Lower for better FPS on slow machines |

---

## 🛠️ Troubleshooting

**"Could not open webcam"**
→ Try setting `CAMERA_INDEX = 1` or `2` in `config.py`

**Low FPS**
→ Lower `FRAME_WIDTH = 640`, `FRAME_HEIGHT = 480` in `config.py`
→ Lower `MAX_PARTICLES = 300`

**Gesture flickering**
→ Increase `GESTURE_BUFFER_SIZE = 12` in `config.py`

**ModuleNotFoundError: mediapipe**
→ Run `pip install mediapipe`  (Python 3.8–3.11 only — not 3.12)

---

## 🔮 Ideas for Extension

- **Add sound effects** — `pygame.mixer` to play audio on gesture trigger
- **Train custom gestures** — collect landmark data → train sklearn SVM
- **Multi-hand battles** — left fist vs right palm = explosion collision
- **Record video** — `cv2.VideoWriter` to save effect clips
- **GUI selector** — Tkinter/PyQt panel to pick effect theme
- **AI mode** — replace rule-based classifier with a trained CNN on landmark coords
