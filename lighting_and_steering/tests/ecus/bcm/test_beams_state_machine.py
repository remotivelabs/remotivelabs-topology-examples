import pytest
from bcm.state_machines.beams import BeamsStateMachine, LightModePosition


@pytest.fixture(name="beams")
def _beams():
    return BeamsStateMachine()


def test_initial_state_is_off(beams):
    assert beams.state == "off"


def test_daylight_running_light_on_off(beams):
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.OFF)
    assert beams.state == "off"


def test_low_beam_from_off_does_not_work(beams):
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.LOW)
    assert beams.state == "off"


async def test_off_always_works(beams):
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.OFF)
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.LOW)
    assert beams.state == "low"

    beams.set_light_mode_position(LightModePosition.OFF)
    assert beams.state == "off"


def test_transitions_between_beams(beams):
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.LOW)
    assert beams.state == "low"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.OFF)
    assert beams.state == "off"


def test_drl_from_low_beam(beams):
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.LOW)
    assert beams.state == "low"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.LOW)
    assert beams.state == "low"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.set_light_mode_position(LightModePosition.OFF)
    assert beams.state == "off"


def test_reset(beams):
    assert beams.state == "off"

    beams.set_light_mode_position(LightModePosition.DRL)
    assert beams.state == "drl"

    beams.reset()
    assert beams.state == "off"
