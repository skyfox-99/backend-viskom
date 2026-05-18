import os
import json
from google import genai
from google.genai import types  # Diperlukan untuk konfigurasi SDK baru
from dotenv import load_dotenv
from app.utils.waste_dictionary import WASTE_DICTIONARY

# 1. Load variabel lingkungan
load_dotenv()

API_KEY = os.getenv("API_KEY")

# 2. Inisialisasi Client SDK Baru (google-genai)
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("❌ Peringatan: API_KEY tidak ditemukan di file .env")
    client = genai.Client() 

async def generate_waste_insight(detected_classes: list) -> dict:

    if not detected_classes:
        return {
            "status": "success",
            "message": "Tidak ada sampah plastik yang terdeteksi.",
            "insights": []
        }
        
    unique_classes = list(set(detected_classes))
    item_names = []
    waste_context = ""
    
    for cls in unique_classes:
        if cls in WASTE_DICTIONARY:
            data = WASTE_DICTIONARY[cls]
            item_names.append(data['nama'])
            waste_context += f"- {data['nama']}: {data['konteks']}\n"
            
    if not item_names:
        item_names = unique_classes
        waste_context = ", ".join(unique_classes)
        
    item_names_str = ", ".join(item_names)

    # 3. PROMPT SUPER KETAT & EDUKATIF
    prompt = f"""
    kamu berperan sebagai seorang dr ecovision, sebuah sistem AI yang sangat ahli dalam memberikan edukasi tentang sampah plastik berdasarkan jenisnya. 
    Sistem AI kami baru saja mendeteksi jenis sampah: "{item_names_str}".

    Konteks Spesifik Benda (Gunakan informasi ini sebagai acuan utama):
    {waste_context}

    PERAN KAMU:
    - Memberikan insight edukasi yang akurat, ringkas, dan dapat ditindaklanjuti
    tentang sampah plastik yang terdeteksi oleh sistem AI.
    - Menjadi jembatan antara deteksi teknologi dan kesadaran lingkungan pengguna.

    ATURAN MUTLAK:
    1. FOKUS: Hanya bahas tentang "{item_names_str}". Dilarang keras membahas jenis sampah lain yang tidak relevan.
    2. GAYA BAHASA: Gunakan bahasa Indonesia yang santai, edukatif, dan langsung ke intinya (tidak terlalu kaku).
    3. Ide daur ulang harus PRAKTIS dan bisa dilakukan di rumah tangga.
    4. Fakta harus berdasarkan data nyata (bukan perkiraan).
    5. STRUKTUR: Output HARUS MURNI berupa JSON valid. Jangan tambahkan penjelasan apapun sebelum atau sesudah JSON. Jangan gunakan awalan markdown ```json.

    FORMAT JSON YANG WAJIB DIGUNAKAN:
    {{
        "ringkasan_bahaya": "buat dalam bentuk paragraf, Satu paragraf (2-3 kalimat) menjelaskan dampak lingkungan spesifik dari {item_names_str}. Sebutkan angka atau data konkret jika relevan.",
        "cara_buang": "Satu kalimat panduan praktis ke mana atau bagaimana sampah ini harus dibuang secara ideal.",
        "ide_daur_ulang": [
            "Ide praktis pertama: langkah singkat cara mendaur ulang atau memanfaatkan kembali {item_names_str} di rumah",
            "Ide praktis kedua: alternatif lain yang berbeda dari ide pertama"
        ],
        "fakta_menarik": "Satu fakta mengejutkan dan spesifik tentang {item_names_str} — berikan angka, durasi, atau perbandingan yang membuat pembaca berpikir."
        "tingkat_bahaya": "rendah | sedang | tinggi",
        "dapat_didaur_ulang": true atau false
    }}
    """

    try:
        # 4. Pemanggilan Model dengan Sintaks SDK Baru
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            # Menggunakan types.GenerateContentConfig pada SDK baru
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Mengunci imajinasi AI agar patuh pada prompt & kamus
            ),
        )
        
        ai_result = json.loads(response.text)
        return ai_result
        
    except Exception as e:
        print(f"❌ Error GenAI: {e}")
        return {
            "status": "error",
            "message": "Gagal menghasilkan insight edukasi.",
            "insights": []
        }