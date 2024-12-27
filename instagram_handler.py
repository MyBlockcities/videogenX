import instaloader
import logging
import os
from pathlib import Path
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, COOKIE_FILE, TEMP_DIR

class InstagramHandler:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=TEMP_DIR
        )
        self._ensure_login()

    def _ensure_login(self):
        """Ensure we're logged into Instagram"""
        try:
            # Try to load session from cookie file
            if os.path.exists(COOKIE_FILE):
                logging.info("Loading session from cookie file...")
                self.L.load_session_from_file(INSTAGRAM_USERNAME, COOKIE_FILE)
                return

            # If no cookie file or it's invalid, login with credentials
            if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                logging.info("Logging in with credentials...")
                self.L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                # Save session for future use
                self.L.save_session_to_file(COOKIE_FILE)
            else:
                logging.warning("No Instagram credentials provided. Some features may be limited.")
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            raise

    def download_post(self, url):
        """Download video from Instagram post"""
        try:
            # Extract post shortcode from URL
            shortcode = url.split("/p/")[1].split("/")[0]
            logging.info(f"Downloading post with shortcode: {shortcode}")

            # Get post
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            
            if not post.is_video:
                raise ValueError("This post does not contain a video")

            # Download the video
            self.L.download_post(post, target=TEMP_DIR)

            # Find the downloaded video file
            video_pattern = f"{post.date_utc:%Y-%m-%d_%H-%M-%S}_UTC*.mp4"
            video_files = list(Path(TEMP_DIR).glob(video_pattern))
            
            if not video_files:
                raise FileNotFoundError("Video file not found after download")

            return str(video_files[0])

        except Exception as e:
            logging.error(f"Error downloading Instagram post: {str(e)}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        try:
            for item in Path(TEMP_DIR).glob("*"):
                if item.is_file():
                    item.unlink()
        except Exception as e:
            logging.error(f"Error cleaning up: {str(e)}")
