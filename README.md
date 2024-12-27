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

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python api.py
```

3. Open your browser and visit:
```
http://localhost:8000
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t instagram-processor .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env instagram-processor
```

### Cloud Deployment

The application can be deployed to various cloud platforms. Here are the recommended options:

#### Railway.app Deployment

1. Install Railway CLI:
```bash
brew install railway
```

2. Login to Railway:
```bash
railway login
```

3. Initialize project:
```bash
railway init
```

4. Deploy:
```bash
railway up
```

#### Render.com Deployment

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Add environment variables in Render dashboard
5. Deploy

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
