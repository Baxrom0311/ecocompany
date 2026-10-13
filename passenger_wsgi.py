"""Passenger entry point; configure the interpreter and environment in cPanel."""
import atexit
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app
from app.wsgi import LifespanWSGI

application = LifespanWSGI(app)
atexit.register(application.close)
