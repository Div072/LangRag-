# LangRag

YouTube language-learning RAG app.

## Current Vector DB Choice

Phase 1 uses a local vector database (Chroma, persisted on disk) for video indexing and retrieval.

## Backend

1. Create env file:
   - `cp backend/.env.example backend/.env`
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Run API:
   - `cd backend && uvicorn main:app --reload`

## Frontend

1. Install dependencies:
   - `cd frontend && npm install`
2. Configure env:
   - `cp .env.local.example .env.local`
3. Run app:
   - `npm run dev`

## API Endpoints

- `POST /process-video`
- `POST /chat`
- `GET /transcript/{video_id}`
