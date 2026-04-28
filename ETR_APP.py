import gradio as gr
from ultralytics import YOLO
import cv2
import os
import uuid
import time

# ==========================================
# 1. INITIALIZATION & MLOPS SETUP
# ==========================================
print("[SYSTEM] Booting Endurance Mainframe...")
model = YOLO("yolov8n.pt") 

TRAINING_DIR = "needs_training"
os.makedirs(TRAINING_DIR, exist_ok=True)

SECRET_CODES = {
    "blue_cube": "SIGMA-3",
    "red_cube": "OMEGA-9",
    "cell phone": "GARGANTUA-1", 
    "person": "ENDURANCE-9"      
}

# ==========================================
# 2. THE SCANNING & LEARNING LOGIC
# ==========================================
def scan_core(image, current_log):
    if image is None:
        return None, "NO TARGET", current_log + "\n[TARS]: Error. Camera offline."

    # Run AI Inference
    results = model(image, verbose=False)[0]
    
    best_conf = 0.0
    detected_code = "ACCESS DENIED"
    target_class = "UNKNOWN"

    # Find the most confident object
    for box in results.boxes:
        conf = float(box.conf[0])
        if conf > best_conf:
            best_conf = conf
            class_id = int(box.cls[0])
            target_class = model.names[class_id]

    # --- THE CONTINUOUS LEARNING LOOP ---
    if best_conf < 0.75:
        # Save confusing images for retraining later
        file_id = uuid.uuid4().hex[:8]
        cv2.imwrite(f"{TRAINING_DIR}/low_conf_{file_id}.jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        new_log = current_log + f"\n[TARS]: Scan failed. Confidence too low ({best_conf*100:.0f}%). Image saved to data banks for retraining."
        return image, detected_code, new_log

    # If successful, check if it's a game object
    if target_class in SECRET_CODES:
        detected_code = SECRET_CODES[target_class]
        new_log = current_log + f"\n[TARS]: Target verified. Match: {target_class.upper()}. Confidence: {best_conf*100:.0f}%."
        
        # Draw the Amber targeting box on the image
        for box in results.boxes:
            if float(box.conf[0]) == best_conf:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 176, 255), 3) # Gargantua Amber (RGB for Gradio)
                
        return image, detected_code, new_log
    else:
        new_log = current_log + f"\n[TARS]: Object recognized ({target_class.upper()}), but is not a valid Quantum Core."
        return image, detected_code, new_log

# ==========================================
# 3. INTERSTELLAR UI/UX (CUSTOM CSS)
# ==========================================
interstellar_css = """
/* Force Deep Space Black & Gargantua Amber */
body, .gradio-container { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
* { border-color: #333333 !important; }

/* Styling text and inputs */
span, p, h1, h2, h3 { color: #aaaaaa !important; }
.box, textarea, input { background-color: #0a0a0a !important; color: #ffb000 !important; }

/* The Scan Button */
.primary-btn { 
    background: transparent !important; 
    border: 2px solid #ffb000 !important; 
    color: #ffb000 !important; 
    font-weight: bold !important; 
    letter-spacing: 3px !important; 
    transition: all 0.3s;
}
.primary-btn:hover { background: #ffb000 !important; color: #050505 !important; }

/* Header Formatting */
.header-container { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px dashed #aaaaaa; margin-bottom: 20px;}
.header-logo { color: #aaaaaa; font-weight: bold; letter-spacing: 2px; border: 1px dashed #aaaaaa; padding: 5px 10px; }
.header-title { color: #ffb000; font-size: 24px; letter-spacing: 5px; }

/* Highlight the Access Code */
#access-code textarea { font-size: 30px !important; text-align: center !important; font-weight: bold !important; text-shadow: 0 0 10px #ffb000 !important; }
"""

# ==========================================
# 4. GRADIO BLOCKS LAYOUT
# ==========================================
with gr.Blocks(css=interstellar_css, theme=gr.themes.Base()) as interface:
    
    # Custom Header with Logos
    gr.HTML("""
    <div class="header-container">
        <div class="header-logo">TRIVENI 2026</div>
        <div class="header-title">STATION: ENDURANCE</div>
        <div class="header-logo">ISTE BITS</div>
    </div>
    """)
    
    with gr.Row():
        # LEFT COLUMN: Scanner
        with gr.Column(scale=2):
            camera = gr.Image(sources=["webcam"], label="HUD Scanner Feed", type="numpy")
            scan_btn = gr.Button("INITIATE SCAN", elem_classes=["primary-btn"])
            
        # RIGHT COLUMN: TARS Terminal & Result
        with gr.Column(scale=1):
            access_code_out = gr.Textbox(label="ACCESS CODE", value="AWAITING CORE...", interactive=False, elem_id="access-code")
            tars_terminal = gr.Textbox(
                label="TARS DIAGNOSTICS", 
                value="[TARS]: System online.\n[TARS]: Awaiting visual input...", 
                lines=12, 
                interactive=False
            )

    # Wire the button to the logic
    # Inputs: The camera frame, and the current text inside the TARS terminal
    # Outputs: The drawn image, the access code, and the updated TARS terminal text
    scan_btn.click(
        fn=scan_core,
        inputs=[camera, tars_terminal],
        outputs=[camera, access_code_out, tars_terminal]
    )

if __name__ == "__main__":
    interface.launch()