import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from app.utils.waste_dictionary import WASTE_DICTIONARY

# Load variabel dari .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Peringatan: API_KEY tidak ditemukan di file .env")

# 1. PERBAIKAN MODEL: Gunakan 1.5-flash atau 2.0-flash (Jangan 2.5)
model = genai.GenerativeModel('gemini-2.5-flash')

async def generate_waste_insight(detected_classes: list) -> dict:
    print("\n" + "="*40)
    print(f"🔍 DEBUG GEN AI: DIMULAI")
    print(f"📦 Input mentah dari YOLO/Frontend: {detected_classes}")
    
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
    print(f"🎯 Target Edukasi yang Dikunci: {item_names_str}")

    # 2. PROMPT SUPER KETAT: Memaksa fokus 100% pada benda target
    prompt = f"""
    kamu adalah seorang pakar tentang ilmu lingkungan, sistem mendeteksi sebuah sampah plastik: "{item_names_str}".
    
    Konteks Spesifik Benda:
    {waste_context}

    ATURAN MUTLAK:
    1. Kamu DILARANG KERAS membahas benda lain selain "{item_names_str}".
    2. Jika kamu membahas tali, botol, atau kresek (padahal tidak ada di target edukasi), kamu dianggap gagal.
    3. Output HANYA berupa JSON murni, tanpa awalan ```json dan akhiran ```.
    
    Format JSON:
    {{
        "ringkasan_bahaya": "Bahaya utama dari {item_names_str} bagi lingkungan hidup.",
        "ide_daur_ulang": [
            "Satu ide kreatif mendaur ulang {item_names_str}",
            "Ide kreatif kedua untuk mendaur ulang {item_names_str}"
        ],
        "fakta_menarik": "Fakta mencengangkan tentang {item_names_str}"
    }}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                # 3. TEMPERATURE PALING RENDAH (0.1): Mematikan imajinasi AI agar 100% patuh pada prompt
                temperature=0.1, 
            ),
        )
        
        print(f"🤖 Respons Mentah Gemini: {response.text.strip()}")
        print("="*40 + "\n")
        
        ai_result = json.loads(response.text)
        return ai_result

    except Exception as e:
        print(f"❌ Error GenAI: {e}")
        return {
            "status": "error",
            "message": "Gagal menghasilkan insight edukasi.",
            "insights": []
        }