import pytest
from atlas.hardware.gateway import HardwareGateway, simulated_atlas_mini
from atlas.embodiment.session import VoiceSession

def test_servo_limits_and_estop():
    gateway = HardwareGateway()
    gateway.register(simulated_atlas_mini())
    assert gateway.execute('atlas-mini-sim', 'servo.set_angle', angle=90) == {'angle': 90}
    for angle in [-1, 151, True, '90']:
        with pytest.raises(ValueError):
            gateway.execute('atlas-mini-sim', 'servo.set_angle', angle=angle)
    gateway.emergency_stop()
    with pytest.raises(PermissionError):
        gateway.execute('atlas-mini-sim', 'servo.set_angle', angle=90)

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
