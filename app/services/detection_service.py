import os
import cv2
import numpy as np
import uuid
from fastapi import UploadFile
from ultralytics import YOLO

MODEL_PATH = "app/models/best.pt" 
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
        detected_class_names = [] # Kumpulkan untuk mempermudah frontend

        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]
            confidence = round(box.conf[0].item(), 2)
            
            coords = box.xyxy[0].tolist() 
            coords = [round(x, 2) for x in coords]

            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "bounding_box": coords
            })
            
            # Masukkan ke array datar agar frontend mudah mengirimkannya kembali
            if class_name not in detected_class_names:
                detected_class_names.append(class_name)

        img_with_boxes = result.plot()
        filename = f"scan_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        cv2.imwrite(filepath, img_with_boxes)

        return {
            "status": "success",
            "message": "Deteksi selesai",
            "file_name": filename,
            "image_url": f"/static/uploads/{filename}",
            "total_detected": len(detections),
            "detected_class_names": detected_class_names, # Ini yang akan dikirim ke route /insight
            "detections": detections
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}