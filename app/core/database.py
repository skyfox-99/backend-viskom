import os
from sqlmodel import Session, create_engine, SQLModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecovision.db")

# Membuat 'mesin' yang menghubungkan aplikasi ke database
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    # Ini akan mencari semua model yang sudah ter-import dan membuat tabelnya
    SQLModel.metadata.create_all(engine)