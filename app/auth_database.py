from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Separate database for CampusVision AI Authentication
DATABASE_URL = "sqlite:///./campusvision_auth.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_auth_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
