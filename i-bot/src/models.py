from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String)
    turn_count = Column(Integer, default=0)
    unsatisfied_count = Column(Integer, default=0)
    creation_time = Column(DateTime(timezone=True), server_default=func.now())

    feedback = relationship("Feedback", back_populates="session")
    tickets = relationship("Ticket", back_populates="session")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    turn_number = Column(Integer)
    satisfied_flag = Column(Boolean)
    comment = Column(String)
    response_text = Column(String)

    session = relationship("Session", back_populates="feedback")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    creation_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="open")
    external_id = Column(String, nullable=True)

    session = relationship("Session", back_populates="tickets")
