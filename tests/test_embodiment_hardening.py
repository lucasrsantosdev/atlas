import pytest
from atlas.embodiment.audio_capture import AudioBuffer
from atlas.embodiment.stt import transcribe_checked, TranscriptionError
from atlas.embodiment.tts import split_speech, SpeechQueue
from atlas.embodiment.dialogue import DialogueCoordinator, BoundedDialogue
from atlas.embodiment.perception import PerceptionBuffer
from atlas.embodiment.gestures import GestureScheduler, GestureRequest
from atlas.embodiment.session import SessionLifecycle, SessionState


def test_audio_buffer_capacity_and_flush():
    b=AudioBuffer(rate=10,max_seconds=1,threshold=100)
    b.push(b'\x00\x00'*10)
    assert not b.speech_detected()
    with pytest.raises(BufferError):b.push(b'\x00\x00')
    assert len(b.flush())==20
    assert b.flush()==b''

def test_audio_buffer_rejects_odd_frames():
    with pytest.raises(ValueError):AudioBuffer().push(b'\x00')

def test_stt_contract():
    class STT:
        def transcribe(self,a):return ' ola '
    assert transcribe_checked(STT(),b'wav').text=='ola'

def test_stt_failure():
    class STT:
        def transcribe(self,a):raise TimeoutError()
    with pytest.raises(TranscriptionError):transcribe_checked(STT(),b'wav')

def test_speech_chunks_and_queue():
    class TTS:
        def synthesize(self,t):return t.encode()
    chunks=split_speech('um dois tres quatro',max_chars=8)
    assert chunks==('um dois','tres','quatro')
    assert SpeechQueue(TTS()).synthesize('ola mundo',max_chars=5)==(b'ola',b'mundo')

def test_dialogue_isolation_and_bound():
    class Responder:
        def reply(self,text,history):return str(len(history))
    d=BoundedDialogue(DialogueCoordinator(Responder()),max_turns=1)
    assert d.reply('a','hi')=='0'
    assert d.reply('b','hi')=='0'
    assert d.reply('a','hi')=='1'
    assert len(d.sessions['a'])==1

def test_perception_expiry():
    p=PerceptionBuffer();p.add('camera','motion',timestamp=10)
    assert len(p.recent(now=11,max_age=2))==1
    assert not p.recent(now=20,max_age=2)

def test_gesture_priority_and_cancel():
    s=GestureScheduler()
    assert s.schedule(GestureRequest('nod',2))
    assert not s.schedule(GestureRequest('neutral',1))
    assert s.active.name=='nod'
    s.cancel();assert s.active is None

def test_session_state_machine():
    s=SessionLifecycle()
    with pytest.raises(ValueError):s.transition(SessionState.SPEAKING)
    s.transition(SessionState.LISTENING)
    s.transition(SessionState.THINKING)
    s.transition(SessionState.SPEAKING)
    s.transition(SessionState.IDLE)
    assert s.state==SessionState.IDLE
