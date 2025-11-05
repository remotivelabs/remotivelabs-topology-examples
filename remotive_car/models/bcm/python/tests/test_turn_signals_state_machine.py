import asyncio
from unittest.mock import AsyncMock

import pytest

from bcm.state_machines.turn_signals import TurnSignalsStateMachine, TurnStalkPosition


@pytest.fixture()
def callback():
    return AsyncMock()


@pytest.fixture()
async def turn_signals(callback):
    with TurnSignalsStateMachine(callback=callback) as tsm:
        yield tsm
    await asyncio.sleep(0)  # give state machine a chance to properly cancel tasks


async def test_initial_state_is_off(turn_signals):
    assert turn_signals.state == "off"


@pytest.mark.asyncio
async def test_hazard_on_off(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "off"


@pytest.mark.asyncio
async def test_left_on_off(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "left_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    assert turn_signals.state == "off"


@pytest.mark.asyncio
async def test_right_on_off(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    assert turn_signals.state == "right_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    assert turn_signals.state == "off"


@pytest.mark.asyncio
async def test_hazard_on_from_any_state(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "off"


@pytest.mark.asyncio
async def test_turn_signals(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "left_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    assert turn_signals.state == "right_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "left_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    assert turn_signals.state == "right_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    assert turn_signals.state == "off"


@pytest.mark.asyncio
async def test_turn_signals_from_hazard_should_not_transition(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    assert turn_signals.state == "hazard_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "hazard_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    assert turn_signals.state == "hazard_on"


@pytest.mark.asyncio
async def test_turn_signals_from_hazard(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "left_on"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "left_on"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    assert turn_signals.state == "hazard_on"

    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "right_on"


@pytest.mark.asyncio
async def test_reset(turn_signals):
    assert turn_signals.state == "off"

    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "left_on"

    turn_signals.reset()
    assert turn_signals.state == "off"
    assert turn_signals.last_turnstalk_position == TurnStalkPosition.OFF


@pytest.mark.asyncio
async def test_blink_transitions(turn_signals):
    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    assert turn_signals.state == "left_on"

    turn_signals.trigger("blink")
    assert turn_signals.state == "left_off"

    turn_signals.trigger("blink")
    assert turn_signals.state == "left_on"


@pytest.mark.asyncio
async def test_hazard_blink_transitions(turn_signals):
    turn_signals.set_hazard_button_pressed()
    assert turn_signals.state == "hazard_on"

    turn_signals.trigger("blink")
    assert turn_signals.state == "hazard_off"

    turn_signals.trigger("blink")
    assert turn_signals.state == "hazard_on"


@pytest.mark.asyncio
async def test_callback_invoked_in_hazard_state(turn_signals, callback):
    turn_signals.set_hazard_button_pressed()
    # Wait for the first blink transition
    await asyncio.sleep(1.1)
    # Callback should be called with hazard_on and hazard_off states
    assert callback.call_args_list[0][0][0] in ["hazard_on", "hazard_off"]


@pytest.mark.asyncio
async def test_callback_invoked_in_left_state(turn_signals, callback):
    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    # Wait for the first blink transition
    await asyncio.sleep(1.1)
    # Callback should be called with left_on or left_off states
    assert callback.call_args_list[0][0][0] in ["left_on", "left_off"]


@pytest.mark.asyncio
async def test_callback_invoked_in_right_state(turn_signals, callback):
    turn_signals.set_turn_stalk_position(TurnStalkPosition.RIGHT)
    # Wait for the first blink transition
    await asyncio.sleep(1.1)
    # Callback should be called with right_on or right_off states
    assert callback.call_args_list[0][0][0] in ["right_on", "right_off"]


@pytest.mark.asyncio
async def test_callback_not_invoked_in_off_state(turn_signals, callback):  # noqa: ARG001
    # Wait for at least one tick
    await asyncio.sleep(1.1)
    callback.assert_not_called()


@pytest.mark.asyncio
async def test_callback_stops_when_state_changes(turn_signals, callback):
    turn_signals.set_turn_stalk_position(TurnStalkPosition.LEFT)
    # Wait for the first blink transition
    await asyncio.sleep(1.1)
    # Verify callback was called with left states
    assert any(args[0][0] in ["left_on", "left_off"] for args in callback.call_args_list)

    callback.reset_mock()
    turn_signals.set_turn_stalk_position(TurnStalkPosition.OFF)
    # No blink transitions in OFF state, so callback shouldn't be called
    await asyncio.sleep(1.1)
    callback.assert_not_called()
