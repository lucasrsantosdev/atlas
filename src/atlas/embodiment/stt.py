"""Whisper.cpp adapter; actual model and executable are operator supplied."""
from .providers import WhisperCppSTT
__all__=["WhisperCppSTT"]


from dataclasses import dataclass

@dataclass(frozen=True)
class Transcript:
    text: str
    language: str = "pt"
    confidence: float | None = None

class TranscriptionError(RuntimeError):
    pass

def transcribe_checked(provider, audio: bytes) -> Transcript:
    if not isinstance(audio, bytes) or not audio:
        raise ValueError("audio required")
    try:
        text = provider.transcribe(audio)
    except (OSError, TimeoutError, RuntimeError) as exc:
        raise TranscriptionError("STT provider unavailable") from exc
    if not isinstance(text, str) or not text.strip():
        raise TranscriptionError("empty transcription")
    return Transcript(text.strip())
