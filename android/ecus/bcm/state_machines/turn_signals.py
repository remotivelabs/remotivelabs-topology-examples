from __future__ import annotations

import asyncio
from enum import Enum
from typing import Awaitable, Callable

import structlog
from remotivelabs.topology.time.async_ticker import create_ticker
from transitions.extensions import HierarchicalMachine

logger = structlog.get_logger(__name__)


class TurnStalkPosition(Enum):
    LEFT = "turn_left"
    RIGHT = "turn_right"
    OFF = "turn_off"


class TurnSignalsStateMachine:
    state: str
    trigger: Callable[[str], None]

    def __init__(self, blink_interval_in_sec: float = 1.0, callback: Callable[[str], Awaitable[None]] | None = None) -> None:
        self._callback = callback
        self._blink_interval = blink_interval_in_sec

        states = [
            "off",
            {"name": "hazard", "children": ["on", "off"]},
            {"name": "left", "children": ["on", "off"]},
            {"name": "right", "children": ["on", "off"]},
        ]
        transitions = [
            {"trigger": "emergency_mode", "source": "*", "dest": "hazard_on"},
            # Hazard transitions (we only trigger when hazard button is pressed, so that we don't have to press and hold it)
            {"trigger": "hazard_pressed", "source": ["off", "left_on", "left_off", "right_on", "right_off"], "dest": "hazard_on"},
            {"trigger": "hazard_pressed", "source": ["hazard_on", "hazard_off"], "dest": "left_on", "conditions": "is_turnstalk_to_left"},
            {"trigger": "hazard_pressed", "source": ["hazard_on", "hazard_off"], "dest": "right_on", "conditions": "is_turnstalk_to_right"},
            {"trigger": "hazard_pressed", "source": ["hazard_on", "hazard_off"], "dest": "off"},
            # Turn stalk transitions
            {"trigger": "turn_left", "source": ["off", "right_on", "right_off"], "dest": "left_on"},
            {"trigger": "turn_right", "source": ["off", "left_on", "left_off"], "dest": "right_on"},
            {"trigger": "turn_off", "source": ["left_on", "left_off", "right_on", "right_off"], "dest": "off"},
            # Blink transitions
            {"trigger": "blink", "source": "left_on", "dest": "left_off"},
            {"trigger": "blink", "source": "left_off", "dest": "left_on"},
            {"trigger": "blink", "source": "right_on", "dest": "right_off"},
            {"trigger": "blink", "source": "right_off", "dest": "right_on"},
            {"trigger": "blink", "source": "hazard_on", "dest": "hazard_off"},
            {"trigger": "blink", "source": "hazard_off", "dest": "hazard_on"},
        ]

        self.machine = HierarchicalMachine(
            model=self,
            states=states,
            initial="off",
            transitions=transitions,
            after_state_change=self._after_state_change,
            ignore_invalid_triggers=True,
        )
        self.last_turnstalk_position = TurnStalkPosition.OFF
        self._ticker: asyncio.Task | None = None

    def __enter__(self) -> TurnSignalsStateMachine:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def reset(self) -> None:
        self.close()

    def close(self) -> None:
        self.machine.set_state("off")
        self.last_turnstalk_position = TurnStalkPosition.OFF
        self._stop_blinking()

    def _start_blinking(self) -> None:
        self._ticker = create_ticker(on_tick=self.on_blink_tick, interval_in_sec=self._blink_interval)

    def _stop_blinking(self) -> None:
        if self._ticker:
            self._ticker.cancel()
        self._ticker = None

    async def on_blink_tick(self, elapsed_time: float, since_last_tick: float, total_drift: float, interval: float) -> None:  # noqa: ARG002
        self.trigger("blink")
        if self._callback:
            await self._callback(self.state)

    def on_enter_hazard(self) -> None:
        self._start_blinking()

    def on_exit_hazard(self) -> None:
        self._stop_blinking()

    def on_enter_left(self) -> None:
        self._start_blinking()

    def on_exit_left(self) -> None:
        self._stop_blinking()

    def on_enter_right(self) -> None:
        self._start_blinking()

    def on_exit_right(self) -> None:
        self._stop_blinking()

    def _after_state_change(self) -> None:
        logger.debug(f"{self.__class__.__name__}", state=self.state)

    def is_turnstalk_to_left(self) -> bool:
        return self.last_turnstalk_position == TurnStalkPosition.LEFT

    def is_turnstalk_to_right(self) -> bool:
        return self.last_turnstalk_position == TurnStalkPosition.RIGHT

    def set_hazard_button_pressed(self) -> str:
        self.trigger("hazard_pressed")
        return self.state

    def set_emergency_mode(self) -> str:
        self.trigger("emergency_mode")
        return self.state

    def set_turn_stalk_position(self, position: TurnStalkPosition) -> str:
        self.last_turnstalk_position = position
        self.trigger(position.value)
        return self.state

    def is_hazard_enabled(self) -> bool:
        return self.state.startswith("hazard")
