import os
import subprocess
from pathlib import Path
import logging
import yt_dlp
import whisper
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import numpy as np
import networkx as nx
from urllib.parse import urlparse
import json
from instagram_handler import InstagramHandler

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class VideoProcessor:
    def __init__(self, output_dir='downloads'):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.model = whisper.load_model("base")
        self.instagram = InstagramHandler()
        
    def get_source_type(self, url):
        """Determine the source type from URL"""
        domain = urlparse(url).netloc.lower()
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram.com' in domain:
            return 'instagram'
        elif 'facebook.com' in domain or 'fb.com' in domain:
            return 'facebook'
        elif 'tiktok.com' in domain:
            return 'tiktok'
        return 'generic'

    def download_video(self, url):
        """Download video from various platforms"""
        source_type = self.get_source_type(url)
        logging.info(f"Downloading video from {source_type}")
        
        if source_type == 'instagram':
            try:
                return self.instagram.download_post(url)
            except Exception as e:
                logging.error(f"Instagram download failed: {str(e)}")
                raise
        
        # For other platforms, use yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'verbose': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                logging.info(f"Successfully downloaded to: {video_path}")
                return video_path
        except Exception as e:
            logging.error(f"Error downloading video: {str(e)}")
            raise

    def transcribe_video(self, video_path):
        """Transcribe video using OpenAI's Whisper"""
        try:
            logging.info(f"Transcribing video: {video_path}")
            result = self.model.transcribe(video_path)
            return result["text"]
        except Exception as e:
            logging.error(f"Error transcribing video: {str(e)}")
            raise

    def summarize_text(self, text, num_sentences=5):
        """Generate summary using TextRank algorithm"""
        logging.info("Generating summary...")
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return {
                'brief': text,
                'keyPoints': sentences
            }
            
        # Create similarity matrix
        stop_words = set(stopwords.words('english'))
        
        def sentence_similarity(sent1, sent2):
            words1 = [word.lower() for word in nltk.word_tokenize(sent1) 
                     if word.lower() not in stop_words]
            words2 = [word.lower() for word in nltk.word_tokenize(sent2) 
                     if word.lower() not in stop_words]
            
            all_words = list(set(words1 + words2))
            vector1 = [1 if word in words1 else 0 for word in all_words]
            vector2 = [1 if word in words2 else 0 for word in all_words]
            
            if not any(vector1) or not any(vector2):
                return 0.0
            
            return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        
        # Create similarity matrix
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    similarity_matrix[i][j] = sentence_similarity(sentences[i], sentences[j])
        
        # Use NetworkX to rank sentences
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)
        
        # Get ranked sentences
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), 
                                reverse=True)
        
        # Generate different length summaries
        brief_summary = " ".join([s[1] for s in ranked_sentences[:3]])
        key_points = [s[1] for s in ranked_sentences[:5]]
        
        return {
            'brief': brief_summary,
            'keyPoints': key_points
        }

    def process_video(self, url, cleanup=True):
        """Main pipeline to process video"""
        video_path = None
        results = {
            'source_type': None,
            'transcript': None,
            'summary': None
        }
        
        try:
            # Identify source
            results['source_type'] = self.get_source_type(url)
            logging.info(f"Processing {results['source_type']} video: {url}")
            
            # Download video
            video_path = self.download_video(url)
            if not video_path:
                raise Exception("Failed to download video")
            
            logging.info(f"Successfully downloaded video to: {video_path}")
            
            # Transcribe video
            transcript = self.transcribe_video(video_path)
            if not transcript:
                raise Exception("Failed to transcribe video")
            results['transcript'] = transcript
            
            # Generate summary
            summary = self.summarize_text(transcript)
            results['summary'] = summary
            
            return results
            
        except Exception as e:
            logging.error(f"Error in processing pipeline: {str(e)}")
            raise
            
        finally:
            # Cleanup
            if cleanup and video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    if results['source_type'] == 'instagram':
                        self.instagram.cleanup()
                except Exception as e:
                    logging.error(f"Error during cleanup: {str(e)}")
