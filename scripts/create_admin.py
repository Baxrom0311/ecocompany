"""
ECO COMPANY — Admin foydalanuvchi yaratish skripti
Ishga tushirish: python scripts/create_admin.py --email admin@ecocompany.uz
"""
import argparse
import secrets
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.utils.hashing import hash_password


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ECO COMPANY uchun super admin yaratish")
    parser.add_argument(
        "--email",
        default=os.getenv("ECO_ADMIN_EMAIL") or os.getenv("ADMIN_EMAIL") or "admin@ecocompany.uz",
        help="Admin email manzili",
    )
    parser.add_argument(
        "--name",
        default=os.getenv("ECO_ADMIN_NAME") or "Super Admin",
        help="Admin display name",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("ECO_ADMIN_PASSWORD"),
        help="Parol. Berilmasa xavfsiz random parol generatsiya qilinadi",
    )
    return parser


def create_admin(email: str, name: str, password: str | None):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"⚠️  Admin allaqachon mavjud: {existing.email} (role: {existing.role})")
            return

        generated_password = password or secrets.token_urlsafe(18)
        if len(generated_password) < 8:
            raise ValueError("Parol kamida 8 ta belgi bo'lishi kerak")

        user = User(
            email=email,
            password=hash_password(generated_password),
            name=name,
            role="super_admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"✅ Admin yaratildi!")
        print(f"   📧 Email: {email}")
        print(f"   🔑 Parol: {generated_password}")
        print(f"   👑 Role: super_admin")
    finally:
        db.close()


if __name__ == "__main__":
    args = _build_parser().parse_args()
    create_admin(email=args.email, name=args.name, password=args.password)
