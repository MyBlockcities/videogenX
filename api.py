from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime
from video_processor import VideoProcessor
from database.supabase_manager import SupabaseManager
import os
from dotenv import load_dotenv

# Try to load environment variables from both possible locations
env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),
    os.path.join(os.path.dirname(__file__), 'instaloader', '.env')
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        if os.getenv('SUPABASE_API_KEY'):
            break

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add security middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
processor = VideoProcessor(output_dir='downloads')
db = SupabaseManager()

class VideoRequest(BaseModel):
    url: str

class SearchRequest(BaseModel):
    keyword: Optional[str] = None
    source_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/process")
async def process_video(request: VideoRequest):
    try:
        logger.info(f"Processing video from URL: {request.url}")
        
        # Check if video already exists in database
        existing_data = await db.get_video_data(request.url)
        if existing_data:
            logger.info(f"Retrieved video data from database for URL: {request.url}")
            return existing_data
        
        # Process video
        results = processor.process_video(request.url)
        
        if not results['transcript']:
            raise HTTPException(
                status_code=500,
                detail="Failed to process video. Please try again."
            )
        
        # Store in database
        video_id = await db.store_video_data(
            url=request.url,
            source_type=results['source_type'],
            transcript=results['transcript'],
            summary=results['summary']
        )
        
        if not video_id:
            logger.warning("Failed to store video data in database")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/search")
async def search_videos(request: SearchRequest):
    try:
        results = await db.search_videos(
            keyword=request.keyword,
            source_type=request.source_type,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"videos": results}
    except Exception as e:
        logger.error(f"Error searching videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/video/{video_url:path}")
async def get_video(video_url: str):
    try:
        data = await db.get_video_data(video_url)
        if not data:
            raise HTTPException(
                status_code=404,
                detail="Video not found"
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# Serve static files from the React build directory
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")

# Serve index.html for all other routes (client-side routing)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    return FileResponse("frontend/build/index.html")

if __name__ == "__main__":
    import uvicorn
    # Create necessary directories
    os.makedirs("downloads", exist_ok=True)
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
