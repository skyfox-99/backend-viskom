from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# 1. TABEL SCAN HISTORY
# (Ditaruh di atas agar bisa dibaca oleh tabel User di bawahnya)
class ScanHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    class_name: str       
    label: str            
    confidence: float     
    category: str         
    image_url: str        
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relasi ke objek User
    user: "User" = Relationship(back_populates="scans")

# 2. TABEL USER
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relasi balik: mempermudah mengambil semua scan milik user ini
    scans: List[ScanHistory] = Relationship(back_populates="user")