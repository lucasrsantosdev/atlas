"""Optional offline-first STT/TTS and local LLM adapters.

No dependency is loaded or process started until invoked. Input is PCM WAV.
Models and binaries must be installed by the operator.
"""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import tempfile
from urllib.request import Request, urlopen


class WhisperCppSTT:
    def __init__(self, binary: str, model: str, *, timeout: float = 60):
        self.binary, self.model, self.timeout = binary, model, timeout

    def transcribe(self, audio: bytes) -> str:
        if not audio.startswith(b"RIFF") or b"WAVE" not in audio[:16]:
            raise ValueError("WhisperCppSTT expects WAV audio")
        with tempfile.TemporaryDirectory(prefix="atlas-stt-") as directory:
            source = Path(directory) / "input.wav"
            source.write_bytes(audio)
            result = subprocess.run(
                [self.binary, "-m", self.model, "-f", str(source), "-l", "pt", "-nt"],
                capture_output=True, text=True, timeout=self.timeout, check=True,
            )
            return result.stdout.strip()


class PiperTTS:
    def __init__(self, binary: str, model: str, *, timeout: float = 60):
        self.binary, self.model, self.timeout = binary, model, timeout

    def synthesize(self, text: str) -> bytes:
        if not text.strip():
            raise ValueError("text is empty")
        with tempfile.TemporaryDirectory(prefix="atlas-tts-") as directory:
            output = Path(directory) / "speech.wav"
            subprocess.run(
                [self.binary, "--model", self.model, "--output_file", str(output)],
                input=text, text=True, capture_output=True, timeout=self.timeout, check=True,
            )
            return output.read_bytes()


class OllamaResponder:
    """Local Ollama /api/chat adapter. No cloud API or implicit fallback."""
    def __init__(self, model: str, *, endpoint: str = "http://127.0.0.1:11434/api/chat", timeout: float = 60):
        self.model, self.endpoint, self.timeout = model, endpoint, timeout

    def reply(self, text: str, history: list[tuple[str, str]]) -> str:
        messages = []
        for question, answer in history:
            messages.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])
        messages.append({"role": "user", "content": text})
        payload = json.dumps({"model": self.model, "stream": False, "messages": messages}).encode()
        req = Request(self.endpoint, data=payload, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=self.timeout) as response:
            answer = json.load(response)["message"]["content"].strip()
        if not answer:
            raise ValueError("LLM returned empty answer")
        return answer
