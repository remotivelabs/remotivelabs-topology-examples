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

from .br_generic_props_to_aaos import BrokerToAAOS
from .br_location_to_emu import BrokerToEmu
from .libs.adb.adb_emulator import AndroidEmulator
from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class IHU:
    someip_ns: str = "IHU-SOMEIP"
    ecu_name: str = "IHU"

    def __init__(self, avp: BehavioralModelArgs, android_emulator: AndroidEmulator) -> None:
        # capture the running loop (must be created inside a running asyncio loop)
        self._loop = asyncio.get_running_loop()

        self.br_emu = BrokerToEmu(android_emulator)
        self.br_prop = BrokerToAAOS(android_emulator, user_callback=self._vhal_callback)

        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)
        self._some_ip_eth = SomeIPNamespace(IHU.someip_ns, client_id=3, broker_client=self._broker_client)
        self.bm = BehavioralModel(
            IHU.ecu_name,
            namespaces=[self._some_ip_eth],
            broker_client=self._broker_client,
            input_handlers=[
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="TurnlightIndicator", event_name="TurnlightControlEvent")],
                    self.on_indicator,
                ),
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="LocationService", event_name="LocationEvent")],
                    self.on_location,
                ),
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="SpeedService", event_name="SpeedEvent")],
                    self.on_speed_event,
                ),
            ],
        )

    # sync wrapper called from the BrokerToAAOS RX thread
    def _vhal_callback(self, name: str, service_instance_name: str, parameters: dict[str, Any]) -> None:
        fut = asyncio.run_coroutine_threadsafe(self._send_someip_event(name, service_instance_name, parameters), self._loop)

        # optionally log callback errors
        def _done(f):
            try:
                f.result()
            except Exception:
                logger.exception("on_vhal_interaction failed")

        fut.add_done_callback(_done)

    async def _send_someip_event(self, name, service_instance_name, parameters) -> None:
        await self._some_ip_eth.notify(SomeIPEvent(name=name, service_instance_name=service_instance_name, parameters=parameters))

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def on_location(self, event: SomeIPEvent) -> None:
        self.br_emu.redirect_location_signals_to_emulator(event.parameters)

    async def on_indicator(self, event: SomeIPEvent) -> None:
        pass
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

    async def on_speed_event(self, event: SomeIPEvent) -> None:
        """
        Callback for handling SpeedEvent from the SpeedService.
        """
        self.br_prop.update_speed_property(event.parameters)


async def main(avp: BehavioralModelArgs, android_emulator: AndroidEmulator):
    logger.info("Starting IHU ECU", args=avp)

    async with IHU(avp, android_emulator) as ihu:
        await ihu


if __name__ == "__main__":
    emulator_name = os.getenv("ANDROID_EMULATOR_NAME") or "emulator-5554"
    android_emulator = AndroidEmulator(emulator_name=emulator_name)
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args, android_emulator))
