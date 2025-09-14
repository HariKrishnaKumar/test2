from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
# Import the shared Base from your database file
from database.database import Base
from sqlalchemy.orm import relationship
from database.base import Base 


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(15), unique=True, nullable=False)
    otp = Column(String(6), nullable=True)
    is_verified = Column(Boolean, default=False)
    name = Column(String(100), nullable=True)
    alternate_contact = Column(String(15), nullable=True)
    floor_or_office = Column(String(255), nullable=True)
    is_guest = Column(Boolean, default=True)
    device_info = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    address = Column(String(200), nullable=True)
    preferences = Column(String(255), nullable=True)

    # These relationships will now resolve correctly
    sessions = relationship("Session", back_populates="user")
    conversation_entries = relationship("ConversationEntry", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")

    