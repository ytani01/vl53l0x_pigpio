import pytest


def test_import_vl53l0x():
    try:
        from vl53l0x_pigpio import VL53L0X

        assert VL53L0X is not None
    except ImportError as e:
        pytest.fail(f"Failed to import VL53L0X: {e}")
