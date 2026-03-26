# 🌱 EcoBottle — Reverse Vending Machine System

A complete plastic bottle recycling rewards system with:
- **Django Web Server** — REST API + beautiful web UI to check recycling points
- **Raspberry Pi App** — Touchscreen GUI with real-time camera bottle detection, HX711 weight sensor integration, and on-screen keyboard

> Users deposit plastic bottles → the machine detects & weighs them → points are earned (1 point per 10g) → check points anytime via the web dashboard.

---

## 📂 Project Structure

```
EcoBottle/
├── server/              # Django web application
│   ├── bottle_vending/  # Django project settings
│   ├── vending/         # Main Django app (models, views, API)
│   ├── templates/       # HTML templates
│   ├── static/          # CSS & JS
│   ├── manage.py
│   ├── create_test_data.py
│   └── requirements.txt
│
├── rpi_app/             # Raspberry Pi vending machine app
│   ├── main.py          # GUI application (Tkinter)
│   ├── bottle_detector.py  # OpenCV bottle detection
│   ├── weight_sensor.py    # HX711 weight sensor driver
│   ├── api_client.py       # REST API client
│   ├── config.py           # All configurable settings
│   └── requirements.txt
│
└── README.md
```

---

## 🖥️ Part 1: Django Web Server Setup

The server provides:
- A **web page** where users enter their register number to check points
- A **REST API** that the Raspberry Pi app uses to submit deposits

### Prerequisites
- Python 3.8+
- pip

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/Jebarson-10/EcoBottle.git
cd EcoBottle/server

# 2. Create a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. (Optional) Create a superuser for Django admin
python manage.py createsuperuser

# 6. (Optional) Load sample test data
python create_test_data.py

# 7. Start the server
python manage.py runserver 0.0.0.0:8000
```

The web UI is now available at **http://localhost:8000**  
The Django admin panel is at **http://localhost:8000/admin**

### ⚙️ Server Configuration

| Setting | File | Description |
|---------|------|-------------|
| `SECRET_KEY` | `server/bottle_vending/settings.py` (line 23) | **Change this** in production! Generate a new one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `server/bottle_vending/settings.py` (line 26) | Set to `False` in production |
| `ALLOWED_HOSTS` | `server/bottle_vending/settings.py` (line 28) | Currently `['*']`. In production, list your specific domain/IPs |
| `POINTS_PER_GRAM` | `server/vending/views.py` (line 11) | Point calculation rate. Default: `0.1` (1 point per 10g) |

### 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/deposit/` | Submit a bottle deposit (`{"register_number": "...", "weight_grams": 150.0}`) |
| `GET` | `/api/points/<register_number>/` | Get points and transaction history for a user |

### Test Register Numbers (after loading sample data)
- `REG001` — 45 points
- `REG002` — 55 points
- `2024CS101` — 87 points

---

## 🍇 Part 2: Raspberry Pi App Setup

The Pi app provides a touchscreen GUI with:
- Live camera feed for plastic bottle detection (YOLOv8 / OpenCV)
- HX711 weight sensor integration
- On-screen keyboard for register number entry
- Automatic point submission to the Django server

### Prerequisites
- Raspberry Pi 3/4/5 with Raspbian OS
- Camera module or USB webcam
- HX711 load cell amplifier + load cell (for weight sensing)
- Touchscreen display (recommended)
- Python 3.8+

### Step-by-Step Setup

```bash
# 1. Clone the repository (on the Pi)
git clone https://github.com/Jebarson-10/EcoBottle.git
cd EcoBottle/rpi_app

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Raspberry Pi specific libraries (on actual Pi hardware)
pip install RPi.GPIO hx711
```

### ⚙️ Raspberry Pi Configuration

All Pi settings are in **`rpi_app/config.py`**. Edit this file before running:

| Setting | Default | Description |
|---------|---------|-------------|
| `SERVER_URL` | `http://192.168.1.100:8000` | **⚠️ CHANGE THIS** — IP address of the machine running the Django server |
| `HX711_DT_PIN` | `5` | GPIO data pin for HX711 weight sensor (BCM numbering) |
| `HX711_SCK_PIN` | `6` | GPIO clock pin for HX711 weight sensor (BCM numbering) |
| `WEIGHT_REFERENCE_UNIT` | `1` | Load cell calibration factor — adjust for your hardware |
| `WEIGHT_OFFSET` | `0` | Tare offset — adjust for your hardware |
| `POINTS_PER_GRAM` | `0.1` | Points calculation (1 point per 10g) |
| `CAMERA_INDEX` | `0` | Camera device index (`0` = default camera) |
| `DETECTION_CONFIDENCE` | `0.45` | Minimum confidence for bottle detection (0.0–1.0) |
| `MOCK_WEIGHT_SENSOR` | `True` | Set to `False` when HX711 hardware is connected |
| `MOCK_CAMERA` | `False` | Set to `True` to use a placeholder instead of a real camera |

### Running the Pi App

```bash
# Make sure the Django server is running and reachable first!

# Run the vending machine GUI
python3 main.py
```

### 🔧 Calibrating the Weight Sensor

1. Set `MOCK_WEIGHT_SENSOR = False` in `config.py`
2. Connect the HX711 to the correct GPIO pins
3. Place a known weight on the load cell
4. Adjust `WEIGHT_REFERENCE_UNIT` until the displayed weight matches the actual weight
5. Set `WEIGHT_OFFSET` to zero out any resting weight reading

---

## 🌐 Connecting Pi to Server

1. Start the Django server on your PC/laptop/server:
   ```bash
   cd EcoBottle/server
   python manage.py runserver 0.0.0.0:8000
   ```

2. Find your server's IP address:
   ```bash
   # Windows
   ipconfig
   # Linux/Mac
   hostname -I
   ```

3. On the Raspberry Pi, edit `rpi_app/config.py`:
   ```python
   SERVER_URL = "http://<YOUR_SERVER_IP>:8000"
   ```

4. Make sure both devices are on the **same network**.

5. Run the Pi app:
   ```bash
   cd EcoBottle/rpi_app
   python3 main.py
   ```

---

## 🎨 Screenshots

The web interface features:
- 🌑 Dark mode with glassmorphism design
- ✨ Animated particle background
- 🔍 Register number lookup with points display
- 📋 Transaction history with staggered animations
- 📱 Fully responsive (works on phone/tablet/desktop)

---

## 📄 License

This project is open source and available for educational purposes.
