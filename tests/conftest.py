"""
ECO COMPANY — Test Fixtures
SQLite in-memory DB + TestClient + Admin token
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.hashing import hash_password
from app.services.auth_service import create_access_token


# In-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db):
    user = User(
        email="admin@test.com",
        password=hash_password("Admin123!"),
        name="Test Admin",
        role="super_admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(admin_user):
    token = create_access_token({"sub": str(admin_user.id)})
    return token


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
