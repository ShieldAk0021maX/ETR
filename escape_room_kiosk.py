import cv2
import time
import numpy as np
from ultralytics import YOLO
import torch

# ==========================================
# 1. EVENT CONFIGURATION
# ==========================================
MODEL_PATH = "yolov8n.pt"
CONF_THRESHOLD = 0.75 
SCAN_DURATION = 2.0  

SECRET_CODES = {
    "blue_cube": "SIGMA-3",
    "red_cube": "OMEGA-9",
    "cell phone": "GARGANTUA-1", # Temporary test object
    "person": "ENDURANCE-9"      # Temporary test object
}

# ==========================================
# 2. SYSTEM INITIALIZATION
# ==========================================
print("[SYSTEM] Initializing AI Station...")
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Quantum Core Scanner offline.")
    exit()

cv2.namedWindow("AI_STATION", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("AI_STATION", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

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

    frame = cv2.flip(frame, 1)
    results = model(frame, verbose=False)[0]
    detection_active = False

    for box in results.boxes:
        conf = float(box.conf[0])
        if conf >= CONF_THRESHOLD:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            
            # Draw targeting UI (Using Gargantua Amber)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 176, 255), 1) # Thinner line
            
            # TARS style terminal text
            cv2.putText(frame, f"INFERENCE: {conf*100:.0f}%", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 176, 255), 1)

            # If it's a valid puzzle piece
            if class_name in SECRET_CODES:
                detection_active = True
                
                if current_target != class_name:
                    current_target = class_name
                    detect_start_time = time.time()
                
                elapsed = time.time() - detect_start_time
                
                # Visual loading bar
                progress = min(1.0, elapsed / SCAN_DURATION)
                bar_width = int((x2 - x1) * progress)
                cv2.rectangle(frame, (x1, y2 + 10), (x1 + bar_width, y2 + 15), (0, 176, 255), -1)

                # TRIGGER THE REVEAL
                if elapsed >= SCAN_DURATION:
                    revealed_code = SECRET_CODES[class_name]
                    reveal_timer = time.time()
                    current_target = None 

    if not detection_active:
        current_target = None
        detect_start_time = 0

    # ==========================================
    # 4. THE REVEAL OVERLAY (INTERSTELLAR THEME)
    # ==========================================
    if revealed_code and (time.time() - reveal_timer < 5.0):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (5, 5, 5), -1)
        frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)
        
        text1 = "QUANTUM CORE VERIFIED."
        text2 = f"ACCESS CODE: {revealed_code}"
        
        cv2.putText(frame, text1, (50, frame.shape[0]//2 - 50), 
                    cv2.FONT_HERSHEY_PLAIN, 2.5, (170, 170, 170), 2)
        cv2.putText(frame, text2, (50, frame.shape[0]//2 + 50), 
                    cv2.FONT_HERSHEY_PLAIN, 3.5, (0, 176, 255), 3)
    elif revealed_code:
        revealed_code = None 

    if not revealed_code:
        cv2.putText(frame, "ISTE ENDURANCE STATION: AWAITING CORE", (30, 50), 
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (170, 170, 170), 1)

    cv2.imshow("AI_STATION", frame)

    if cv2.waitKey(1) & 0xFF == 27: 
        break

cap.release()
cv2.destroyAllWindows()