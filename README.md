# 🌱 EcoBottle — Firebase Cloud Vending System

A complete plastic bottle recycling rewards system migrated to **Firebase**. Zero server setup required — the backend runs entirely on Google's cloud infrastructure (Firestore + Hosting).

- **Web Dashboard** — Beautiful, glassmorphic UI hosted on Firebase Hosting.
- **Raspberry Pi App** — Graphical vending machine app with camera bottle detection and Firestore integration.

---

## 📂 Project Structure

```
EcoBottle/
├── web/                 # Web dashboard (Static HTML/JS)
│   ├── index.html       # The premium UI dashboard
│   ├── style.css        # Glassmorphic dark-mode styles
│   ├── script.js        # Firebase logic (Firestore reads)
│   └── firebase-config.js # YOUR PROJECT CONFIG HERE
│
├── rpi_app/             # Raspberry Pi vending machine app
│   ├── main.py          # GUI application (Tkinter)
│   ├── bottle_detector.py  # OpenCV bottle detection
│   ├── weight_sensor.py    # HX711 weight sensor driver
│   ├── api_client.py       # Firestore integration (Admin SDK)
│   ├── config.py           # Configuration (path to JSON key)
│   ├── requirements.txt    # Pi dependencies
│   └── serviceAccountKey.json # PLACE YOUR SERVICE ACCOUNT KEY HERE
│
├── firebase.json        # Firebase Hosting & Hosting rules
├── firestore.rules      # Database security rules
└── .firebaserc          # Repository project settings
```

---

## 🔥 Step 1: Firebase Project Setup

1. **Create Project**: Go to [Firebase Console](https://console.firebase.google.com/) and create a new project named **`EcoBottle`**.
2. **Enable Firestore**:
   - Go to **Build > Firestore Database**.
   - Click **Create Database**.
   - Choose a location and select **Test Mode** (or Production, then use the rules in `firestore.rules`).
3. **Register Web App**:
   - In Project Overview, click the **Web icon (`</>`)**.
   - Name it `EcoBottle Web`, register it.
   - Copy the `firebaseConfig` object — you'll need it for Step 2.
4. **Generate Service Account Key**:
   - Go to **Project Settings (齿轮) > Service accounts**.
   - Click **Generate new private key** (JSON file).
   - This file is for your Raspberry Pi.

---

## 🖥️ Step 2: Web Dashboard Setup (Zero Server!)

1. **Configure**: Open `web/firebase-config.js` and paste the `firebaseConfig` object you copied earlier.
2. **Deploy to Cloud**:
   ```bash
   # Install Firebase tools if you haven't
   npm install -g firebase-tools
   
   # Log in
   firebase login
   
   # Initialize and Deploy
   firebase deploy
   ```
   *Your site is now live at `https://your-project-id.web.app`!*

---

## 🍇 Step 3: Raspberry Pi App Setup

1. **Key File**: Move the JSON service account key you downloaded in Step 1 into the `rpi_app/` folder. Rename it to `serviceAccountKey.json`.
2. **Install**:
   ```bash
   cd rpi_app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # On Pi hardware, install GPIO libs
   pip install RPi.GPIO hx711
   ```
3. **Run**:
   ```bash
   python3 main.py
   ```

---

## ⚙️ Configuration Hints

- **Weights**: Calibrate your load cell in `rpi_app/config.py` by adjusting `WEIGHT_REFERENCE_UNIT`.
- **Points**: Point rate is controlled in `rpi_app/api_client.py` and `rpi_app/config.py`. Currently `1 point per 10g`.
- **Security**: The `firestore.rules` allow anyone to **read** the data (for the dashboard) but prevent anyone from **writing** via the client (only your Pi with the service key can write).

---

## 📄 License
This project is for educational use and is free to modify.
