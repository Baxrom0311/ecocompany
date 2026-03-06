"""
ECO COMPANY — Admin foydalanuvchi yaratish skripti
Ishga tushirish: python scripts/create_admin.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.utils.hashing import hash_password

def create_admin():
    db = SessionLocal()
    try:
        email = "admin@ecocompany.uz"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"⚠️  Admin allaqachon mavjud: {existing.email} (role: {existing.role})")
            return

        user = User(
            email=email,
            password=hash_password("admin123"),
            name="Baxrom Admin",
            role="super_admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"✅ Admin yaratildi!")
        print(f"   📧 Email: {email}")
        print(f"   🔑 Parol: admin123")
        print(f"   👑 Role: super_admin")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
