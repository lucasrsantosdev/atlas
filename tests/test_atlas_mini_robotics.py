import pytest
from atlas.hardware.gateway import HardwareGateway, simulated_atlas_mini


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


def test_estop_propagates_to_device_and_latches():
    gw = HardwareGateway()
    dev = simulated_atlas_mini()
    gw.register(dev)
    assert gw.emergency_stop() == {}
    assert dev.state['stopped'] is True
    assert gw.execute(dev.id, 'device.health')['healthy'] is True
    with pytest.raises(PermissionError):
        gw.execute(dev.id, 'servo.set_angle', angle=90)
    gw.reset_emergency_stop()
    with pytest.raises(PermissionError):
        gw.execute(dev.id, 'servo.set_angle', angle=90)


@pytest.mark.parametrize('angle', [float('nan'), float('inf'), float('-inf')])
def test_servo_rejects_nonfinite(angle):
    gw = HardwareGateway()
    gw.register(simulated_atlas_mini())
    with pytest.raises(ValueError):
        gw.execute('atlas-mini-sim', 'servo.set_angle', angle=angle)


def test_estop_blocks_led_as_well_as_servo_after_software_reset():
    gateway = HardwareGateway()
    gateway.register(simulated_atlas_mini())
    gateway.emergency_stop()
    gateway.reset_emergency_stop()
    for capability, kwargs in [("led.control", {"on": True}), ("servo.set_angle", {"angle": 90})]:
        with pytest.raises(PermissionError):
            gateway.execute("atlas-mini-sim", capability, **kwargs)
