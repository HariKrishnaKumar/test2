from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from database.database import Base

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("models.user.User", back_populates="sessions")
    conversation_entries = relationship("ConversationEntry", back_populates="session")

class QuestionMaster(Base):
    __tablename__ = "question_masters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_key = Column(String(100), unique=True, nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    type = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    translations = relationship("QuestionTranslation", back_populates="question_master")
    answers = relationship("AnswerMaster", back_populates="question_master")
    conversation_entries = relationship("ConversationEntry", back_populates="question_master")


class QuestionTranslation(Base):
    __tablename__ = "question_translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_key = Column(String(100), ForeignKey("question_masters.question_key"), nullable=False)
    language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    variant = Column(String(50), nullable=True)

    question_master = relationship("QuestionMaster", back_populates="translations")


class AnswerMaster(Base):
    __tablename__ = "answer_masters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_key = Column(String(100), unique=True, nullable=False)
    question_key = Column(String(100), ForeignKey("question_masters.question_key"), nullable=False)
    answer_text = Column(Text, nullable=False)
    answer_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    question_master = relationship("QuestionMaster", back_populates="answers")
    translations = relationship("AnswerTranslation", back_populates="answer_master")
    conversation_entries = relationship("ConversationEntry", back_populates="answer_master")


class AnswerTranslation(Base):
    __tablename__ = "answer_translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_key = Column(String(100), ForeignKey("answer_masters.answer_key"), nullable=False)
    language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    variant = Column(String(50), nullable=True)

    answer_master = relationship("AnswerMaster", back_populates="translations")


class ConversationEntry(Base):
    __tablename__ = 'conversation_entries'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String(1000))
    response = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question_key = Column(String(100), ForeignKey("question_masters.question_key"))
    answer_key = Column(String(100), ForeignKey("answer_masters.answer_key"))

    session = relationship("Session", back_populates="conversation_entries")
    user = relationship("models.user.User", back_populates="conversation_entries")
    question_master = relationship("QuestionMaster", back_populates="conversation_entries")
    answer_master = relationship("AnswerMaster", back_populates="conversation_entries")


# Pydantic Models for API
class UserBase(BaseModel):
    id: str
    is_guest: bool = True
    device_info: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    created_at: datetime

    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    id: str
    user_id: Optional[str] = None
    language: str

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionMasterBase(BaseModel):
    question_key: str
    question_text: str
    question_order: int
    type: Optional[str] = None
    is_active: bool = True

class QuestionMasterCreate(QuestionMasterBase):
    pass

class QuestionMasterResponse(QuestionMasterBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionTranslationBase(BaseModel):
    question_key: str
    language: str
    translated_text: str
    variant: Optional[str] = None

class QuestionTranslationCreate(QuestionTranslationBase):
    pass

class QuestionTranslationResponse(QuestionTranslationBase):
    id: int

    class Config:
        from_attributes = True


class AnswerMasterBase(BaseModel):
    answer_key: str
    question_key: str
    answer_text: str
    answer_order: Optional[int] = None
    is_active: bool = True

class AnswerMasterCreate(AnswerMasterBase):
    pass

class AnswerMasterResponse(AnswerMasterBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerTranslationBase(BaseModel):
    answer_key: str
    language: str
    translated_text: str
    variant: Optional[str] = None

class AnswerTranslationCreate(AnswerTranslationBase):
    pass

class AnswerTranslationResponse(AnswerTranslationBase):
    id: int

    class Config:
        from_attributes = True


class ConversationEntryBase(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    question_key: str
    answer_key: Optional[str] = None
    custom_input: Optional[str] = None
    response_text: Optional[str] = None

class ConversationEntryCreate(ConversationEntryBase):
    pass

class ConversationEntryResponse(ConversationEntryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Extended response models with relationships
class QuestionWithTranslations(QuestionMasterResponse):
    translations: List[QuestionTranslationResponse] = []

class AnswerWithTranslations(AnswerMasterResponse):
    translations: List[AnswerTranslationResponse] = []

class QuestionWithAnswers(QuestionMasterResponse):
    answers: List[AnswerMasterResponse] = []
    translations: List[QuestionTranslationResponse] = []

class SessionWithEntries(SessionResponse):
    conversation_entries: List[ConversationEntryResponse] = []