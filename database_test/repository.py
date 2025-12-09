from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User
from config import config


class Database:
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_or_create_user(self, vk_id, first_name, last_name):
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.vk_id == vk_id).first()
            if not user:
                user = User(
                    vk_id=vk_id,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    def update_user_location(self, vk_id, city):
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.vk_id == vk_id).first()
            if user:
                user.city = city
                session.commit()
        finally:
            session.close()