#!/usr/bin/env python3
"""
ECO COMPANY — Seed Script
Boshlang'ich ma'lumotlarni DB ga yuklash
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.setting import SiteSetting
from app.utils.hashing import hash_password


def seed_admin():
    """Super admin yaratish"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@ecocompany.uz").first()
        if existing:
            print("ℹ️  Admin allaqachon mavjud, o'tkazildi")
            return

        admin = User(
            email="admin@ecocompany.uz",
            password=hash_password("EcoAdmin@2024!"),
            name="Super Admin",
            role="super_admin",
        )
        db.add(admin)
        db.commit()
        print("✅ Super admin yaratildi: admin@ecocompany.uz / EcoAdmin@2024!")
    finally:
        db.close()


def seed_settings():
    """Boshlang'ich sozlamalar"""
    db = SessionLocal()
    try:
        default_settings = [
            ("phone_1", "+998901234567", "text", "Telefon 1", True),
            ("phone_2", "", "text", "Telefon 2", True),
            ("email", "info@ecocompany.uz", "text", "Email", True),
            ("address", "Toshkent, O'zbekiston", "text", "Manzil", True),
            ("working_hours", "Du-Ju: 09:00-18:00", "text", "Ish vaqti", True),
            ("hero_title_uz", "Toza suv — toza hayot", "text", "Hero sarlavha", True),
            ("hero_desc_uz", "ECO COMPANY — yuqori sifatli tozalangan suv", "text", "Hero tavsif", True),
            ("logo_url", "", "image", "Logo", True),
            ("instagram_url", "https://instagram.com/ecocompany", "text", "Instagram", True),
            ("telegram_url", "https://t.me/ecocompany", "text", "Telegram", True),
            ("facebook_url", "", "text", "Facebook", True),
        ]

        count = 0
        for key, value, type_, label, is_public in default_settings:
            existing = db.query(SiteSetting).filter(SiteSetting.key == key).first()
            if not existing:
                db.add(SiteSetting(key=key, value=value, type=type_, label=label, is_public=is_public))
                count += 1

        db.commit()
        print(f"✅ {count} ta sozlama qo'shildi")
    finally:
        db.close()


if __name__ == "__main__":
    print("🌿 ECO COMPANY — Seed boshlandi...")
    seed_admin()
    seed_settings()
    print("🎉 Seed tugadi!")
