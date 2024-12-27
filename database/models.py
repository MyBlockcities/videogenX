from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String(500))
    duration = Column(Integer)  # in seconds
    
    # Relationships
    transcript = relationship("Transcript", back_populates="video", uselist=False)
    summary = relationship("Summary", back_populates="video", uselist=False)
    video_meta = relationship("VideoMeta", back_populates="video", uselist=False)

class Transcript(Base):
    __tablename__ = 'transcripts'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), unique=True)
    content = Column(Text, nullable=False)
    language = Column(String(10), default='en')
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video = relationship("Video", back_populates="transcript")

class Summary(Base):
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), unique=True)
    brief = Column(Text, nullable=False)
    key_points = Column(JSON)  # Store as JSON array
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video = relationship("Video", back_populates="summary")

class VideoMeta(Base):
    __tablename__ = 'video_metadata'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), unique=True)
    author = Column(String(200))
    publish_date = Column(DateTime)
    likes = Column(Integer)
    views = Column(Integer)
    comments = Column(Integer)
    hashtags = Column(JSON)  # Store as JSON array
    mentions = Column(JSON)  # Store as JSON array
    additional_data = Column(JSON)  # Store any additional platform-specific data
    
    # Relationships
    video = relationship("Video", back_populates="video_meta")
