import json
import pytest
from atlas.hardware.gateway import HardwareGateway, simulated_atlas_mini
from atlas.embodiment.session import VoiceSession
from atlas.security.policy import PolicyEngine, Permission, AuditLog


def test_estop_blocks_led_as_well_as_servo_after_software_reset():
    gateway = HardwareGateway()
    gateway.register(simulated_atlas_mini())
    gateway.emergency_stop()
    gateway.reset_emergency_stop()
    for capability, kwargs in [("led.control", {"on": True}), ("servo.set_angle", {"angle": 90})]:
        with pytest.raises(PermissionError):
            gateway.execute("atlas-mini-sim", capability, **kwargs)


def test_approval_wrong_scope_does_not_destroy_valid_token():
    policy = PolicyEngine([Permission.HARDWARE_WRITE])
    token = policy.issue_approval(Permission.HARDWARE_WRITE, scope="servo:head")
    assert not policy.consume_approval(token, Permission.HARDWARE_WRITE, scope="servo:arm")
    assert policy.consume_approval(token, Permission.HARDWARE_WRITE, scope="servo:head")
    assert not policy.consume_approval(token, Permission.HARDWARE_WRITE, scope="servo:head")


def test_audit_file_detects_tampering(tmp_path):
    path = tmp_path / "audit.jsonl"
    audit = AuditLog(path)
    audit.record(event="example", allowed=False)
    assert audit.verify_file()
    events = [json.loads(x) for x in path.read_text().splitlines()]
    events[0]["allowed"] = True
    path.write_text(json.dumps(events[0]) + "\n")
    assert not audit.verify_file()


class STT:
    def transcribe(self, audio): return "oi"
class TTS:
    def synthesize(self, text): return b"wav"
class LLM:
    def reply(self, text, history): return "olá"


def test_voice_session_rejects_invalid_history_limit():
    with pytest.raises(ValueError):
        VoiceSession(STT(), TTS(), LLM(), max_turns=0).process(b"wav")


def test_voice_session_rejects_empty_audio_output_without_history_mutation():
    class EmptyTTS:
        def synthesize(self, text): return b""
    session = VoiceSession(STT(), EmptyTTS(), LLM())
    with pytest.raises(ValueError): session.process(b"wav")
    assert session.history == []


def test_voice_session_rejects_empty_llm_answer():
    class EmptyLLM:
        def reply(self, text, history): return "  "
    session = VoiceSession(STT(), TTS(), EmptyLLM())
    with pytest.raises(ValueError): session.process(b"wav")
    assert session.history == []
