from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.id"))
    name = Column(String, index=True)
    role = Column(String)
    group = Column(String)

    meeting = relationship("MeetingNote", back_populates="participants")


class DiscussionSegment(Base):
    __tablename__ = "discussion_segments"

    id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.id"))
    speaker = Column(String)
    group = Column(String)
    content = Column(Text)
    timestamp = Column(Float)
    duration = Column(Float)

    meeting = relationship("MeetingNote", back_populates="discussions")


class MeetingNote(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    date = Column(String)

    juiciness = Column(Float, default=7.0)
    tenderness = Column(Float, default=6.5)
    elasticity = Column(Float, default=7.2)
    flavor = Column(Float, default=6.8)
    texture = Column(Float, default=7.0)
    chewiness = Column(Float, default=6.5)

    cell_density = Column(Float, default=1500000)
    scaffold_porosity = Column(Float, default=85)
    fiber_alignment = Column(Float, default=78)
    maturation_rate = Column(Float, default=72)
    extracellular_matrix = Column(Float, default=85)
    vascularization = Column(Float, default=45)

    summary = Column(Text, nullable=True)
    process_adjustments = Column(Text, nullable=True)
    flavor_optimizations = Column(Text, nullable=True)
    experiment_record_id = Column(String, nullable=True)
    email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship("Participant", back_populates="meeting", cascade="all, delete-orphan")
    discussions = relationship("DiscussionSegment", back_populates="meeting", cascade="all, delete-orphan")
