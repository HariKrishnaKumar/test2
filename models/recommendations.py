# # models/recommendation.py

# from sqlalchemy import Column, Integer, String, ForeignKey
# from database.database import Base
# from sqlalchemy.orm import relationship

# class Recommendation(Base):
#     __tablename__ = "recommendations"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     mobile_number = Column(String(20), nullable=False)
#     item_id = Column(String(100), nullable=False)  # Clover item_id

#     # Not storing item_name in DB, we fetch from Clover dynamically
#     user = relationship("User", back_populates="recommendations")
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
# import models.recommendations as models

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mobile_number = Column(String(20), nullable=False)
    item_id = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=True)

    user = relationship("User", back_populates="recommendations")