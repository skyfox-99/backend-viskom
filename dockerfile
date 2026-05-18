# 1. Gunakan OS Linux + Python 3.11 yang super ringan
FROM python:3.11-slim

# 2. Set folder kerja di dalam server
WORKDIR /app

# 3. MENGHANCURKAN ERROR libxcb: Instal komponen grafis Linux secara paksa
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libxext6 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Trik Paranoid: Pastikan YOLO tidak membawa opencv-python yang salah
RUN pip uninstall -y opencv-python || true
RUN pip install opencv-python-headless==4.13.0.92

# 6. Copy seluruh kode aplikasi (folder app/, dll) ke dalam server
COPY . .

# 7. Jalankan FastAPI dengan port dinamis dari Railway
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]