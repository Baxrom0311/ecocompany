"""
ECO COMPANY — Manual Database Seeder Script
Ishga tushirish: python init_db.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal, engine, Base
from app.services.init_data import seed_initial_data

if __name__ == "__main__":
    print("🌿 ECO COMPANY: Baza strukturasini tekshirish va ma'lumotlarni yuklash...")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_initial_data(db)
    print("✨ Baza muvaffaqiyatli tayyorlandi!")
