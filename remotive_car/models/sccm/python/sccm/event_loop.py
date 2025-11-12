from __future__ import annotations

import asyncio

import structlog

from sccm.device import Device
from sccm.mapper import Mapper
from sccm.target import Target

logger = structlog.get_logger(__name__)


class EventLoop:
    """
    TODO: Come up with a better name, and move to topology package.
    """

    device: Device
    mapper: Mapper
    target: Target

    def __init__(self, device: Device, mapper: Mapper, target: Target):
        self.device = device
        self.mapper = mapper
        self.target = target

    def create_task(self, event_loop: asyncio.BaseEventLoop | None = None) -> asyncio.Task[None]:
        """
        Returns a task that will run the main event loop.
        """
        if event_loop:
            return event_loop.create_task(self._loop())
        return asyncio.create_task(self._loop())

    async def _loop(self) -> None:
        """
        Main event loop that pulls events from the input device, maps them, and sends them to the target.
        """
        async with self.target as output:
            async with self.device as d:
                async for input_event in d.events_stream():
                    output_event = self.mapper.map_event(input_event=input_event)
                    if output_event:
                        logger.debug("sending event", output_event=output_event)
                        await output.send(output_event=output_event)
