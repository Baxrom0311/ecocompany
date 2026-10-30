"""Alembic migratsiyalarini qo'llash va boshlang'ich sozlamalarni yaratish."""
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.services.init_data import seed_initial_data

if __name__ == "__main__":
    print("🌿 ECO COMPANY: Alembic migratsiyalarini qo'llash va boshlang'ich sozlamalarni yaratish...")
    command.upgrade(Config(str(Path(__file__).resolve().parent / "alembic.ini")), "head")
    with SessionLocal() as db:
        seed_initial_data(db)
    print("✨ Baza muvaffaqiyatli tayyorlandi!")
