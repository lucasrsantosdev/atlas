"""Piper adapter; audio playback is a separate output concern."""
from .providers import PiperTTS
__all__=["PiperTTS"]


import re

def split_speech(text: str, *, max_chars: int = 180) -> tuple[str, ...]:
    if not isinstance(text, str) or not text.strip() or max_chars < 1:
        raise ValueError("invalid speech request")
    words = text.split()
    chunks = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            raise ValueError("word exceeds chunk limit")
        if current and len(current) + 1 + len(word) > max_chars:
            chunks.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        chunks.append(current)
    return tuple(chunks)

class SpeechQueue:
    def __init__(self, provider):
        self.provider = provider
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def synthesize(self, text: str, *, max_chars: int = 180) -> tuple[bytes, ...]:
        self.cancelled = False
        output = []
        for chunk in split_speech(text, max_chars=max_chars):
            if self.cancelled:
                break
            audio = self.provider.synthesize(chunk)
            if not isinstance(audio, bytes) or not audio:
                raise ValueError("TTS returned invalid audio")
            output.append(audio)
        return tuple(output)
