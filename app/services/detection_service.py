import os
import cv2
import numpy as np
import uuid
from fastapi import UploadFile
from ultralytics import YOLO

from app.utils.waste_dictionary import WASTE_DICTIONARY

MODEL_PATH = "app/models/best_model.pt" 
UPLOAD_DIR = "app/static/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Peringatan: Gagal memuat model. Error: {e}")
    model = None

async def process_image_and_detect(file: UploadFile):
    if model is None:
        return {"status": "error", "message": "Model YOLO belum tersedia atau path salah."}

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        results = model.predict(img, conf=0.50, imgsz=640) 
        result = results[0]

        detections = []
        detected_class_names = []

        for box in result.boxes:
            class_name = model.names[int(box.cls[0].item())]
            
            dict_info = WASTE_DICTIONARY.get(class_name, {})
            
            detections.append({
                "className": class_name,
                "confidence": round(box.conf[0].item(), 2),
                "box": box.xyxyn[0].tolist(),
                "label": dict_info.get("nama", class_name),
                "category": dict_info.get("kategori", "Unknown"),
                "action": dict_info.get("action", "Tidak ada panduan"),
                "impact": dict_info.get("konteks", "")
            })
            
            if class_name not in detected_class_names:
                detected_class_names.append(class_name)

        if not detections:
            return {
                "status": "not_found",
                "message": "Gambar tidak terdeteksi sebagai sampah plastik yang dikenali.",
                "allDetections": [],
                "detected_class_names": []
            }
            
        img_with_boxes = result.plot()
        filename = f"scan_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        cv2.imwrite(filepath, img_with_boxes)

        return {
            "status": "success",
            "message": "Deteksi selesai",
            "file_name": filename,
            "image_url": f"/static/uploads/{filename}",
            "totalDetected": len(detections),
            "detected_class_names": detected_class_names, 
            "allDetections": detections
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}