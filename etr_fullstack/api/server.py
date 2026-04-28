from pathlib import Path
from typing import Any

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

APP_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = APP_ROOT / "assets"
# Reuse the existing model from the original workspace root.
MODEL_PATH = APP_ROOT.parent.parent / "yolov8n.pt"

GARGANTUA_AMBER_BGR = (0, 176, 255)
CONF_THRESHOLD = 0.75

SECRET_CODES = {
    "blue_cube": "SIGMA-3",
    "red_cube": "OMEGA-9",
    "cell phone": "GARGANTUA-1",
    "person": "ENDURANCE-9",
}


def tars_line(message: str) -> str:
    return f"[TARS]: {message}"


print("[SYSTEM] Booting Endurance Mainframe...")
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

MODEL = YOLO(str(MODEL_PATH))
print(tars_line("Model loaded once. Scanner online."))

app = FastAPI(title="Escape The Room API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": MODEL_PATH.name}


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload must be an image file.")

    payload = await file.read()
    np_buffer = np.frombuffer(payload, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode uploaded image.")

    results = MODEL(image, verbose=False)[0]

    detections: list[dict[str, Any]] = []
    best_conf = 0.0
    best_class = "UNKNOWN"

    for box in results.boxes:
        conf = float(box.conf[0])
        class_id = int(box.cls[0])
        class_name = str(MODEL.names[class_id])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

        if conf > best_conf:
            best_conf = conf
            best_class = class_name

        detections.append(
            {
                "class": class_name,
                "confidence": round(conf, 4),
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            }
        )

        # Draw Gargantua Amber target lines in backend processing context.
        cv2.rectangle(image, (x1, y1), (x2, y2), GARGANTUA_AMBER_BGR, 2)

    if best_conf >= CONF_THRESHOLD and best_class in SECRET_CODES:
        terminal_output = tars_line(
            f"Target verified. Match: {best_class.upper()}. Confidence: {best_conf * 100:.0f}%."
        )
        access_code = SECRET_CODES[best_class]
    elif detections:
        terminal_output = tars_line(
            f"Object recognized ({best_class.upper()}), but no valid Quantum Core confirmation."
        )
        access_code = "ACCESS DENIED"
    else:
        terminal_output = tars_line("No target detected. Awaiting visual input.")
        access_code = "NO TARGET"

    print(terminal_output)

    return {
        "success": True,
        "access_code": access_code,
        "terminal": terminal_output,
        "count": len(detections),
        "detections": detections,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
