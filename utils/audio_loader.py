
from langchain_core.documents import Document
from typing import List
import whisper
import os


def transcribe_audio(path: str) -> List[Document]:
    """
    Transcribes an audio file using OpenAI Whisper (runs locally).
    Supports: mp3, mp4, wav, m4a, flac, ogg, webm

    Why Whisper?
    - Runs 100% locally — no API needed
    - Supports 99 languages
    - Free forever
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file not found: {path}")

    print(f"🎙️ Transcribing: {path}")
    print("  ⏳ Loading Whisper model...")

    # base = fast, good quality
    
    model = whisper.load_model("base")

    print("  ⏳ Transcribing audio...")
    result = model.transcribe(path)

    doc = Document(
        page_content=result["text"],
        metadata={
            "doc_type": "audio",
            "source": path,
            "language": result.get("language", "unknown"),
        }
    )

    print(f"  ✅ Transcribed {len(result['text'])} characters")
    return [doc]


# ── Test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    docs = transcribe_audio("test.mp3")
    print(f"Language: {docs[0].metadata['language']}")
    print(f"Transcript: {docs[0].page_content[:300]}")
    