import pytest
from atlas.robotics.protocol import Command, ProtocolError, encode_command, decode_command
from atlas.robotics.motion import JointLimit, interpolate_motion
from atlas.robotics.simulator import RobotSimulator
from atlas.robotics.controller import RobotController, RobotState
from atlas.robotics.sensors import SensorHub, SensorSample


def test_wire_roundtrip():
    cmd = Command('sim', 'led', {'on': True})
    result, seq = decode_command(encode_command(cmd, sequence=7))
    assert result == cmd and seq == 7

@pytest.mark.parametrize('frame', [b'', b'{', b'[]', b'{"payload":{},"crc32":"00000000"}'])
def test_reject_malformed_wire(frame):
    with pytest.raises(ProtocolError): decode_command(frame)

def test_reject_corrupted_wire():
    frame = encode_command(Command('sim', 'led', {'on': True}), sequence=1)
    with pytest.raises(ProtocolError): decode_command(frame.replace(b'true', b'null'))

@pytest.mark.parametrize('sequence', [-1, True, 1.5])
def test_reject_invalid_sequence(sequence):
    with pytest.raises(ProtocolError): encode_command(Command('sim','heartbeat'), sequence=sequence)

def test_reject_nan_payload():
    with pytest.raises(ProtocolError): encode_command(Command('sim','servo',{'angle':float('nan')}), sequence=1)

def test_interpolation_bounds_and_endpoint():
    steps = interpolate_motion(90, 110, joint='head', limit=JointLimit(max_delta=2), max_velocity=20, max_acceleration=40, dt=.05)
    assert steps[-1].angle == 110
    assert all(90 <= s.angle <= 110 for s in steps)
    assert all(abs(b.angle-a.angle) <= 2 for a,b in zip(steps,steps[1:]))
    assert all(b.at_seconds > a.at_seconds for a,b in zip(steps,steps[1:]))

def test_interpolation_rejects_out_of_range():
    with pytest.raises(ValueError): interpolate_motion(90, 170, joint='head', limit=JointLimit(), max_velocity=10, max_acceleration=10)

def test_recovery_requires_operator():
    sim = RobotSimulator()
    c = RobotController(sim)
    c.connect(); c.emergency_stop()
    with pytest.raises(PermissionError): c.recover()
    c.recover(local_operator_confirmed=True)
    assert c.state == RobotState.READY

def test_sensor_freshness():
    hub = SensorHub()
    hub.publish(SensorSample('temp', 22, 'C', 10))
    assert 'temp' in hub.fresh_snapshot(now=11, max_age=2)
    assert not hub.fresh_snapshot(now=20, max_age=2)

def test_simulated_sensor_fault_latches():
    sim = RobotSimulator();sim.inject_sensor_fault('temp')
    with pytest.raises(PermissionError):sim.execute(Command(sim.device,'led',{'on':True}))
