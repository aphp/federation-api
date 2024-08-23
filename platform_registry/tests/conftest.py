from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker

from platform_registry import models
from platform_registry.core import database
from platform_registry.main import app
from platform_registry.models import User
from platform_registry.schemas import Role
from platform_registry.tests.utils import get_authorization_headers, get_or_create_platform_role, get_main_platform_user

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def db_override():
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

app.dependency_overrides[database.get_db] = db_override


@pytest.fixture(scope="session", autouse=True)
def db():
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as tc:
        yield tc


@pytest.fixture(scope="session")
def admin_user_auth_headers(client: TestClient, db: Session) -> dict[str, str]:
    return get_authorization_headers(client=client, db=db, for_admin=True)


@pytest.fixture(scope="session")
def platform_user_auth_headers(client: TestClient, db: Session) -> dict[str, str]:
    return get_authorization_headers(client=client, db=db, for_admin=False)


@pytest.fixture(scope="session")
def platform_role(db: Session) -> Role:
    return get_or_create_platform_role(db=db)


@pytest.fixture(scope="session")
def platform_user(db: Session) -> User:
    return get_main_platform_user(db=db)
