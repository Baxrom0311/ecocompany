#!/usr/bin/env python3
"""
ECO COMPANY — Seed Script
Boshlang'ich ma'lumotlarni DB ga yuklash
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.setting import SiteSetting

def seed_settings():
    """Boshlang'ich sozlamalar"""
    db = SessionLocal()
    try:
        default_settings = [
            ("phone_1", "+998901234567", "text", "Telefon 1", True),
            ("phone_2", "", "text", "Telefon 2", True),
            ("email", "info@ecocompany.uz", "text", "Email", True),
            ("address_uz", "Toshkent, O'zbekiston", "text", "Manzil (UZ)", True),
            ("address_ru", "Ташкент, Узбекистан", "text", "Manzil (RU)", True),
            ("address_en", "Tashkent, Uzbekistan", "text", "Address (EN)", True),
            ("working_hours", "Du-Ju: 09:00-18:00", "text", "Ish vaqti", True),
            ("hero_badge", "Premium Tozalangan Suv", "text", "Hero badge", True),
            ("hero_title_uz", "Toza suv — toza hayot", "text", "Hero sarlavha", True),
            ("hero_title_ru", "Чистая вода — чистая жизнь", "text", "Hero title (RU)", True),
            ("hero_title_en", "Pure water — pure life", "text", "Hero title (EN)", True),
            ("hero_subtitle_uz", "ECO COMPANY — yuqori sifatli tozalangan suv", "text", "Hero tavsif (UZ)", True),
            ("hero_subtitle_ru", "ECO COMPANY — высококачественная очищенная вода", "text", "Hero tavsif (RU)", True),
            ("hero_subtitle_en", "ECO COMPANY — premium purified water", "text", "Hero subtitle (EN)", True),
            ("hero_image_url", "", "image", "Hero rasmi", True),
            ("about_page_title_uz", "Kompaniya haqida", "text", "About page title (UZ)", True),
            ("about_page_title_ru", "О компании", "text", "About page title (RU)", True),
            ("about_page_title_en", "About Company", "text", "About page title (EN)", True),
            ("about_section_badge_uz", "Biz haqimizda", "text", "About badge (UZ)", True),
            ("about_section_badge_ru", "О нас", "text", "About badge (RU)", True),
            ("about_section_badge_en", "About us", "text", "About badge (EN)", True),
            ("about_section_title_uz", "Sifatli suv — sog'lom hayot kafolati", "text", "About title (UZ)", True),
            ("about_section_title_ru", "Качественная вода — залог здоровья", "text", "About title (RU)", True),
            ("about_section_title_en", "Quality water — guarantee of health", "text", "About title (EN)", True),
            ("about_text_uz", "ECO COMPANY — O'zbekistondagi sifatli tozalangan suv ishlab chiqaruvchisi.", "text", "Biz haqimizda (UZ)", True),
            ("about_text_ru", "ECO COMPANY — производитель качественной очищенной воды в Узбекистане.", "text", "Biz haqimizda (RU)", True),
            ("about_text_en", "ECO COMPANY is a producer of quality purified water in Uzbekistan.", "text", "About us (EN)", True),
            ("about_values_badge_uz", "Nima uchun biz?", "text", "Values badge (UZ)", True),
            ("about_values_badge_ru", "Почему мы?", "text", "Values badge (RU)", True),
            ("about_values_badge_en", "Why us?", "text", "Values badge (EN)", True),
            ("about_values_title_uz", "Bizning qadriyatlar", "text", "Values title (UZ)", True),
            ("about_values_title_ru", "Наши ценности", "text", "Values title (RU)", True),
            ("about_values_title_en", "Our Values", "text", "Values title (EN)", True),
            ("stats_years", "10", "text", "Yillar tajriba", True),
            ("stats_clients", "5000", "text", "Mijozlar", True),
            ("stats_products", "20", "text", "Mahsulotlar", True),
            ("stats_cities", "15", "text", "Shaharlar", True),
            ("logo_url", "", "image", "Logo", True),
            ("whatsapp_url", "", "text", "WhatsApp", True),
            ("instagram_url", "https://instagram.com/ecocompany", "text", "Instagram", True),
            ("telegram_url", "https://t.me/ecocompany", "text", "Telegram", True),
            ("facebook_url", "", "text", "Facebook", True),
            ("youtube_url", "", "text", "YouTube", True),
            ("partner_logos", json.dumps([]), "json", "Hamkor logolari", True),
            ("seo_keywords_uz", "eco company, tozalangan suv, ichimlik suvi, suv filtrlari, suv tozalash uskunalari", "text", "SEO kalit so'zlar (UZ)", True),
            ("seo_keywords_ru", "eco company, очищенная вода, питьевая вода, фильтры для воды, оборудование для очистки воды", "text", "SEO kalit so'zlar (RU)", True),
            ("seo_keywords_en", "eco company, purified water, drinking water, water filters, water treatment equipment", "text", "SEO keywords (EN)", True),
            ("seo_home_keywords_uz", "", "text", "Home SEO kalit so'zlar (UZ)", True),
            ("seo_home_keywords_ru", "", "text", "Home SEO kalit so'zlar (RU)", True),
            ("seo_home_keywords_en", "", "text", "Home SEO keywords (EN)", True),
            ("seo_products_keywords_uz", "", "text", "Products SEO kalit so'zlar (UZ)", True),
            ("seo_products_keywords_ru", "", "text", "Products SEO kalit so'zlar (RU)", True),
            ("seo_products_keywords_en", "", "text", "Products SEO keywords (EN)", True),
            ("seo_about_keywords_uz", "", "text", "About SEO kalit so'zlar (UZ)", True),
            ("seo_about_keywords_ru", "", "text", "About SEO kalit so'zlar (RU)", True),
            ("seo_about_keywords_en", "", "text", "About SEO keywords (EN)", True),
            ("seo_gallery_keywords_uz", "", "text", "Gallery SEO kalit so'zlar (UZ)", True),
            ("seo_gallery_keywords_ru", "", "text", "Gallery SEO kalit so'zlar (RU)", True),
            ("seo_gallery_keywords_en", "", "text", "Gallery SEO keywords (EN)", True),
            ("seo_certificates_keywords_uz", "", "text", "Certificates SEO kalit so'zlar (UZ)", True),
            ("seo_certificates_keywords_ru", "", "text", "Certificates SEO kalit so'zlar (RU)", True),
            ("seo_certificates_keywords_en", "", "text", "Certificates SEO keywords (EN)", True),
            ("seo_contact_keywords_uz", "", "text", "Contact SEO kalit so'zlar (UZ)", True),
            ("seo_contact_keywords_ru", "", "text", "Contact SEO kalit so'zlar (RU)", True),
            ("seo_contact_keywords_en", "", "text", "Contact SEO keywords (EN)", True),
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
    seed_settings()
    print("ℹ️  Admin foydalanuvchi avtomatik yaratilmaydi.")
    print("ℹ️  Admin yaratish uchun: python scripts/create_admin.py --email admin@ecocompany.uz")
    print("🎉 Seed tugadi!")
