from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from platform_registry.core.config import settings


engine = create_engine(str(settings.database_url))
SessionLocal = sessionmaker(bind=engine,
                            autocommit=False,
                            autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
