import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import detection_route

app = FastAPI(title="API Deteksi Gambar")

origins = [
    # Akses Lokal (Development)   
    "http://localhost:5173",      # Jika frontend pakai Vite (Vue/React modern)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    # PENTING: Tambahkan "OPTIONS" agar browser bisa melakukan preflight check
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],              
    allow_headers=[
        "Content-Type",
        "Authorization",     
        "Accept",
        "X-Requested-With",
        "X-CSRF-Token"       
    ],
    # PENTING: max_age dimasukkan ke dalam sini, bukan menggantung di luar
    max_age=600, 
)

# Pastikan path absolut/relatif sesuai
os.makedirs("app/static/uploads", exist_ok=True)

# Membuka folder 'static' agar gambar bisa diakses melalui URL browser
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Daftarkan router dari detection_route.py
app.include_router(detection_route.router, prefix="/api", tags=["Detection"])

@app.get("/")
def read_root():
    return {"message": "Server FastAPI berjalan dengan lancar!"}