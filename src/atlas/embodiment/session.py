"""Provider-independent voice conversation coordinator; no audio dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol

class SpeechToText(Protocol):
    def transcribe(self, audio: bytes) -> str: ...

class TextToSpeech(Protocol):
    def synthesize(self, text: str) -> bytes: ...

class Responder(Protocol):
    def reply(self, text: str, history: list[tuple[str, str]]) -> str: ...

@dataclass
class VoiceSession:
    stt: SpeechToText
    tts: TextToSpeech
    responder: Responder
    history: list[tuple[str, str]] = field(default_factory=list)
    max_turns: int = 6

    def process(self, audio: bytes) -> tuple[str, bytes]:
        if self.max_turns < 1:
            raise ValueError("max_turns must be positive")
        if not audio:
            raise ValueError("audio is empty")
        text = self.stt.transcribe(audio).strip()
        if not text:
            raise ValueError("no speech recognized")
        answer = self.responder.reply(text, list(self.history))
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("responder returned empty answer")
        speech = self.tts.synthesize(answer)
        if not isinstance(speech, bytes) or not speech:
            raise ValueError("TTS returned invalid audio")
        self.history.append((text, answer))
        self.history = self.history[-self.max_turns:]
        return answer, speech
