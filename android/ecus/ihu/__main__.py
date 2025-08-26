from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.some_ip import SomeIPEvent, SomeIPNamespace

from .log import configure_logging
from .remotivelabs_android_emulator.br_generic_props_to_aaos import BrokerToAAOS
from .remotivelabs_android_emulator.br_location_to_emu import brokerToEmu
from .remotivelabs_android_emulator.libs.adb import device as adb
from .remotivelabs_android_emulator.libs.vhal_emulator.vhal_prop_consts_2_0 import vhal_props

logger = structlog.get_logger(__name__)


@dataclass
class IHU:
    someip_ns: str = "IHU-SOMEIP"
    ecu_name: str = "IHU"

    def __init__(self, avp: BehavioralModelArgs, br_emu: brokerToEmu) -> None:
        # capture the running loop (must be created inside a running asyncio loop)
        self._loop = asyncio.get_running_loop()

        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)
        br_prop = BrokerToAAOS(adb_device, user_callback=self._vhal_callback)

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
        self.br_emu = br_emu
        self.br_prop = br_prop

    # sync wrapper called from the BrokerToAAOS RX thread
    def _vhal_callback(self, msg: dict[str, Any]) -> None:
        fut = asyncio.run_coroutine_threadsafe(self.on_vhal_interaction(msg), self._loop)

        # optionally log callback errors
        def _done(f):
            try:
                f.result()
            except Exception:
                logger.exception("on_vhal_interaction failed")

        fut.add_done_callback(_done)

    async def on_vhal_interaction(self, msg) -> None:
        # Extract the first value from the 'value' field if it exists
        value = next(iter(getattr(msg, "value", [])), None)
        if not value or getattr(value, "prop", None) != vhal_props.HVAC_TEMPERATURE_SET:
            return  # Exit if no value or the property ID doesn't match

        # Extract the temperature and area_id
        area_id = getattr(value, "area_id", None)
        temperature = next(iter(getattr(value, "float_values", [])), None)
        if temperature is None:
            return

        if area_id == 49:  # Left temperature (ROW_1_LEFT | ROW_2_LEFT | ROW_2_CENTER)
            await self._some_ip_eth.notify(
                SomeIPEvent(
                    name="CompartmentControl",
                    service_instance_name="HVACService",
                    parameters={"LeftTemperature": temperature},
                )
            )
        # elif area_id == 68:  # Right temperature (ROW_1_RIGHT | ROW_2_RIGHT)
        #     await self._some_ip_eth.notify(
        #         SomeIPEvent(
        #             name="CompartmentControl",
        #             service_instance_name="HVACService",
        #             parameters={"RightTemperature": temperature},
        #         )
        #     )

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
        signals = {
            "LocationFrame.Longitude": float(event.parameters.get("Longitude", 0)),
            "LocationFrame.Latitude": float(event.parameters.get("Latitude", 0)),
        }
        br_emu.redirect_location_to_emulator_signals(signals)

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
        speed = float(event.parameters.get("Speed", 0))  # Extract speed from the event
        speed_mps = speed / 3.6
        self.br_prop.set_property(vhal_props.PERF_VEHICLE_SPEED, 0, speed_mps)


async def main(avp: BehavioralModelArgs, br_emu: brokerToEmu):
    logger.info("Starting IHU ECU", args=avp)

    async with IHU(avp, br_emu) as ihu:
        await ihu


if __name__ == "__main__":
    # Instantiate brokerToEmu and start location updates
    adb_device = adb.get_emulator_device()
    br_emu = brokerToEmu(adb_device)
    # br_prop = BrokerToAAOS(adb_device)

    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args, br_emu))
