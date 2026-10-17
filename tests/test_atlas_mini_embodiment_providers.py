import io
import json
from unittest.mock import patch
import pytest
from atlas.embodiment.providers import WhisperCppSTT, PiperTTS, OllamaResponder
from atlas.embodiment.session import VoiceSession


def test_ollama_history_and_no_cloud_fallback():
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b''
    def fake_urlopen(request, timeout):
        body = json.loads(request.data)
        assert body['messages'] == [
            {'role':'user','content':'Oi'},
            {'role':'assistant','content':'Olá'},
            {'role':'user','content':'Tudo bem?'}]
        assert request.full_url.startswith('http://127.0.0.1:')
        return io.BytesIO(json.dumps({'message':{'content':'Tudo ótimo'}}).encode())
    with patch('atlas.embodiment.providers.urlopen', side_effect=fake_urlopen):
        assert OllamaResponder('qwen2.5:3b').reply('Tudo bem?', [('Oi','Olá')]) == 'Tudo ótimo'


def test_stt_requires_wav():
    with pytest.raises(ValueError):
        WhisperCppSTT('whisper-cli', 'model.bin').transcribe(b'not audio')


def test_tts_rejects_empty_text():
    with pytest.raises(ValueError):
        PiperTTS('piper', 'voice.onnx').synthesize(' ')


def test_voice_history_not_updated_when_tts_fails():
    class STT:
        def transcribe(self, audio): return 'oi'
    class LLM:
        def reply(self, text, history): return 'olá'
    class TTS:
        def synthesize(self, text): raise RuntimeError('failed')
    session = VoiceSession(STT(), TTS(), LLM())
    with pytest.raises(RuntimeError): session.process(b'audio')
    assert session.history == []
