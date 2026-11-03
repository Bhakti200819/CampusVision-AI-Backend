from sqlalchemy import Column, Integer, String, Boolean
from app.auth_database import Base


class User(Base):
    __tablename__ = "campusvision_users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="teacher")
    is_active = Column(Boolean, default=True)