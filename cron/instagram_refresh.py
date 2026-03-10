#!/usr/bin/env python3
"""
ECO COMPANY — Instagram Cron Job
Instagram videolari endi qo'lda link orqali boshqariladi.

cPanel Cron Job buyrug'i:
  cd /home/user/ecocompany-backend && .venv/bin/python cron/instagram_refresh.py
"""
import sys
import os
import asyncio

# Project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    print("📸 Instagram cron job boshlandi...")
    print("ℹ️ Instagram API integratsiyasi o'chirilgan.")
    print("ℹ️ Videolar admin paneldagi Instagram bo'limida qo'lda link bilan boshqariladi.")
    print("📸 Instagram cron job tugadi")


if __name__ == "__main__":
    asyncio.run(main())
