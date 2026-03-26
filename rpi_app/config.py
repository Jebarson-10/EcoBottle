"""
Configuration for the Raspberry Pi Vending Machine App.
Update these values to match your setup.
"""

# ─── Firebase Configuration ─────────────────────────────
# Path to your Firebase service account key JSON file
FIREBASE_CREDENTIALS_PATH = "serviceAccountKey.json"

# ─── Weight Sensor Configuration ─────────────────────────────
# HX711 GPIO pins (BCM numbering)
HX711_DT_PIN = 5   # Data pin
HX711_SCK_PIN = 6  # Clock pin

# Calibration: adjust these based on your load cell
WEIGHT_REFERENCE_UNIT = 1  # Calibration factor
WEIGHT_OFFSET = 0           # Tare offset

# ─── Points Configuration ────────────────────────────────────
# Points earned per gram of bottle weight
POINTS_PER_GRAM = 0.1  # 1 point per 10 grams

# ─── Camera Configuration ────────────────────────────────────
CAMERA_INDEX = 0        # Camera device index (0 = default)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# ─── Detection Configuration ────────────────────────────────
# Minimum confidence threshold for bottle detection
DETECTION_CONFIDENCE = 0.45

# ─── GUI Configuration ──────────────────────────────────────
# Window title
APP_TITLE = "EcoBottle Reverse Vending Machine"

# Set to True when running on a machine without HX711 hardware
# (will simulate weight readings)
MOCK_WEIGHT_SENSOR = True

# Set to True when running without camera (uses placeholder)
MOCK_CAMERA = False
