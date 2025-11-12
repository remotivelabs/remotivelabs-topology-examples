from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.some_ip import SomeIPEvent, SomeIPNamespace

from .broker_to_cuttlefish import BrokerToCuttlefish
from .broker_to_emulator import BrokerToEmulator
from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class IHU:
    someip_ns: str = "IHU-SOMEIP"
    ecu_name: str = "IHU"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        # capture the running loop (must be created inside a running asyncio loop)
        self._loop = asyncio.get_running_loop()
        self.br_emulator = None
        self.br_cuttlefish = None
        virtual_device_type = os.getenv("VIRTUAL_DEVICE_TYPE") or "none"

        if virtual_device_type == "android_emulator":
            emulator_name = os.getenv("ANDROID_EMULATOR_NAME") or "emulator-5554"
            self.br_emulator = BrokerToEmulator(emulator_name=emulator_name, vhal_callback=self._vhal_callback)

        if virtual_device_type == "cuttlefish":
            cuttlefish_gnss_url = os.getenv("CUTTLEFISH_GNSS_URL") or "https://localhost:1443/devices/cvd-1"
            cuttlefish_vhal_url = os.getenv("CUTTLEFISH_VHAL_URL") or "localhost:9300"
            self.br_cuttlefish = BrokerToCuttlefish(
                cuttlefish_gnss_url=cuttlefish_gnss_url, cuttlefish_vhal_url=cuttlefish_vhal_url, vhal_callback=self._vhal_callback
            )

        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)
        self._some_ip_eth = SomeIPNamespace(IHU.someip_ns, client_id=3, broker_client=self._broker_client)

        self.bm = BehavioralModel(
            IHU.ecu_name,
            namespaces=[self._some_ip_eth],
            broker_client=self._broker_client,
            input_handlers=[
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="TurnlightIndicator", event_name="TurnlightControlEvent")],
                    self._handle_indicator_event,
                ),
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="LocationService", event_name="LocationEvent")],
                    self._handle_location_event,
                ),
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="SpeedService", event_name="SpeedEvent")],
                    self._handle_speed_event,
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

    async def _handle_indicator_event(self, event: SomeIPEvent) -> None:
        # left = event.parameters.get("LeftTurnlight", 0)
        # right = event.parameters.get("RightTurnlight", 0)

        # if left:
        #     # logger.info("Left turnlight activated", someip_event=event)
        #     br_prop.set_property(289408008, 0, 2)
        #     # handle left turnlight logic here
        # elif right:
        #     # logger.info("Right turnlight activated", someip_event=event)
        #     br_prop.set_property(289408008, 0, 1)
        #     # handle right turnlight logic here
        # else:
        #     br_prop.set_property(289408008, 0, 0)
        #     # logger.info("No turnlight activated", someip_event=event)
        pass

    async def _handle_location_event(self, event: SomeIPEvent):
        lon = float(event.parameters.get("Longitude", 0))
        lat = float(event.parameters.get("Latitude", 0))
        if self.br_emulator is not None:
            self.br_emulator.redirect_location_signals_to_emulator(lon, lat)
        if self.br_cuttlefish:
            self.br_cuttlefish.redirect_location_signals_to_cuttlefish(lon, lat)

    async def _handle_speed_event(self, event: SomeIPEvent):
        speed = float(event.parameters.get("Speed", 0))
        if self.br_emulator is not None:
            self.br_emulator.update_speed_property(speed)
        if self.br_cuttlefish:
            self.br_cuttlefish.update_speed_property(speed)

    async def _send_someip_event(self, name, service_instance_name, parameters) -> None:
        await self._some_ip_eth.notify(SomeIPEvent(name=name, service_instance_name=service_instance_name, parameters=parameters))

    def _vhal_callback(self, name: str, service_instance_name: str, parameters: dict[str, Any]) -> None:
        fut = asyncio.run_coroutine_threadsafe(self._send_someip_event(name, service_instance_name, parameters), self._loop)

        # optionally log callback errors
        def _done(f):
            try:
                f.result()
            except Exception:
                logger.exception("on_vhal_interaction failed")

        fut.add_done_callback(_done)


async def main(avp: BehavioralModelArgs):
    logger.info("Starting IHU ECU", args=avp)

    async with IHU(avp) as ihu:
        await ihu


if __name__ == "__main__":
    model_args = BehavioralModelArgs.parse()
    configure_logging(model_args.loglevel)
    asyncio.run(main(model_args))
