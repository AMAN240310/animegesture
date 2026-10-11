# Anime Gesture FX

**Real-Time Hand Gesture Recognition with Anime-Inspired Visual Effects**

Anime Gesture FX is a computer vision project that detects hand gestures in real time and transforms them into dynamic, anime-inspired visual effects. Drawing inspiration from *Naruto*, *Dragon Ball Z*, and *Jujutsu Kaisen*, the project combines hand landmark detection, gesture classification, and particle-based rendering to create an interactive visual experience.

## Features

- **Real-Time Gesture Recognition:** Detects and classifies hand gestures using a webcam.
- **Anime-Inspired Visual Effects:** Generates energy auras, fire bursts, lightning strikes, summoning circles, and other visual effects.
- **Hand Landmark Visualization:** Displays a glowing hand skeleton for interactive feedback.
- **Particle System:** Uses NumPy-based vectorized calculations to manage visual particles efficiently.
- **Gesture Smoothing:** Reduces classification flickering for more stable recognition.
- **Configurable Settings:** Customize camera resolution, particle count, gesture cooldowns, and visual effects.
- **Interactive Controls:** Clear particles, save screenshots, or exit using keyboard shortcuts.

## Gesture-to-Effect Mapping

| Gesture | Recognition Criteria | Visual Effect | Anime Inspiration |
|---|---|---|---|
| Open Palm | All five fingers extended | Golden Energy Aura | Naruto Chakra Mode |
| Fist | All fingers closed | Fire Burst | Dragon Ball Kaioken |
| Thumbs Up | Thumb extended, other fingers closed | Lightning Strike | Sasuke's Chidori |
| Peace Sign ✌️ | Index and middle fingers extended | Summoning Circle | Jujutsu Kaisen Domain Expansion |
| Pointing ☝️ | Index finger extended | Cursed Energy Beam | Gojo's Infinity |
| Spider-Man Gesture 🤟 | Thumb, index, and pinky extended | Web / Energy Blast | Black Flash-inspired effects |

*Note: Gesture recognition accuracy depends on camera visibility, lighting conditions, and hand positioning.*

## Technology Stack

- **Python** — Core application logic
- **OpenCV** — Webcam input and image processing
- **MediaPipe** — Hand landmark detection
- **NumPy** — Vectorized particle calculations
- **Custom Rendering Pipeline** — Glowing effects, particle animations, and visual transitions

See `requirements.txt` for the project's dependency list.

## Project Structure

```text
anime_gesture/
├── main.py
├── config.py
├── hand_detector.py
├── gesture_recognizer.py
├── requirements.txt
├── screenshots/
└── effects/
    ├── __init__.py
    ├── particle_system.py
    ├── anime_effects.py
    ├── effect_manager.py
    └── hud.py
```

### Core Modules

| File | Responsibility |
|---|---|
| `main.py` | Application entry point and main execution loop |
| `config.py` | Centralized configuration for performance and visual settings |
| `hand_detector.py` | Webcam processing, hand landmark detection, and skeleton visualization |
| `gesture_recognizer.py` | Rule-based gesture classification and temporal smoothing |
| `particle_system.py` | Particle simulation and vectorized particle updates |
| `anime_effects.py` | Implementation of the six anime-inspired visual effects |
| `effect_manager.py` | Effect selection, cooldown management, and transitions |
| `hud.py` | On-screen interface, FPS counter, gesture labels, and gesture legend |
| `requirements.txt` | Python dependency specifications |
| `screenshots/` | Directory for screenshots saved by the application |

## Installation

### Prerequisites

- Python 3.8–3.11, subject to compatibility with the selected MediaPipe version
- A working webcam
- Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd anime_gesture
```

Replace `<repository-url>` with the URL of your GitHub repository.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment using the appropriate command.

**Windows — PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows — Command Prompt**

```cmd
venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

Start the application from the project root:

```bash
python main.py
```

Allow webcam access when prompted. Position your hand within the camera frame and perform one of the supported gestures to trigger its corresponding visual effect.

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Q` | Exit the application |
| `ESC` | Exit the application |
| `C` | Clear all active particles |
| `S` | Save a screenshot |

## Configuration

Customize the application through `config.py`.

| Parameter | Default | Description |
|---|---|---|
| `MAX_PARTICLES` | `600` | Maximum particle count; higher values may reduce performance |
| `GESTURE_BUFFER_SIZE` | `8` | Number of recent predictions used for gesture smoothing |
| `GESTURE_COOLDOWN` | `1.2` seconds | Minimum delay before the same gesture can retrigger |
| `GLOW_BLUR_KERNEL` | `31` | Blur kernel size controlling the softness of glow effects |
| `CAMERA_INDEX` | `0` | Webcam device index |
| `FRAME_WIDTH` | `1280` | Camera frame width in pixels |
| `FRAME_HEIGHT` | `720` | Camera frame height in pixels |

Actual performance depends on hardware, camera resolution, particle count, and rendering complexity.

## Troubleshooting

### Webcam Not Detected

- Confirm that the webcam is connected and accessible.
- Close other applications that may be using the camera.
- Try setting `CAMERA_INDEX` to `1` or `2` in `config.py`.

### Low Frame Rate

- Reduce `FRAME_WIDTH` and `FRAME_HEIGHT` to `640 × 480`.
- Lower `MAX_PARTICLES` to `300`.
- Close unnecessary background applications.

### Unstable Gesture Recognition

- Increase `GESTURE_BUFFER_SIZE` to `12` for stronger temporal smoothing.
- Improve lighting and keep the entire hand visible.
- Avoid rapid movements or overlapping fingers when testing gestures.

### `ModuleNotFoundError: No module named 'mediapipe'`

Ensure that the virtual environment is activated and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

If installation fails, verify the Python and MediaPipe versions supported by your chosen dependency release.

## Future Improvements

The project can be extended with the following features:

- **Sound Effects:** Add synchronized audio using `pygame.mixer`.
- **Custom Gesture Training:** Collect hand landmark data and train a classifier using scikit-learn or another machine learning framework.
- **Multi-Hand Interactions:** Support two-hand combinations, energy collisions, and interactive battles.
- **Video Recording:** Record animations using `cv2.VideoWriter`.
- **Interactive GUI:** Add a desktop interface for selecting effects and adjusting settings.
- **AI-Based Recognition:** Explore trained neural networks for more flexible gesture classification.
- **Additional Effect Themes:** Introduce new animations, particle behaviors, and customizable visual styles.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Submit a pull request describing the changes.

Please keep contributions focused, document new configuration options, and include screenshots or recordings when introducing visual effects.

## License

Add a `LICENSE` file to specify the terms under which this project can be used, modified, and distributed.

## Acknowledgements

- [OpenCV](https://opencv.org/) for computer vision and image processing.
- [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) for hand landmark detection.
- [NumPy](https://numpy.org/) for numerical computing.

---

**Anime Gesture FX** — Bringing anime-inspired energy effects into real-time computer vision.
