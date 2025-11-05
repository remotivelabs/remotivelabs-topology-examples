from __future__ import annotations

from enum import Enum
from typing import Callable

import structlog
from transitions import Machine

logger = structlog.get_logger(__name__)


class GearPositionChange(Enum):
    Up = "up"
    Down = "down"


class GearsStateMachine:
    state: str
    trigger: Callable[[str], None]

    def __init__(self) -> None:
        states = ["reverse", "drive"]
        transitions = [
            {"trigger": "up", "source": "reverse", "dest": "drive"},
            {"trigger": "down", "source": "drive", "dest": "reverse"},
        ]
        self.machine = Machine(
            model=self,
            states=states,
            initial="drive",
            transitions=transitions,
            after_state_change=self._after_state_change,
            ignore_invalid_triggers=True,
        )

    def reset(self) -> None:
        self.machine.set_state("drive")

    def _after_state_change(self) -> None:
        logger.debug(f"{self.__class__.__name__}", state=self.state)

    def change_gear_position(self, change: GearPositionChange) -> str:
        self.trigger(change.value)
        return self.state
