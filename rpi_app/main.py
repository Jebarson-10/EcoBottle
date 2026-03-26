"""
EcoBottle Reverse Vending Machine - Raspberry Pi GUI Application

Main application with:
- Live camera stream with bottle detection
- On-screen virtual keyboard for register number input
- Weight measurement and point calculation
- Communication with Django backend via REST API

Usage:
    python main.py
    
On Raspberry Pi, ensure camera and HX711 are connected.
On development machines, runs in mock mode automatically.
"""

import tkinter as tk
from tkinter import font as tkfont
import cv2
import threading
import time
from PIL import Image, ImageTk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from bottle_detector import BottleDetector
from weight_sensor import WeightSensor
import api_client


# ═══════════════════════════════════════════════════════════════
# Color Theme (matching the web app)
# ═══════════════════════════════════════════════════════════════
COLORS = {
    'bg_dark': '#0a0f1a',
    'bg_card': '#111827',
    'bg_input': '#1f2937',
    'border': '#1f2937',
    'text': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'accent_green': '#34d399',
    'accent_cyan': '#06b6d4',
    'accent_emerald': '#10b981',
    'btn_hover': '#2dd4bf',
    'error': '#ef4444',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'key_bg': '#1e293b',
    'key_hover': '#334155',
    'key_special': '#0f766e',
}


class VendingMachineApp:
    """Main GUI application for the reverse vending machine."""

    # ─── Application States ──────────────────────────────────
    STATE_IDLE = "idle"               # Waiting for bottle
    STATE_BOTTLE_DETECTED = "detected"  # Bottle found, enter register number
    STATE_WEIGHING = "weighing"        # Weighing the bottle
    STATE_SUBMITTING = "submitting"    # Sending to server
    STATE_SUCCESS = "success"          # Deposit complete
    STATE_ERROR = "error"             # Something went wrong

    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.configure(bg=COLORS['bg_dark'])

        # Fullscreen on Raspberry Pi, windowed on development
        try:
            self.root.attributes('-fullscreen', True)
        except:
            self.root.geometry("1024x768")

        # Allow Escape to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # ─── State ───────────────────────────────────────────
        self.state = self.STATE_IDLE
        self.register_number = ""
        self.current_weight = 0.0
        self.bottle_detected = False
        self.camera_running = False
        self.cap = None

        # ─── Initialize Components ──────────────────────────
        self.detector = BottleDetector()
        self.weight_sensor = WeightSensor()

        # ─── Fonts ───────────────────────────────────────────
        self.font_title = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.font_large = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.font_medium = tkfont.Font(family="Helvetica", size=14)
        self.font_small = tkfont.Font(family="Helvetica", size=11)
        self.font_key = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.font_status = tkfont.Font(family="Helvetica", size=13, weight="bold")

        # ─── Build GUI ──────────────────────────────────────
        self._build_gui()

        # ─── Start Camera ───────────────────────────────────
        self._start_camera()

    def _build_gui(self):
        """Build the complete GUI layout."""
        # Main container with 2 columns
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        # ─── Left Panel: Camera + Status ────────────────────
        left_panel = tk.Frame(self.root, bg=COLORS['bg_dark'], padx=10, pady=10)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(left_panel, bg=COLORS['bg_card'], padx=16, pady=10)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        tk.Label(
            header, text="♻️ EcoBottle Vending Machine",
            font=self.font_title, fg=COLORS['accent_green'],
            bg=COLORS['bg_card']
        ).pack(side="left")

        # Camera frame
        cam_container = tk.Frame(left_panel, bg=COLORS['border'], padx=2, pady=2)
        cam_container.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        cam_container.grid_rowconfigure(0, weight=1)
        cam_container.grid_columnconfigure(0, weight=1)

        self.camera_label = tk.Label(
            cam_container, bg=COLORS['bg_dark'],
            text="📷 Starting camera...",
            fg=COLORS['text_muted'],
            font=self.font_medium
        )
        self.camera_label.grid(row=0, column=0, sticky="nsew")

        # Status bar
        status_frame = tk.Frame(left_panel, bg=COLORS['bg_card'], padx=16, pady=12)
        status_frame.grid(row=2, column=0, sticky="ew")

        self.status_label = tk.Label(
            status_frame,
            text="⏳ Waiting for bottle...",
            font=self.font_status,
            fg=COLORS['warning'],
            bg=COLORS['bg_card'],
            anchor="w"
        )
        self.status_label.pack(fill="x")

        self.weight_label = tk.Label(
            status_frame,
            text="",
            font=self.font_small,
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_card'],
            anchor="w"
        )
        self.weight_label.pack(fill="x")

        # ─── Right Panel: Input + Keyboard ──────────────────
        right_panel = tk.Frame(self.root, bg=COLORS['bg_dark'], padx=10, pady=10)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(3, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Register number label
        tk.Label(
            right_panel, text="Enter Register Number",
            font=self.font_medium, fg=COLORS['text'],
            bg=COLORS['bg_dark'], pady=8
        ).grid(row=0, column=0, sticky="ew")

        # Register number display
        input_frame = tk.Frame(right_panel, bg=COLORS['accent_green'], padx=2, pady=2)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.reg_display = tk.Label(
            input_frame,
            text="",
            font=self.font_large,
            fg=COLORS['accent_green'],
            bg=COLORS['bg_input'],
            anchor="w",
            padx=16,
            pady=14,
            height=1
        )
        self.reg_display.pack(fill="x")

        # Message display
        self.message_frame = tk.Frame(right_panel, bg=COLORS['bg_card'], padx=16, pady=12)
        self.message_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.message_label = tk.Label(
            self.message_frame,
            text="Insert a plastic bottle to begin",
            font=self.font_small,
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_card'],
            wraplength=350,
            justify="left"
        )
        self.message_label.pack(fill="x")

        # Virtual Keyboard
        self._build_keyboard(right_panel)

        # Action buttons
        btn_frame = tk.Frame(right_panel, bg=COLORS['bg_dark'], pady=8)
        btn_frame.grid(row=4, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.submit_btn = tk.Button(
            btn_frame, text="✅ SUBMIT",
            font=self.font_status,
            fg=COLORS['bg_dark'],
            bg=COLORS['accent_green'],
            activebackground=COLORS['btn_hover'],
            activeforeground=COLORS['bg_dark'],
            padx=20, pady=14,
            bd=0, cursor="hand2",
            command=self._on_submit
        )
        self.submit_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.reset_btn = tk.Button(
            btn_frame, text="🔄 RESET",
            font=self.font_status,
            fg=COLORS['text'],
            bg=COLORS['bg_input'],
            activebackground=COLORS['key_hover'],
            activeforeground=COLORS['text'],
            padx=20, pady=14,
            bd=0, cursor="hand2",
            command=self._on_reset
        )
        self.reset_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _build_keyboard(self, parent):
        """Build the on-screen virtual keyboard."""
        kb_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        kb_frame.grid(row=3, column=0, sticky="nsew", pady=4)
        kb_frame.grid_columnconfigure(tuple(range(10)), weight=1)

        # Keyboard layout
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '⌫'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', '_', ' '],
        ]

        for row_idx, row in enumerate(rows):
            for col_idx, key in enumerate(row):
                is_special = key in ('⌫', ' ')
                bg = COLORS['key_special'] if is_special else COLORS['key_bg']
                display_text = key if key != ' ' else '␣'

                btn = tk.Button(
                    kb_frame,
                    text=display_text,
                    font=self.font_key,
                    fg=COLORS['text'],
                    bg=bg,
                    activebackground=COLORS['key_hover'],
                    activeforeground=COLORS['text'],
                    bd=0,
                    padx=4,
                    pady=10,
                    cursor="hand2",
                    command=lambda k=key: self._on_key_press(k)
                )
                btn.grid(
                    row=row_idx, column=col_idx,
                    sticky="nsew", padx=2, pady=2
                )

                # Hover effects
                btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=COLORS['key_hover']))
                btn.bind('<Leave>', lambda e, b=btn, c=bg: b.configure(bg=c))

    # ─── Camera Handling ─────────────────────────────────────

    def _start_camera(self):
        """Start the camera capture thread."""
        self.camera_running = True
        self.cam_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.cam_thread.start()

    def _camera_loop(self):
        """Continuous camera capture and detection loop."""
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

        if not self.cap.isOpened():
            self.root.after(0, lambda: self._update_status(
                "❌ Camera not found!", COLORS['error']
            ))
            return

        while self.camera_running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            # Run bottle detection
            detections = self.detector.detect(frame)
            self.bottle_detected = len(detections) > 0

            # Draw detections on frame
            if detections:
                frame = self.detector.draw_detections(frame, detections)

            # Draw status overlay
            self._draw_overlay(frame, detections)

            # Convert to PhotoImage and update GUI
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            # Resize to fit the label
            try:
                label_w = self.camera_label.winfo_width()
                label_h = self.camera_label.winfo_height()
                if label_w > 10 and label_h > 10:
                    img = img.resize((label_w, label_h), Image.LANCZOS)
            except:
                pass

            photo = ImageTk.PhotoImage(img)
            self.root.after(0, self._update_camera, photo)

            # Update state based on detection
            if self.state == self.STATE_IDLE and self.bottle_detected:
                self.root.after(0, self._bottle_found)

            time.sleep(0.03)  # ~30 FPS

    def _update_camera(self, photo):
        """Update camera display (must run on main thread)."""
        self.camera_label.configure(image=photo, text="")
        self.camera_label._photo = photo  # Prevent garbage collection

    def _draw_overlay(self, frame, detections):
        """Draw status overlay on the camera frame."""
        h, w = frame.shape[:2]

        # Detection status badge
        if detections:
            text = "BOTTLE DETECTED"
            color = (100, 255, 0)
        else:
            text = "SCANNING..."
            color = (0, 180, 255)

        cv2.rectangle(frame, (10, 10), (240, 45), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (240, 45), color, 2)
        cv2.putText(
            frame, text, (20, 36),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2
        )

    # ─── State Management ────────────────────────────────────

    def _bottle_found(self):
        """Handle bottle detection event."""
        if self.state != self.STATE_IDLE:
            return

        self.state = self.STATE_BOTTLE_DETECTED
        self._update_status("🍶 Bottle detected! Enter your register number.", COLORS['accent_green'])
        self._update_message("Type your register number using the keyboard, then press SUBMIT.")

        # Read weight
        weight = self.weight_sensor.read_weight()
        self.current_weight = weight
        self.weight_label.configure(
            text=f"⚖️ Weight: {weight:.1f}g  →  Points: {weight * config.POINTS_PER_GRAM:.1f}"
        )

    def _on_key_press(self, key):
        """Handle virtual keyboard key press."""
        if key == '⌫':
            self.register_number = self.register_number[:-1]
        elif key == ' ':
            pass  # Ignore spaces
        else:
            if len(self.register_number) < 30:  # Max length
                self.register_number += key

        self.reg_display.configure(text=self.register_number)

    def _on_submit(self):
        """Handle the submit button press."""
        if not self.register_number.strip():
            self._update_message("⚠️ Please enter your register number first!")
            return

        if self.current_weight <= 0 and not config.MOCK_WEIGHT_SENSOR:
            self._update_message("⚠️ No bottle weight detected. Please place the bottle correctly.")
            return

        # If weight is 0 in mock mode, generate one
        if self.current_weight <= 0 and config.MOCK_WEIGHT_SENSOR:
            self.current_weight = self.weight_sensor.read_weight()
            self.weight_label.configure(
                text=f"⚖️ Weight: {self.current_weight:.1f}g  →  Points: {self.current_weight * config.POINTS_PER_GRAM:.1f}"
            )

        self.state = self.STATE_SUBMITTING
        self._update_status("📤 Submitting deposit...", COLORS['accent_cyan'])
        self._update_message("Please wait while we record your deposit...")

        # Submit in background thread
        threading.Thread(
            target=self._submit_deposit,
            daemon=True
        ).start()

    def _submit_deposit(self):
        """Submit deposit to the server (runs in background thread)."""
        result = api_client.submit_deposit(
            register_number=self.register_number,
            weight_grams=self.current_weight
        )

        if result['success']:
            points = result['points_earned']
            total = result['total_points']
            self.root.after(0, lambda: self._show_success(points, total))
        else:
            self.root.after(0, lambda: self._show_error(result['message']))

    def _show_success(self, points_earned, total_points):
        """Display success message."""
        self.state = self.STATE_SUCCESS
        self._update_status("✅ Deposit Successful!", COLORS['success'])
        self._update_message(
            f"🎉 You earned {points_earned:.1f} points!\n"
            f"📊 Total balance: {total_points:.1f} points\n"
            f"💧 Weight: {self.current_weight:.1f}g\n\n"
            f"Check your points anytime at the web portal!"
        )

        # Auto-reset after 8 seconds
        self.root.after(8000, self._on_reset)

    def _show_error(self, message):
        """Display error message."""
        self.state = self.STATE_ERROR
        self._update_status("❌ Error", COLORS['error'])
        self._update_message(f"Error: {message}\n\nPlease try again or contact support.")

    def _on_reset(self):
        """Reset the application to idle state."""
        self.state = self.STATE_IDLE
        self.register_number = ""
        self.current_weight = 0.0
        self.bottle_detected = False

        self.reg_display.configure(text="")
        self.weight_label.configure(text="")
        self._update_status("⏳ Waiting for bottle...", COLORS['warning'])
        self._update_message("Insert a plastic bottle to begin")

    # ─── UI Helpers ──────────────────────────────────────────

    def _update_status(self, text, color):
        """Update the status label."""
        self.status_label.configure(text=text, fg=color)

    def _update_message(self, text):
        """Update the message display."""
        self.message_label.configure(text=text)

    def cleanup(self):
        """Clean up resources."""
        self.camera_running = False
        if self.cap:
            self.cap.release()
        self.weight_sensor.cleanup()


# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 50)
    print("  EcoBottle Reverse Vending Machine")
    print("  Connection: Direct Firebase Firestore")
    print(f"  Mock weight: {config.MOCK_WEIGHT_SENSOR}")
    print(f"  Camera: {config.CAMERA_INDEX}")
    print("=" * 50)

    root = tk.Tk()
    app = VendingMachineApp(root)

    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.cleanup()


if __name__ == "__main__":
    main()
