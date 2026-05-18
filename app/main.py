import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import detection_route

app = FastAPI(title="EcoVision API Deteksi Gambar")

# Menggunakan "*" agar fitur html2canvas (export gambar) tidak diblokir oleh CORS
origins = [
    "http://localhost:5173",      
    "http://127.0.0.1:5173",
    "https://frontend-ecovision.vercel.app/"
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],              
    allow_headers=[
        "Content-Type",
        "Authorization",     
        "Accept",
        "X-Requested-With",
        "X-CSRF-Token"       
    ],
    max_age=600, 
)

# Hanya menyambungkan rute deteksi (YOLO + Gemini API)
app.include_router(detection_route.router, prefix="/api", tags=["Detection"])

# Memastikan folder upload ada, lalu membuka folder static ke publik
os.makedirs("app/static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Server FastAPI EcoVision berjalan dengan lancar!"}