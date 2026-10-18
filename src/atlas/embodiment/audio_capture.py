"""Audio framing and silence detection; hardware microphone remains pluggable."""
from __future__ import annotations
import array
import math
import sys
import io
import wave

class AudioFramer:
    def __init__(self, rate=16000, threshold=300, max_seconds=15):
        if rate <= 0 or threshold < 0 or max_seconds <= 0: raise ValueError("invalid audio settings")
        self.rate=rate;self.threshold=threshold;self.max_seconds=max_seconds

    def wav(self, pcm:bytes) -> bytes:
        if not pcm or len(pcm)%2 or len(pcm)>self.rate*2*self.max_seconds: raise ValueError("invalid PCM frame")
        with io.BytesIO() as buffer:
            with wave.open(buffer,"wb") as out:
                out.setnchannels(1);out.setsampwidth(2);out.setframerate(self.rate);out.writeframes(pcm)
            return buffer.getvalue()

    def has_speech(self, pcm:bytes) -> bool:
        if not pcm or len(pcm)%2: return False
        samples=array.array("h")
        samples.frombytes(pcm)
        if sys.byteorder != "little": samples.byteswap()
        return math.sqrt(sum(sample*sample for sample in samples)/len(samples))>=self.threshold


class AudioBuffer:
    """Bounded PCM16 mono buffer with deterministic silence segmentation."""
    def __init__(self, *, rate=16000, max_seconds=15, threshold=300):
        self.framer = AudioFramer(rate=rate, max_seconds=max_seconds, threshold=threshold)
        self.capacity = int(rate * max_seconds * 2)
        self.data = bytearray()

    def push(self, pcm: bytes):
        if not isinstance(pcm, bytes) or len(pcm) % 2:
            raise ValueError("PCM16 frames must be even-sized bytes")
        if len(self.data) + len(pcm) > self.capacity:
            raise BufferError("audio buffer capacity exceeded")
        self.data.extend(pcm)

    def flush(self) -> bytes:
        result = bytes(self.data)
        self.data.clear()
        return result

    def speech_detected(self) -> bool:
        return self.framer.has_speech(bytes(self.data))
