"""
ECO COMPANY — Initial Database Seeder
Yangi bazada avtomatik super_admin, boshlang'ich kategoriyalar va sayt sozlamalarini yaratish
"""
import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.setting import SiteSetting
from app.models.category import Category
from app.utils.hashing import hash_password

logger = logging.getLogger("ecocompany.init")


def seed_initial_data(db: Session) -> None:
    """Agar baza bo'sh bo'lsa, birlamchi ma'lumotlarni xavfsiz yaratish."""
    try:
        # 1. Super Admin yaratish (agar user bo'lmasa)
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("🌱 Yangi baza aniqlandi: Super Admin foydalanuvchisi yaratilmoqda...")
            admin_user = User(
                email="admin@ecocompany.uz",
                password=hash_password("Admin123!"),
                name="Boshqaruvchi Admin",
                role="super_admin",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info("✅ Standart Super Admin yaratildi: admin@ecocompany.uz / Admin123!")

        # 2. Boshlang'ich Sayt Sozlamalari (agar sozlamalar bo'lmasa)
        setting_count = db.query(SiteSetting).count()
        if setting_count == 0:
            logger.info("🌱 Boshlang'ich sayt sozlamalari yaratilmoqda...")
            default_settings = [
                {"key": "site_name", "value": "ECO COMPANY", "type": "text", "label": "Sayt nomi", "is_public": True},
                {"key": "phone_1", "value": "+998 71 200 00 00", "type": "text", "label": "Asosiy telefon", "is_public": True},
                {"key": "phone_2", "value": "+998 90 123 45 67", "type": "text", "label": "Qo'shimcha telefon", "is_public": True},
                {"key": "email", "value": "info@ecocompany.uz", "type": "text", "label": "Elektron pochta", "is_public": True},
                {"key": "working_hours", "value": "09:00 - 18:00 (Dush - Shan)", "type": "text", "label": "Ish vaqti", "is_public": True},
                {"key": "address_uz", "value": "Toshkent shahri, O'zbekiston", "type": "text", "label": "Manzil (UZ)", "is_public": True},
                {"key": "address_ru", "value": "г. Ташкент, Узбекистан", "type": "text", "label": "Manzil (RU)", "is_public": True},
                {"key": "address_en", "value": "Tashkent city, Uzbekistan", "type": "text", "label": "Manzil (EN)", "is_public": True},
                {"key": "hero_title_uz", "value": "Tabiiy va toza tog' suvi", "type": "text", "label": "Bosh sahifa sarlavha (UZ)", "is_public": True},
                {"key": "hero_subtitle_uz", "value": "Har bir tomchida hayot nafasi", "type": "text", "label": "Bosh sahifa matn (UZ)", "is_public": True},
                {"key": "about_text_uz", "value": "ECO COMPANY — sifatli va ekologik toza ichimlik suvi yetkazib beruvchi kompaniya.", "type": "text", "label": "Kompaniya haqida (UZ)", "is_public": True},
            ]
            for s in default_settings:
                db.add(SiteSetting(**s))
            db.commit()
            logger.info("✅ Boshlang'ich sozlamalar yaratildi")

        # 3. Boshlang'ich Kategoriyalar (agar kategoriya bo'lmasa)
        cat_count = db.query(Category).count()
        if cat_count == 0:
            logger.info("🌱 Boshlang'ich kategoriyalar yaratilmoqda...")
            default_categories = [
                {"name_uz": "Gazsiz suv", "name_ru": "Негазированная вода", "name_en": "Still Water", "slug": "gazsiz-suv", "order_index": 1, "is_active": True},
                {"name_uz": "Gazli suv", "name_ru": "Газированная вода", "name_en": "Sparkling Water", "slug": "gazli-suv", "order_index": 2, "is_active": True},
                {"name_uz": "Katta idishlar (19L)", "name_ru": "Большие бутыли (19L)", "name_en": "19L Bottles", "slug": "katta-idishlar-19l", "order_index": 3, "is_active": True},
            ]
            for c in default_categories:
                db.add(Category(**c))
            db.commit()
            logger.info("✅ Boshlang'ich kategoriyalar yaratildi")

    except Exception as e:
        logger.warning(f"⚠️ Boshlang'ich ma'lumotlarni yaratishda ogohlantirish: {e}")
        db.rollback()
