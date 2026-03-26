"""
Bottle Detection using OpenCV DNN with MobileNet SSD.
Detects 'bottle' class from COCO-trained model.
"""
import cv2
import numpy as np
import config

# COCO class labels (MobileNet SSD)
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow",
    "diningtable", "dog", "horse", "motorbike", "person",
    "pottedplant", "sheep", "sofa", "train", "tvmonitor"
]

# Index of 'bottle' in COCO classes
BOTTLE_CLASS_ID = CLASSES.index("bottle")


class BottleDetector:
    def __init__(self):
        """Initialize the bottle detector with MobileNet SSD model."""
        self.net = None
        self.confidence_threshold = config.DETECTION_CONFIDENCE
        self._load_model()

    def _load_model(self):
        """Load the MobileNet SSD model from OpenCV's built-in models."""
        try:
            # Use OpenCV's DNN module with a pre-trained MobileNet SSD
            # These are the standard Caffe model files for MobileNet-SSD
            prototxt_url = "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt"
            model_url = "https://drive.google.com/uc?export=download&id=0B3gersZ2cHIxRm5PMWRoTkdHdHc"

            # Try to load from local files first
            import os
            model_dir = os.path.dirname(os.path.abspath(__file__))
            prototxt_path = os.path.join(model_dir, "deploy.prototxt")
            model_path = os.path.join(model_dir, "mobilenet_iter_73000.caffemodel")

            if os.path.exists(prototxt_path) and os.path.exists(model_path):
                self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
                print("[INFO] Loaded MobileNet SSD model from local files.")
            else:
                print("[WARNING] Model files not found locally.")
                print(f"  Please download:")
                print(f"  1. deploy.prototxt -> {prototxt_path}")
                print(f"  2. mobilenet_iter_73000.caffemodel -> {model_path}")
                print("[INFO] Running in basic detection mode (color-based).")
                self.net = None

        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            print("[INFO] Running in basic detection mode (color-based).")
            self.net = None

    def detect(self, frame):
        """
        Detect bottles in the given frame.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            list of dicts with 'bbox' (x1, y1, x2, y2), 'confidence', 'label'
        """
        if frame is None:
            return []

        detections = []

        if self.net is not None:
            detections = self._detect_dnn(frame)
        else:
            detections = self._detect_basic(frame)

        return detections

    def _detect_dnn(self, frame):
        """Detect using DNN model."""
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            0.007843, (300, 300), 127.5
        )
        self.net.setInput(blob)
        output = self.net.forward()

        detections = []
        for i in range(output.shape[2]):
            confidence = output[0, 0, i, 2]
            class_id = int(output[0, 0, i, 1])

            if confidence > self.confidence_threshold and class_id == BOTTLE_CLASS_ID:
                box = output[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype("int")

                # Clamp to frame boundaries
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': float(confidence),
                    'label': 'bottle'
                })

        return detections

    def _detect_basic(self, frame):
        """
        Basic bottle detection using contour analysis.
        Fallback when DNN model is not available.
        Looks for tall, narrow objects which are typical bottle shapes.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        edges = cv2.Canny(blurred, 30, 100)

        # Dilate to close gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        h, w = frame.shape[:2]
        min_area = (h * w) * 0.02  # At least 2% of frame

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = bh / max(bw, 1)

            # Bottles are typically taller than wide (aspect ratio > 1.5)
            if aspect_ratio > 1.5 and aspect_ratio < 6.0:
                # Check solidity (filled vs convex hull)
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = area / max(hull_area, 1)

                if solidity > 0.3:
                    confidence = min(0.9, solidity * aspect_ratio / 5.0)
                    if confidence > self.confidence_threshold:
                        detections.append({
                            'bbox': (x, y, x + bw, y + bh),
                            'confidence': confidence,
                            'label': 'bottle'
                        })

        return detections

    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on the frame."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            label = f"Bottle: {conf:.0%}"

            # Green bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 100), 3)

            # Label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(
                frame,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                (0, 255, 100), -1
            )
            cv2.putText(
                frame, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2
            )

        return frame
