from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """
    Parsed representation of a steering wheel configuration file.
    """

    name: str = Field(description="A descriptive name for the steering wheel device(s). One device may have multiple virtual devices.")
    broker: BrokerSection = Field(description="RemotiveBroker connection details")
    devices: dict[str, VirtualDeviceSection] = Field(description="Map of virtual device names to their button mappings")


class BrokerSection(BaseModel):
    """
    Broker specific configuration.

    The steering_wheel app can only connect to one broker.
    """

    url: str


class VirtualDeviceSection(BaseModel):
    """
    A section of button mappings for a virtual device.
    """

    button_mappings: list[ButtonMapping]


class ButtonMapping(BaseModel):
    """
    Mapping of a single physical button (or pedal) for a virtual device.
    """

    # descriptive name for the mapping, e.g. "hazard button"
    description: str

    type: Literal["axis", "button"]
    source_name: str
    source_type: int
    source_code: int

    target_name: str
    target_signal: str

    # for axis type. Used for linear mapping of the axis.
    gradient: float | None = None
    intercept: float | None = None
    min: float | None = None
    max: float | None = None

    # for button type. Used when a button produces more than one event, e.g. the turn stalk "button".
    mapping: dict[int, int] | None = None

    # JSON does not allow integer keys, so we need to convert them from strings to integers
    @field_validator("mapping", mode="before")
    @classmethod
    def convert_mapping_keys(cls, v: dict | None) -> dict[int, int] | None:
        if v is None:
            return None
        return {int(k): v[k] for k in v}


def read_config(path: Path) -> Config:
    """
    Read a steering wheel config from a file.

    Raises:
        ValueError: If the config is invalid.
    """
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
        return Config.model_validate(config)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid device config: {str(e)}") from e
