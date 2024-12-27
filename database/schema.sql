-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    url text UNIQUE NOT NULL,
    source_type text NOT NULL,
    processed_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Transcripts table
CREATE TABLE IF NOT EXISTS transcripts (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    video_id uuid REFERENCES videos(id) ON DELETE CASCADE,
    content text NOT NULL,
    language text DEFAULT 'en',
    processed_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    video_id uuid REFERENCES videos(id) ON DELETE CASCADE,
    brief text NOT NULL,
    key_points jsonb DEFAULT '[]'::jsonb,
    processed_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Video metadata table
CREATE TABLE IF NOT EXISTS video_metadata (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    video_id uuid REFERENCES videos(id) ON DELETE CASCADE,
    author text,
    publish_date timestamp with time zone,
    likes integer,
    views integer,
    comments integer,
    hashtags jsonb DEFAULT '[]'::jsonb,
    mentions jsonb DEFAULT '[]'::jsonb,
    additional_data jsonb DEFAULT '{}'::jsonb
);

-- Enable full text search on transcripts
ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS fts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX IF NOT EXISTS transcripts_fts_idx ON transcripts USING gin(fts);

-- Add indexes for foreign keys and common queries
CREATE INDEX IF NOT EXISTS idx_transcripts_video_id ON transcripts(video_id);
CREATE INDEX IF NOT EXISTS idx_summaries_video_id ON summaries(video_id);
CREATE INDEX IF NOT EXISTS idx_video_metadata_video_id ON video_metadata(video_id);
CREATE INDEX IF NOT EXISTS idx_videos_processed_at ON videos(processed_at);
CREATE INDEX IF NOT EXISTS idx_videos_source_type ON videos(source_type);
