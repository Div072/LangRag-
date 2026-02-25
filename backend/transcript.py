from youtube_transcript_api import YouTubeTranscriptApi

try:
    from .chunking import build_chunks
except ImportError:
    from chunking import build_chunks


def get_video_id_from_url(url):
    if "youtube.com" in url:
        video_id = url.split("v=")[-1]
        if "&" in video_id:
            video_id = video_id.split("&")[0]
    elif "youtu.be" in url:
        video_id = url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL")
    return video_id
def get_transcript(url):
    video_id = get_video_id_from_url(url)
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    return transcript.to_raw_data()

# transcript is list of dictionaries with keys 'text', 'start', and 'duration'
#store in data/transcripts/ directory with filename as video_id.txt

def save_transcript_to_file(transcript, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for entry in transcript:
            f.write(f"{entry['start']}: {entry['text']}\n")


def chunk_transcript(url, strategy="segment_count", **strategy_kwargs):
    transcript = get_transcript(url)
    return build_chunks(transcript, strategy=strategy, **strategy_kwargs)


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=sX2nF1fW7kI"
    transcript = get_transcript(url)
    print(f"Transcript type: {type(transcript)}")
    save_transcript_to_file(transcript, f"./data/transcripts/{get_video_id_from_url(url)}.txt")
    chunks = chunk_transcript(url, strategy="segment_count", segments_per_chunk=6, overlap_segments=1)
    print(f"Built {len(chunks)} chunks using strategy=segment_count")
    print("Transcript saved successfully.")
