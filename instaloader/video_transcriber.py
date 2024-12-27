import os
import whisper
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoTranscriber:
    def __init__(self, model_name="base"):
        """Initialize the transcriber with specified model.
        
        Args:
            model_name (str): The name of the Whisper model to use.
                            Options: "tiny", "base", "small", "medium", "large"
        """
        self.model = whisper.load_model(model_name)
        logger.info(f"Loaded Whisper model: {model_name}")

    def transcribe_video(self, video_path, output_dir=None):
        """Transcribe a video file and save the transcript.
        
        Args:
            video_path (str): Path to the video file
            output_dir (str, optional): Directory to save the transcript. 
                                      If None, saves in the same directory as the video.
        
        Returns:
            str: Path to the generated transcript file
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        # Determine output directory
        if output_dir is None:
            output_dir = video_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
        # Generate output filename
        transcript_path = output_dir / f"{video_path.stem}_transcript.txt"
        
        try:
            logger.info(f"Starting transcription of {video_path}")
            result = self.model.transcribe(str(video_path))
            
            # Save the transcript
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
                
            logger.info(f"Transcription saved to {transcript_path}")
            return str(transcript_path)
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise

def transcribe_video_file(video_path, model_name="base", output_dir=None):
    """Convenience function to transcribe a single video file.
    
    Args:
        video_path (str): Path to the video file
        model_name (str): Name of the Whisper model to use
        output_dir (str, optional): Directory to save the transcript
    
    Returns:
        str: Path to the generated transcript file
    """
    transcriber = VideoTranscriber(model_name)
    return transcriber.transcribe_video(video_path, output_dir)
