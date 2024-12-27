from supabase import create_client
import os
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from dotenv import load_dotenv

# Try to load environment variables from both possible locations
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instaloader', '.env')
]

for env_path in env_paths:
    print(f"Looking for .env file at: {env_path}")
    print(f"File exists: {os.path.exists(env_path)}")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("Environment variables after loading:")
        print(f"SUPABASE_API_KEY: {os.getenv('SUPABASE_API_KEY')}")
        print(f"INSTAGRAM_USERNAME: {os.getenv('INSTAGRAM_USERNAME')}")
        if os.getenv('SUPABASE_API_KEY'):
            break

class SupabaseManager:
    def __init__(self):
        self.supabase_url = 'https://ncxikoazwraguwudeovx.supabase.co'
        self.supabase_key = os.getenv('SUPABASE_API_KEY')
        if not self.supabase_key:
            self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        if not self.supabase_key:
            raise ValueError("Neither SUPABASE_API_KEY nor SUPABASE_ANON_KEY found in environment variables")
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables if they don't exist"""
        try:
            # We'll use Supabase's SQL editor to create tables
            # The tables should be created through the Supabase dashboard
            # This function will only verify the connection
            self.client.table('videos').select('id').limit(1).execute()
            logging.info("Successfully connected to Supabase")
        except Exception as e:
            logging.error(f"Failed to connect to Supabase: {str(e)}")
            raise
    
    async def store_video_data(self,
                             url: str,
                             source_type: str,
                             transcript: str,
                             summary: Dict[str, Any],
                             metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Store video data in Supabase"""
        try:
            # Check if video exists
            response = self.client.table('videos').select('id').eq('url', url).execute()
            if response.data:
                logging.info(f"Video {url} already exists in database")
                return response.data[0]['id']
            
            # Store video data
            video_data = {
                'url': url,
                'source_type': source_type,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            video_response = self.client.table('videos').insert(video_data).execute()
            video_id = video_response.data[0]['id']
            
            # Store transcript
            if transcript:
                transcript_data = {
                    'video_id': video_id,
                    'content': transcript,
                    'language': 'en',
                    'processed_at': datetime.utcnow().isoformat()
                }
                self.client.table('transcripts').insert(transcript_data).execute()
            
            # Store summary
            if summary:
                summary_data = {
                    'video_id': video_id,
                    'brief': summary.get('brief', ''),
                    'key_points': summary.get('keyPoints', []),
                    'processed_at': datetime.utcnow().isoformat()
                }
                self.client.table('summaries').insert(summary_data).execute()
            
            # Store metadata if available
            if metadata:
                metadata_data = {
                    'video_id': video_id,
                    'author': metadata.get('author'),
                    'publish_date': metadata.get('publish_date'),
                    'likes': metadata.get('likes'),
                    'views': metadata.get('views'),
                    'comments': metadata.get('comments'),
                    'hashtags': metadata.get('hashtags', []),
                    'mentions': metadata.get('mentions', []),
                    'additional_data': metadata.get('additional_data', {})
                }
                self.client.table('metadata').insert(metadata_data).execute()
            
            return video_id
            
        except Exception as e:
            logging.error(f"Error storing video data: {str(e)}")
            return None
    
    async def get_video_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Retrieve video data from Supabase"""
        try:
            # Get video and related data
            response = self.client.table('videos')\
                .select('''
                    *,
                    transcripts (*),
                    summaries (*),
                    metadata (*)
                ''')\
                .eq('url', url)\
                .execute()
            
            if not response.data:
                return None
            
            video = response.data[0]
            
            return {
                'id': video['id'],
                'url': video['url'],
                'source_type': video['source_type'],
                'processed_at': video['processed_at'],
                'transcript': video['transcripts'][0]['content'] if video.get('transcripts') else None,
                'summary': {
                    'brief': video['summaries'][0]['brief'] if video.get('summaries') else '',
                    'key_points': video['summaries'][0]['key_points'] if video.get('summaries') else []
                } if video.get('summaries') else None,
                'metadata': {
                    'author': video['metadata'][0]['author'],
                    'publish_date': video['metadata'][0]['publish_date'],
                    'likes': video['metadata'][0]['likes'],
                    'views': video['metadata'][0]['views'],
                    'comments': video['metadata'][0]['comments'],
                    'hashtags': video['metadata'][0]['hashtags'],
                    'mentions': video['metadata'][0]['mentions'],
                    'additional_data': video['metadata'][0]['additional_data']
                } if video.get('metadata') else None
            }
                
        except Exception as e:
            logging.error(f"Error retrieving video data: {str(e)}")
            return None
    
    async def search_videos(self,
                          keyword: Optional[str] = None,
                          source_type: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> list:
        """Search videos in Supabase"""
        try:
            query = self.client.table('videos')\
                .select('''
                    *,
                    transcripts (content)
                ''')
            
            if keyword:
                query = query.textSearch('transcripts.content', keyword)
            
            if source_type:
                query = query.eq('source_type', source_type)
            
            if start_date:
                query = query.gte('processed_at', start_date.isoformat())
            
            if end_date:
                query = query.lte('processed_at', end_date.isoformat())
            
            response = query.execute()
            
            return [{
                'id': video['id'],
                'url': video['url'],
                'source_type': video['source_type'],
                'processed_at': video['processed_at'],
                'transcript_preview': video['transcripts'][0]['content'][:200] + '...' if video.get('transcripts') else None
            } for video in response.data]
            
        except Exception as e:
            logging.error(f"Error searching videos: {str(e)}")
            return []
