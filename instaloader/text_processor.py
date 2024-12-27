import os
import logging
from pathlib import Path
import re
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        """Initialize the text processor"""
        pass
        
    def extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
        
    def extract_key_points(self, sentences: List[str], num_points: int = 5) -> List[str]:
        """Extract key points from sentences."""
        # Simple approach: take the first num_points sentences as key points
        return sentences[:min(num_points, len(sentences))]
        
    def summarize_text(self, text: str, detail_level: str = "detailed") -> Dict:
        """Summarize the given text.
        
        Args:
            text (str): Text to summarize
            detail_level (str): Level of detail for summary ('brief', 'detailed', or 'comprehensive')
        
        Returns:
            dict: Dictionary containing original text, summary, and key points
        """
        sentences = self.extract_sentences(text)
        
        if not sentences:
            return {
                "original_text": text,
                "summary": "No text to summarize.",
                "key_points": []
            }
            
        # Determine number of sentences based on detail level
        if detail_level == "brief":
            summary_sentences = sentences[:2]
            num_points = 3
        elif detail_level == "comprehensive":
            summary_sentences = sentences
            num_points = 7
        else:  # detailed (default)
            summary_sentences = sentences[:5]
            num_points = 5
            
        summary = " ".join(summary_sentences)
        key_points = self.extract_key_points(sentences, num_points)
            
        return {
            "original_text": text,
            "summary": summary,
            "key_points": key_points
        }

    def process_transcript(self, transcript_path: str, output_dir: str = None) -> str:
        """Process a transcript file and generate summary.
        
        Args:
            transcript_path (str): Path to the transcript file
            output_dir (str, optional): Directory to save the summary. If None, uses same directory as transcript.
        
        Returns:
            str: Path to the generated summary file
        """
        transcript_path = Path(transcript_path)
        
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
            
        # Determine output directory
        if output_dir is None:
            output_dir = transcript_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
            
        # Get summaries at different detail levels
        summaries = {
            level: self.summarize_text(transcript_text, level)
            for level in ['brief', 'detailed', 'comprehensive']
        }
        
        # Generate summary file
        summary_path = output_dir / f"{transcript_path.stem}_summary.txt"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== TRANSCRIPT ANALYSIS ===\n\n")
            
            f.write("=== ORIGINAL TRANSCRIPT ===\n")
            f.write(transcript_text)
            f.write("\n\n")
            
            for level, content in summaries.items():
                f.write(f"=== {level.upper()} SUMMARY ===\n")
                f.write(content['summary'])
                f.write("\n\n")
                
                f.write(f"=== KEY POINTS ({level.upper()}) ===\n")
                f.write("\n".join(f"• {point}" for point in content['key_points']))
                f.write("\n\n")
                
        logger.info(f"Summary saved to: {summary_path}")
        return str(summary_path)
