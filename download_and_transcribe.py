#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import subprocess
import logging
from instaloader.video_transcriber import transcribe_video_file
from instaloader.text_processor import TextProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_and_process(shortcode, model_name="base"):
    """Download an Instagram video, create its transcript, and generate summary.
    
    Args:
        shortcode (str): Instagram post shortcode (from URL)
        model_name (str): Whisper model name to use for transcription
    """
    # Download the video using instaloader
    logger.info(f"Downloading video with shortcode: {shortcode}")
    download_cmd = [
        "python3", "-m", "instaloader",
        "--no-pictures",  # Skip thumbnails
        "--no-metadata-json",  # Skip metadata
        "--", f"-{shortcode}"  # The post to download
    ]
    
    subprocess.run(download_cmd, check=True)
    
    # Find the downloaded video
    download_dir = Path(f"-{shortcode}")
    video_files = list(download_dir.glob("*.mp4"))
    
    if not video_files:
        raise FileNotFoundError(f"No video files found in {download_dir}")
    
    video_path = video_files[0]
    logger.info(f"Found video file: {video_path}")
    
    # Transcribe the video
    transcript_path = transcribe_video_file(video_path, model_name)
    logger.info(f"Transcription complete! Transcript saved to: {transcript_path}")
    
    # Process and summarize the transcript
    text_processor = TextProcessor()
    summary_path = text_processor.process_transcript(transcript_path)
    logger.info(f"Summary generated! Summary saved to: {summary_path}")
    
    return transcript_path, summary_path

def display_file_contents(file_path):
    """Display the contents of a file in a readable format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n" + "="*80)
    print(f"Contents of {Path(file_path).name}:")
    print("="*80)
    print(content)
    print("="*80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_and_transcribe.py SHORTCODE [MODEL_NAME]")
        print("\nExample:")
        print("  python download_and_transcribe.py ABC123")
        print("  python download_and_transcribe.py ABC123 medium")
        sys.exit(1)
        
    shortcode = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    try:
        transcript_path, summary_path = download_and_process(shortcode, model_name)
        
        # Display the transcript and summary
        display_file_contents(transcript_path)
        display_file_contents(summary_path)
            
        print("\nSuccess! Files saved:")
        print(f"- Transcript: {transcript_path}")
        print(f"- Summary: {summary_path}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)
