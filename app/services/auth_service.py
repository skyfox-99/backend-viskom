import os
from fastapi import HTTPException
from sqlmodel import Session, select
from google.oauth2 import id_token
from google.auth.transport import requests

from app.models.user import User
from app.utils.security import get_password_hash, verify_password, create_access_token

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class AuthService:
    
    @staticmethod
    def register_user(session: Session, username: str, email: str, password: str):
        # 1. Cek apakah user sudah ada
        existing_user = session.exec(select(User).where((User.username == username) | (User.email == email))).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username atau Email sudah terdaftar")
        
        # 2. Simpan user baru
        new_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            auth_provider="local"
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        return {"status": "success", "message": "Registrasi berhasil"}

    @staticmethod
    def login_user(session: Session, username: str, password: str):
        # 1. Cari user di DB
        user = session.exec(select(User).where(User.username == username)).first()
        
        # 2. Verifikasi
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Username atau Password salah")
        
        # 3. Buat Token
        access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
        
        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }

    @staticmethod
    def google_login(session: Session, token: str):
        try:
            # 1. Validasi token ke server Google
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            
            email = idinfo['email']
            name = idinfo.get('name', email.split('@')[0])
            
            # 2. Cek user di DB
            user = session.exec(select(User).where(User.email == email)).first()
            
            # 3. Auto-Register jika belum ada
            if not user:
                base_username = name.replace(" ", "").lower()
                user = User(
                    username=f"{base_username}_{str(idinfo['sub'])[:4]}", 
                    email=email,
                    auth_provider="google"
                )
                session.add(user)
                session.commit()
                session.refresh(user)

            # 4. Buat Token
            access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
            
            return {
                "status": "success",
                "access_token": access_token,
                "token_type": "bearer",
                "user": {"id": user.id, "username": user.username, "email": user.email}
            }
            
        except ValueError:
            raise HTTPException(status_code=401, detail="Token Google tidak valid atau sudah kadaluarsa")