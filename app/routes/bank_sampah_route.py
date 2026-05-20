import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Path menuju file json
JSON_PATH = "app/utils/bank_sampah.json"

# route untuk mendapatkan semua data bank sampah
@router.get("/bank-sampah")
def get_all_bank_sampah():
    if not os.path.exists(JSON_PATH):
        raise HTTPException(status_code=404, detail="File data bank sampah tidak ditemukan.")
        
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return {
            "status": "success",
            "total": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca data: {str(e)}")