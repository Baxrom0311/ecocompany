#!/usr/bin/env python3
"""
ECO COMPANY — Instagram Cron Job
Har 25 kunda token yangilash va postlarni keshga saqlash.

cPanel Cron Job buyrug'i:
  cd /home/user/ecocompany-backend && .venv/bin/python cron/instagram_refresh.py
"""
import sys
import os
import asyncio

# Project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import SessionLocal
from app.services import instagram_service


async def main():
    print("📸 Instagram cron job boshlandi...")

    # 1. Token yangilash
    result = await instagram_service.refresh_long_lived_token()
    if result:
        print(f"✅ Token yangilandi (expires_in: {result['expires_in']} sec)")
        # TODO: Yangi tokenni .env ga yozish yoki DB ga saqlash
    else:
        print("❌ Token yangilanmadi!")

    # 2. Postlarni keshga saqlash
    db = SessionLocal()
    try:
        count = await instagram_service.fetch_and_cache_posts(db)
        print(f"✅ {count} ta post keshga saqlandi")
    finally:
        db.close()

    print("📸 Instagram cron job tugadi")


if __name__ == "__main__":
    asyncio.run(main())
