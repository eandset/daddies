from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Таблица для связи пользователь-интересы (многие ко многим)
user_interests = Table(
    'user_interests', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.vk_id')),
    Column('interest_id', Integer, ForeignKey('interests.id'))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    city = Column(String(100))
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    eco_score = Column(Integer, default=0)  # Рейтинг эко-активности
    level = Column(Integer, default=1)  # Уровень в геймификации

    # Связи
    interests = relationship("Interest", secondary=user_interests, back_populates="users")
    feedbacks = relationship("Feedback", back_populates="user")
    actions = relationship("UserAction", back_populates="user")


class Interest(Base):
    __tablename__ = 'interests'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", secondary=user_interests, back_populates="interests")


class RecyclingPoint(Base):
    __tablename__ = 'recycling_points'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    working_hours = Column(String(100))
    accepted_materials = Column(String(300))  # JSON или список материалов
    is_active = Column(Boolean, default=True)


class EcoEvent(Base):
    __tablename__ = 'eco_events'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    location = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    organizer = Column(String(100))
    registration_link = Column(String(500))


class Feedback(Base):
    __tablename__ = 'feedbacks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.vk_id'))
    text = Column(Text)
    rating = Column(Integer)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)
    entity_type = Column(String(50))  # 'point', 'event', 'bot'
    entity_id = Column(Integer)

    user = relationship("User", back_populates="feedbacks")


class UserAction(Base):
    __tablename__ = 'user_actions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.vk_id'))
    action_type = Column(String(50))  # 'recycle', 'event_participation', 'feedback', etc.
    points_earned = Column(Integer)
    description = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="actions")