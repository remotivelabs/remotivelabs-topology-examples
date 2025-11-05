import pytest

from bcm.state_machines.gears import GearPositionChange, GearsStateMachine


@pytest.fixture(name="gears")
def _gears():
    return GearsStateMachine()


def test_initial_state_is_drive(gears):
    assert gears.state == "drive"


def test_changing_gears_up_in_drive_does_nothing(gears):
    assert gears.state == "drive"

    gears.change_gear_position(GearPositionChange.Up)
    assert gears.state == "drive"


def test_changing_gears_down_in_reverse_does_nothing(gears):
    assert gears.state == "drive"

    gears.change_gear_position(GearPositionChange.Down)
    assert gears.state == "reverse"

    gears.change_gear_position(GearPositionChange.Down)
    assert gears.state == "reverse"


def test_changing_gears_down_in_drive_goes_to_reverse(gears):
    assert gears.state == "drive"

    gears.change_gear_position(GearPositionChange.Down)
    assert gears.state == "reverse"


def test_changing_gears_up_in_reverse_goes_to_drive(gears):
    assert gears.state == "drive"

    gears.change_gear_position(GearPositionChange.Down)
    assert gears.state == "reverse"

    gears.change_gear_position(GearPositionChange.Up)
    assert gears.state == "drive"


def test_reset(gears):
    assert gears.state == "drive"

    gears.change_gear_position(GearPositionChange.Down)
    assert gears.state == "reverse"

    gears.reset()
    assert gears.state == "drive"
