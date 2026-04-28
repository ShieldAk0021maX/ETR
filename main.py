import cv2
import time
import numpy as np
from ultralytics import YOLO
import torch

# ==========================================
# 1. EVENT CONFIGURATION
# ==========================================
# Path to your trained model (after you feed it the DIY cube images)
MODEL_PATH = "yolov8n.pt"

# Confidence required to trigger the reveal (75% prevents false alarms)
CONF_THRESHOLD = 0.75 

# How long teams must hold the cube steady (in seconds) to build suspense
SCAN_DURATION = 2.0  

# Map your YOLO class names to the Escape Room secret codes
# Make sure these keys match the exact class names in your data_config.yaml
SECRET_CODES = {
    "blue_cube": "SIGMA-3",
    "red_cube": "OMEGA-9",
    "green_cube": "DELTA-7"
}

# ==========================================
# 2. SYSTEM INITIALIZATION
# ==========================================
print("[SYSTEM] Initializing AI Station...")
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Quantum Core Scanner (Webcam) offline.")
    exit()

# Set up Fullscreen for maximum immersion
cv2.namedWindow("AI_STATION", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("AI_STATION", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Tracking variables
detect_start_time = 0
current_target = None
revealed_code = None
reveal_timer = 0

print("[SYSTEM] Station Online. Awaiting Quantum Cores.")

# ==========================================
# 3. THE MAIN EVENT LOOP
# ==========================================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally like a mirror so it's easier for teams to aim
    frame = cv2.flip(frame, 1)
    
    # Run Inference
    results = model(frame, verbose=False)[0]
    
    detection_active = False

    for box in results.boxes:
        conf = float(box.conf[0])
        if conf >= CONF_THRESHOLD:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            
            # Draw targeting UI
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, f"ANALYZING: {conf*100:.0f}%", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # If it's a valid puzzle piece
            if class_name in SECRET_CODES:
                detection_active = True
                
                # Start or continue the scanning timer
                if current_target != class_name:
                    current_target = class_name
                    detect_start_time = time.time()
                
                # Calculate how long it has been scanning
                elapsed = time.time() - detect_start_time
                
                # Visual loading bar
                progress = min(1.0, elapsed / SCAN_DURATION)
                bar_width = int((x2 - x1) * progress)
                cv2.rectangle(frame, (x1, y2 + 10), (x1 + bar_width, y2 + 20), (0, 255, 0), -1)

                # TRIGGER THE REVEAL
                if elapsed >= SCAN_DURATION:
                    revealed_code = SECRET_CODES[class_name]
                    reveal_timer = time.time()
                    current_target = None # Reset so it doesn't trigger infinitely

    # Reset scan timer if the team drops the cube
    if not detection_active:
        current_target = None
        detect_start_time = 0

    # ==========================================
    # 4. THE REVEAL OVERLAY
    # ==========================================
    # Flash the code on screen for 5 seconds after a successful scan
    if revealed_code and (time.time() - reveal_timer < 5.0):
        # Create a semi-transparent black background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Display the Access Code
        text1 = "QUANTUM CORE VERIFIED."
        text2 = f"ACCESS CODE: {revealed_code}"
        
        # Center the text
        cv2.putText(frame, text1, (50, frame.shape[0]//2 - 50), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(frame, text2, (50, frame.shape[0]//2 + 50), 
                    cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 255, 255), 4)
    elif revealed_code:
        revealed_code = None # Clear after 5 seconds

    # Add standard "Standby" UI
    if not revealed_code:
        cv2.putText(frame, "AI STATION: AWAITING CORE SCAN", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show the final image
    cv2.imshow("AI_STATION", frame)

    # Emergency exit for the event admin (Press 'Esc')
    if cv2.waitKey(1) & 0xFF == 27: 
        break

cap.release()
cv2.destroyAllWindows()