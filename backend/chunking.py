from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Chunk:
    chunk_id: int
    start: float
    end: float
    text: str


def normalize_segments(raw_segments: Iterable[Dict[str, Any]]) -> List[TranscriptSegment]:
    normalized: List[TranscriptSegment] = []
    for row in raw_segments:
        text = str(row.get("text", "")).strip()
        if not text:
            continue

        start = float(row.get("start", 0.0))
        duration = float(row.get("duration", 0.0))
        end = max(start, start + duration)
        normalized.append(TranscriptSegment(start=start, end=end, text=text))

    normalized.sort(key=lambda s: s.start)
    return normalized


class BaseChunker:
    def chunk(self, segments: List[TranscriptSegment]) -> List[Chunk]:
        raise NotImplementedError


class SegmentCountChunker(BaseChunker):
    """Create chunks using a fixed number of transcript segments per chunk."""

    def __init__(self, segments_per_chunk: int = 6, overlap_segments: int = 1):
        if segments_per_chunk <= 0:
            raise ValueError("segments_per_chunk must be > 0")
        if overlap_segments < 0:
            raise ValueError("overlap_segments must be >= 0")
        if overlap_segments >= segments_per_chunk:
            raise ValueError("overlap_segments must be < segments_per_chunk")
        self.segments_per_chunk = segments_per_chunk
        self.overlap_segments = overlap_segments

    def chunk(self, segments: List[TranscriptSegment]) -> List[Chunk]:
        if not segments:
            return []

        step = self.segments_per_chunk - self.overlap_segments
        chunks: List[Chunk] = []
        chunk_id = 0

        for i in range(0, len(segments), step):
            window = segments[i : i + self.segments_per_chunk]
            if not window:
                break
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    start=window[0].start,
                    end=window[-1].end,
                    text=" ".join(s.text for s in window),
                )
            )
            chunk_id += 1
            if i + self.segments_per_chunk >= len(segments):
                break

        return chunks


class DurationChunker(BaseChunker):
    """Create chunks that do not exceed a time budget in seconds."""

    def __init__(self, max_duration_seconds: float = 30.0):
        if max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be > 0")
        self.max_duration_seconds = max_duration_seconds

    def chunk(self, segments: List[TranscriptSegment]) -> List[Chunk]:
        if not segments:
            return []

        chunks: List[Chunk] = []
        current: List[TranscriptSegment] = []
        chunk_id = 0

        for seg in segments:
            if not current:
                current.append(seg)
                continue

            projected_duration = seg.end - current[0].start
            if projected_duration <= self.max_duration_seconds:
                current.append(seg)
                continue

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    start=current[0].start,
                    end=current[-1].end,
                    text=" ".join(s.text for s in current),
                )
            )
            chunk_id += 1
            current = [seg]

        if current:
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    start=current[0].start,
                    end=current[-1].end,
                    text=" ".join(s.text for s in current),
                )
            )

        return chunks


class CharacterChunker(BaseChunker):
    """Create chunks capped by character length with segment overlap."""

    def __init__(self, max_chars: int = 700, overlap_segments: int = 1):
        if max_chars <= 0:
            raise ValueError("max_chars must be > 0")
        if overlap_segments < 0:
            raise ValueError("overlap_segments must be >= 0")
        self.max_chars = max_chars
        self.overlap_segments = overlap_segments

    def chunk(self, segments: List[TranscriptSegment]) -> List[Chunk]:
        if not segments:
            return []

        chunks: List[Chunk] = []
        current: List[TranscriptSegment] = []
        chunk_id = 0

        for seg in segments:
            candidate = current + [seg]
            candidate_text = " ".join(s.text for s in candidate)

            if current and len(candidate_text) > self.max_chars:
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        start=current[0].start,
                        end=current[-1].end,
                        text=" ".join(s.text for s in current),
                    )
                )
                chunk_id += 1
                if self.overlap_segments > 0:
                    current = current[-self.overlap_segments :]
                else:
                    current = []

            current.append(seg)

        if current:
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    start=current[0].start,
                    end=current[-1].end,
                    text=" ".join(s.text for s in current),
                )
            )

        return chunks


def get_chunker(strategy: str, **kwargs: Any) -> BaseChunker:
    strategy_key = strategy.strip().lower()
    if strategy_key == "segment_count":
        return SegmentCountChunker(**kwargs)
    if strategy_key == "duration":
        return DurationChunker(**kwargs)
    if strategy_key == "character":
        return CharacterChunker(**kwargs)
    raise ValueError(
        "Unsupported strategy. Use one of: segment_count, duration, character."
    )


def build_chunks(
    raw_segments: Iterable[Dict[str, Any]],
    strategy: str = "segment_count",
    **strategy_kwargs: Any,
) -> List[Dict[str, Any]]:
    segments = normalize_segments(raw_segments)
    chunker = get_chunker(strategy, **strategy_kwargs)
    chunks = chunker.chunk(segments)
    return [
        {
            "chunk_id": c.chunk_id,
            "start": c.start,
            "end": c.end,
            "text": c.text,
        }
        for c in chunks
    ]
