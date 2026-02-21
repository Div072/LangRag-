1. Project Overview

Goal: Build a resume-worthy full-stack application that helps users learn languages from YouTube videos.
Core Functionality:

    User pastes a YouTube URL.

    System downloads audio, transcribes it (with timestamps), and stores vector embeddings.

    User chats with the video (RAG). The AI answers questions and provides clickable timestamps to jump the video to the exact moment where the answer is found.

    UI: Split screen with Video Player on the left, Interactive Transcript/Chat on the right.

2. Tech Stack (Strict Constraints)

    Frontend: Next.js 14+ (App Router), Tailwind CSS, TypeScript, react-player.

    Backend: FastAPI (Python), Uvicorn.

    AI/ML Services:

        Transcription: OpenAI Whisper API (Must use verbose_json for timestamps).

        LLM: OpenAI GPT-4o-mini (via langchain-openai).

        Embeddings: text-embedding-3-small.

        Vector DB: Pinecone (Serverless).

    Video Tools: yt-dlp (for audio extraction).

    Database: PostgreSQL (via Supabase or local Docker) - optional for Phase 1.

3. Architecture & Data Flow
Pipeline A: Ingestion (/process-video)

    Input: YouTube URL.

    Download: Backend uses yt-dlp to download audio as a temporary MP3 (low bitrate is fine).

    Transcribe: Send MP3 to OpenAI Whisper API.

        Constraint: Set response_format="verbose_json" to get start/end times for every segment.

    Embed: Split transcript into segments. Create embeddings for each segment.

    Store: Upsert to Pinecone.

        Metadata: video_id, text, start_time, end_time.

    Clean up: Delete temp MP3.

Pipeline B: Chat RAG (/chat)

    Input: user_query, video_id.

    Retrieve: Convert query to vector -> Search Pinecone for top 3 matching segments from this video_id.

    Generate: Send retrieved context + query to LLM.

        System Prompt: "You are a language tutor. Answer based on the context. Always cite the timestamp in the format [MM:SS] at the end of relevant sentences."

    Output: Text response with timestamp tags.

4. API Endpoints (FastAPI Specification)
POST /process-video

    Request: { "url": "https://youtube.com/..." }

    Process: Downloads audio, calls Whisper API, upserts to Pinecone.

    Response: { "status": "success", "video_id": "uuid-string", "title": "Video Title" }

POST /chat

    Request: { "video_id": "uuid", "query": "Why was he angry?" }

    Process: RAG pipeline (Embed query -> Search -> LLM).

    Response: { "answer": "He was angry because... [04:20]", "sources": [{"start": 260, "text": "..."}] }

GET /transcript/{video_id}

    Response: Full list of segments [{ "start": 0.0, "end": 4.5, "text": "..." }] for the frontend "Interactive Transcript" view.

5. Frontend Requirements (Next.js)
Components

    URLInput: Simple form to submit video.

    VideoWorkspace: The main page after submission.

        PlayerPanel: Wraps react-player. Must expose a seekTo(seconds) method.

        TranscriptPanel: Lists all sentences.

            Feature: Clicking a sentence seeks the video to that time.

            Feature: "Active Highlighting" - highlights the current sentence as video plays.

        ChatPanel: Standard chat interface.

            Feature: If AI response contains [04:20], render it as a clickable button that seeks the video.

6. Implementation Phase Guide

(Use this to tell Claude where to start)

Phase 1: Backend Core

    Set up FastAPI.

    Implement yt-dlp download function.

    Implement OpenAI Whisper API integration.

    Test with a real YouTube link.

Phase 2: Vector Database Integration

    Set up Pinecone client.

    Implement embedding logic.

    Create the /chat endpoint with RAG.

Phase 3: Frontend Setup

    Initialize Next.js project.

    Build the PlayerPanel and sync it with dummy transcript data.

    Connect Frontend to Backend API.