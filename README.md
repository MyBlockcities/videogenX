# Instagram Video Processor

A modern web application that downloads Instagram videos, transcribes them, and generates intelligent summaries.

## Features

- 🎥 Download Instagram videos using just the post URL
- 🗣️ Convert speech to text using OpenAI's Whisper
- 📝 Generate smart summaries and key points
- 🎨 Beautiful, responsive UI
- ⚡ Fast processing with real-time status updates
- 💾 Persistent storage with Supabase

## Setup Instructions

### Environment Variables

Create a `.env` file with the following variables:
```bash
SUPABASE_API_KEY=your_supabase_api_key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

### Local Development

1. Navigate to the project directory:
```bash
cd /path/to/instaloader
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install and build frontend:
```bash
cd frontend
npm install
npm run build
cd ..
```

4. Start the application:
```bash
python api.py
```

5. Open your browser and visit:
```
http://localhost:8000
```

Note: You don't need to run the frontend separately as the FastAPI server serves the built React frontend files.

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t instagram-processor .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env instagram-processor
```

### Deployment

This application is configured for easy deployment to Render.com, which provides a reliable and simple deployment process for both the frontend and backend components.

#### Prerequisites
- A GitHub account
- A Render.com account
- Your Supabase API key
- Instagram credentials

#### Deployment Steps

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-github-repo-url
git push -u origin main
```

2. Deploy to Render.com:
   1. Go to [render.com](https://render.com) and sign up/login
   2. Click "New +" and select "Web Service"
   3. Connect your GitHub repository
   4. Configure the service:
      - Name: instaloader
      - Environment: Python
      - Region: Choose closest to your users
      - Branch: main (or your default branch)
      - Build Command: `curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs ffmpeg && pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..`
      - Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app`
   5. Click on "Advanced" and configure:
      - Health Check Path: `/healthz` (optional)
      - Auto-Deploy: Yes (recommended)
   6. Add environment variables:
      - SUPABASE_API_KEY
      - INSTAGRAM_USERNAME
      - INSTAGRAM_PASSWORD
   7. Click "Create Web Service"

The deployment process will automatically:
- Install system dependencies (ffmpeg)
- Install Python dependencies
- Build the React frontend
- Start the FastAPI server

#### Monitoring and Troubleshooting

After deployment:
1. Monitor the build logs in Render dashboard
2. Check the "Logs" tab for runtime issues
3. Use the "Shell" tab to debug if needed

#### Updating the Application

To update your deployed application:
1. Push changes to your GitHub repository
2. Render will automatically rebuild and deploy

## Usage

1. Copy an Instagram video post URL
2. Paste it into the application
3. Click "Process Video"
4. View the transcript and summary in the results section

## Technologies Used

- Backend:
  - FastAPI
  - OpenAI Whisper
  - Python
  - Supabase
- Infrastructure:
  - Docker
  - Railway/Render
- Dependencies:
  - FFmpeg (for video processing)
  - Python 3.11+

## Database Schema

The application uses Supabase with the following tables:

- `videos`: Stores video metadata
- `transcripts`: Stores video transcriptions
- `summaries`: Stores video summaries and key points

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
