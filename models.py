# models.py
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    participants_full_names = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    solved_tasks = Column(Integer)
    active_task = Column(Integer, nullable=True)



def print_user(user: User):
    print(user.id,user.username,user.start_time,user.end_time,user.solved_tasks, user.active_task)