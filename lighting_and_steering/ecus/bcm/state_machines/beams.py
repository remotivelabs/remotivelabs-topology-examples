from __future__ import annotations

from enum import Enum
from typing import Callable

import structlog
from transitions import Machine

logger = structlog.get_logger(__name__)


class LightModePosition(Enum):
    OFF = "off"
    DRL = "drl"
    LOW = "low"


class BeamsStateMachine:
    state: str
    trigger: Callable[[str], None]

    def __init__(self) -> None:
        states = ["off", "drl", "low"]
        transitions = [
            {"trigger": "drl", "source": "off", "dest": "drl"},
            {"trigger": "low", "source": "drl", "dest": "low"},
            {"trigger": "drl", "source": "low", "dest": "drl"},
            {"trigger": "off", "source": "*", "dest": "off"},
        ]
        self.machine = Machine(
            model=self,
            states=states,
            initial="off",
            transitions=transitions,
            after_state_change=self._after_state_change,
            ignore_invalid_triggers=True,
        )

    def _after_state_change(self) -> None:
        logger.debug(f"{self.__class__.__name__}", state=self.state)

    def set_light_mode_position(self, position: LightModePosition) -> str:
        self.trigger(position.value)
        return self.state
