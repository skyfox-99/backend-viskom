import os
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt

# Konfigurasi JWT
SECRET_KEY = os.getenv("SECRET_KEY", "rahasia_negara_jangan_dibocorkan_123!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 Hari

# Inisialisasi Argon2 Password Hasher dengan parameter standar yang aman
ph = PasswordHasher()

def get_password_hash(password: str) -> str:
    """Mengubah plain password menjadi hash Argon2 ID"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi apakah plain password cocok dengan hash di database"""
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        # Jika password salah atau tidak cocok
        return False
    except Exception:
        # Mengantisipasi keerroran sistem lainnya
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt