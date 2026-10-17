import pytest
from atlas.embodiment.session import VoiceSession


class STT:
    def transcribe(self, audio): return 'Olá'


class TTS:
    def synthesize(self, text): return text.encode()


class Reply:
    def reply(self, text, history): return f'{text} ({len(history)})'


def test_voice_session_history():
    session = VoiceSession(STT(), TTS(), Reply(), max_turns=2)
    assert session.process(b'audio') == ('Olá (0)', 'Olá (0)'.encode())
    session.process(b'audio')
    session.process(b'audio')
    assert len(session.history) == 2


class V3STT:
    def transcribe(self, audio): return "oi"


class V3TTS:
    def synthesize(self, text): return b"wav"


class V3LLM:
    def reply(self, text, history): return "olá"


def test_voice_session_rejects_invalid_history_limit():
    with pytest.raises(ValueError):
        VoiceSession(V3STT(), V3TTS(), V3LLM(), max_turns=0).process(b"wav")


def test_voice_session_rejects_empty_audio_output_without_history_mutation():
    class EmptyTTS:
        def synthesize(self, text): return b""
    session = VoiceSession(V3STT(), EmptyTTS(), V3LLM())
    with pytest.raises(ValueError): session.process(b"wav")
    assert session.history == []


def test_voice_session_rejects_empty_llm_answer():
    class EmptyLLM:
        def reply(self, text, history): return "  "
    session = VoiceSession(V3STT(), V3TTS(), EmptyLLM())
    with pytest.raises(ValueError): session.process(b"wav")
    assert session.history == []
