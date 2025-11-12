from __future__ import annotations

from typing import NamedTuple

import structlog

from sccm.adapters.evdev_device import DeviceEvent
from sccm.config import ButtonMapping, Config
from sccm.mapper import Mapper

log = structlog.get_logger(__name__)


class Signal(NamedTuple):
    target: str
    signal_id: str
    value: float


class EvdevToTopologyMapper(Mapper):
    def __init__(self, config: Config):
        self.config = config

        # re-index the mapping by the evdev [name,type,code], so that we can look up the mapping by the event type/code
        self._keyed_mapping: dict[tuple[str, int, int], ButtonMapping] = {
            (name, mapping.source_type, mapping.source_code): mapping
            for name, device in config.devices.items()
            for mapping in device.button_mappings
        }

    def map_event(self, input_event: DeviceEvent) -> Signal | None:
        event_key = (input_event.device_name, input_event.event.type, input_event.event.code)
        if event_key not in self._keyed_mapping:
            return None

        mapping = self._keyed_mapping[event_key]
        signal_id = mapping.target_signal
        target = mapping.target_name

        # ignore invalid mapping type (you probably need to update the config)
        if mapping.type not in ["axis", "button"]:
            log.warning("invalid mapping type", mapping_type=mapping.type)
            return None

        if mapping.type == "axis":
            # ignore invalid axis config (you probably need to update the config)
            if mapping.gradient is None or mapping.intercept is None:
                log.warning("invalid axis config", gradient=mapping.gradient, intercept=mapping.intercept)
                return None

            # perform linear regression on the inputs
            value = mapping.gradient * input_event.event.value + mapping.intercept

            # use the min/max guards for non-exact input devices (that have floating min/max values)
            if mapping.min is not None:
                value = max(value, mapping.min)
            if mapping.max is not None:
                value = min(value, mapping.max)

        elif mapping.type == "button":
            if mapping.mapping is None:
                # If we have no mapping, we just use the raw value
                value = input_event.event.value
            else:
                # If we do have a mapping, we must use it. If we get values not in the mapping, we ignore them.
                value = mapping.mapping.get(input_event.event.value, None)
                if value is None:
                    log.debug("mapping value out of range", mapping=mapping, value=input_event.event.value)
                    return None

        return Signal(target=target, signal_id=signal_id, value=value)
