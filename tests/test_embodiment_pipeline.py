import pytest
from atlas.embodiment.audio_capture import AudioFramer
from atlas.embodiment.dialogue import DialogueCoordinator
from atlas.embodiment.perception import PerceptionBuffer
from atlas.embodiment.gestures import gesture_steps


def test_pcm_wav_framing_and_silence():
    f=AudioFramer(threshold=100)
    assert f.wav(b'\x00\x00'*160).startswith(b'RIFF')
    assert not f.has_speech(b'\x00\x00'*160)
    assert f.has_speech(b'\xff\x7f'*160)


def test_audio_size_limit():
    with pytest.raises(ValueError):AudioFramer(max_seconds=1).wav(b'\x00\x00'*16001)


def test_dialogue_memory_adapter():
    class Memory:
        def __init__(self):self.saved=[]
        def recall(self,text):return 'remembered context'
        def remember(self,text,answer):self.saved.append((text,answer))
    class Responder:
        def reply(self,text,history):
            assert history[0][0]=='context'
            return 'ok'
    mem=Memory()
    assert DialogueCoordinator(Responder(),mem).reply('hello',[])=='ok'
    assert mem.saved==[('hello','ok')]


def test_perception_is_bounded():
    p=PerceptionBuffer(2)
    for i in range(3):p.add('sensor',str(i))
    assert [e.detail for e in p.events]==['1','2']


def test_gestures_are_allowlisted():
    assert len(gesture_steps('nod'))==2
    with pytest.raises(ValueError):gesture_steps('run_motor_forever')
