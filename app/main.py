from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import detection_route
import os

app = FastAPI(title="API Deteksi Gambar")

# Pastikan path absolut/relatif sesuai
os.makedirs("app/static/uploads", exist_ok=True)

# Membuka folder 'static' agar gambar bisa diakses melalui URL browser
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Daftarkan router dari detection_route.py
app.include_router(detection_route.router, prefix="/api", tags=["Detection"])

@app.get("/")
def read_root():
    return {"message": "Server FastAPI berjalan dengan lancar!"}