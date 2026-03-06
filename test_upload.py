import requests
import os
import sys

sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User
from app.utils.jwt import create_access_token

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@ecocompany.uz').first()

if not user:
    print("User not found!")
    sys.exit(1)

token = create_access_token({'sub': str(user.id), 'role': user.role})

with open("/tmp/dummy.jpg", "wb") as f:
    f.write(b"fake image data here")

url = "http://127.0.0.1:8000/api/v1/admin/upload"
headers = {"Authorization": f"Bearer {token}"}
files = {"file": ("dummy.jpg", open("/tmp/dummy.jpg", "rb"), "image/jpeg")}
data = {"folder": "test"}

r = requests.post(url, headers=headers, files=files, data=data)
print(r.status_code)
print(r.text)
