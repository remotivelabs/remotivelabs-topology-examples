from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import cast

import structlog
from remotivelabs.broker import BrokerClient, Frame, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from remotivelabs.topology.namespaces.generic import GenericNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class TCU:
    ecu_name: str = "TCU"
    vss_namespace_name: str = "TCU-VSS"
    body_can_namespace_name: str = "TCU-BodyCan0"

    vss_latitude: str = "Vehicle.CurrentLocation.Latitude"
    vss_longitude: str = "Vehicle.CurrentLocation.Longitude"
    latitude_signal: str = "LocationFrame.Latitude"
    longitude_signal: str = "LocationFrame.Longitude"
    lat: float | None = None
    lng: float | None = None

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.body_can = CanNamespace(
            TCU.body_can_namespace_name,
            broker_client=self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=TCU.ecu_name)], delay_multiplier=avp.delay_multiplier)],
        )
        self.vss = GenericNamespace(
            TCU.vss_namespace_name,
            broker_client=self._broker_client,
        )
        self.bm = BehavioralModel(
            TCU.ecu_name,
            namespaces=[self.vss, self.body_can],
            broker_client=self._broker_client,
            input_handlers=[
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=TCU.vss_latitude)],
                    self.on_latitude,
                ),
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=TCU.vss_longitude)],
                    self.on_longitude,
                ),
            ],
        )

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def on_latitude(self, frame: Frame) -> None:
        self.lat = cast(float, frame.value)
        await self._handle_location_state()

    async def on_longitude(self, frame: Frame) -> None:
        self.lng = cast(float, frame.value)
        await self._handle_location_state()

    async def _handle_location_state(self) -> None:
        if self.lat is not None and self.lng is not None:
            await self.body_can.restbus.update_signals(
                RestbusSignalConfig.set(name=TCU.latitude_signal, value=self.lat),
                RestbusSignalConfig.set(name=TCU.longitude_signal, value=self.lng),
            )
            self.lat = None
            self.lng = None


async def main(avp: BehavioralModelArgs):
    logger.info("Starting TCU ECU", args=avp)
    async with TCU(avp) as tcu:
        await tcu


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
