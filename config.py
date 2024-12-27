import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Instagram credentials
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

# Directory settings
DOWNLOAD_DIR = 'downloads'
TEMP_DIR = 'temp'
COOKIE_FILE = 'session-cookies.txt'

# Create necessary directories
for directory in [DOWNLOAD_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)
