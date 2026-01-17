# models.py
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    grade = Column(String, index=True)  # убрал unique=True, если это не требуется
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

