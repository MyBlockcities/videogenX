from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .models import Base, Video, Transcript, Summary, VideoMeta

class DatabaseManager:
    def __init__(self, db_url: str = "sqlite:///videos.db"):
        self.engine = create_engine(db_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        # Create all tables
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def store_video_data(self, 
                        url: str,
                        source_type: str,
                        transcript: str,
                        summary: Dict[str, Any],
                        metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Store video data in the database"""
        try:
            with self.session_scope() as session:
                # Check if video already exists
                existing_video = session.query(Video).filter_by(url=url).first()
                if existing_video:
                    logging.info(f"Video {url} already exists in database")
                    return existing_video.id
                
                # Create new video entry
                video = Video(
                    url=url,
                    source_type=source_type,
                    processed_at=datetime.utcnow()
                )
                session.add(video)
                session.flush()  # Get the video ID
                
                # Add transcript
                if transcript:
                    transcript_obj = Transcript(
                        video_id=video.id,
                        content=transcript
                    )
                    session.add(transcript_obj)
                
                # Add summary
                if summary:
                    summary_obj = Summary(
                        video_id=video.id,
                        brief=summary.get('brief', ''),
                        key_points=summary.get('keyPoints', [])
                    )
                    session.add(summary_obj)
                
                # Add metadata if available
                if metadata:
                    metadata_obj = VideoMeta(
                        video_id=video.id,
                        author=metadata.get('author'),
                        publish_date=metadata.get('publish_date'),
                        likes=metadata.get('likes'),
                        views=metadata.get('views'),
                        comments=metadata.get('comments'),
                        hashtags=metadata.get('hashtags', []),
                        mentions=metadata.get('mentions', []),
                        additional_data=metadata.get('additional_data', {})
                    )
                    session.add(metadata_obj)
                
                return video.id
                
        except IntegrityError as e:
            logging.error(f"Database integrity error: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error storing video data: {str(e)}")
            return None
    
    def get_video_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Retrieve video data from database"""
        try:
            with self.session_scope() as session:
                video = session.query(Video).filter_by(url=url).first()
                if not video:
                    return None
                
                return {
                    'id': video.id,
                    'url': video.url,
                    'source_type': video.source_type,
                    'processed_at': video.processed_at.isoformat(),
                    'transcript': video.transcript.content if video.transcript else None,
                    'summary': {
                        'brief': video.summary.brief,
                        'key_points': video.summary.key_points
                    } if video.summary else None,
                    'metadata': {
                        'author': video.metadata.author,
                        'publish_date': video.metadata.publish_date.isoformat() if video.metadata.publish_date else None,
                        'likes': video.metadata.likes,
                        'views': video.metadata.views,
                        'comments': video.metadata.comments,
                        'hashtags': video.metadata.hashtags,
                        'mentions': video.metadata.mentions,
                        'additional_data': video.metadata.additional_data
                    } if video.metadata else None
                }
                
        except Exception as e:
            logging.error(f"Error retrieving video data: {str(e)}")
            return None
    
    def search_videos(self, 
                     keyword: Optional[str] = None, 
                     source_type: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> list:
        """Search videos in the database"""
        try:
            with self.session_scope() as session:
                query = session.query(Video)
                
                if keyword:
                    query = query.join(Transcript).filter(
                        Transcript.content.ilike(f'%{keyword}%')
                    )
                
                if source_type:
                    query = query.filter(Video.source_type == source_type)
                
                if start_date:
                    query = query.filter(Video.processed_at >= start_date)
                
                if end_date:
                    query = query.filter(Video.processed_at <= end_date)
                
                videos = query.all()
                
                return [{
                    'id': video.id,
                    'url': video.url,
                    'source_type': video.source_type,
                    'processed_at': video.processed_at.isoformat(),
                    'transcript_preview': video.transcript.content[:200] + '...' if video.transcript else None
                } for video in videos]
                
        except Exception as e:
            logging.error(f"Error searching videos: {str(e)}")
            return []
