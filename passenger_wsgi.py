"""
ECO COMPANY — cPanel Passenger WSGI Entry Point
cPanel shared hosting uchun MAJBURIY fayl
"""
import sys
import os

# Virtual environment Python interpretatori
INTERP = '/home/ecocompany/fastapi_app/venv/bin/python3'
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Project path
sys.path.insert(0, '/home/ecocompany/fastapi_app')

# FastAPI app import
from app.main import app as application  # noqa: E402
