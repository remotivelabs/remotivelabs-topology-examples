from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient, Frame
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.some_ip import SomeIPEvent, SomeIPNamespace
from remotivelabs.topology.namespaces.can import CanNamespace

from .log import configure_logging

from .remotivelabs_android_emulator.br_location_to_emu import brokerToEmu
from .remotivelabs_android_emulator.br_generic_props_to_aaos import BrokerToAAOS
from .remotivelabs_android_emulator.libs.adb import device as adb

logger = structlog.get_logger(__name__)


@dataclass
class IHU:
    someip_ns: str = "IHU-SOMEIP"
    ecu_name: str = "IHU"

    def __init__(self, avp: BehavioralModelArgs, br_emu: brokerToEmu, br_prop: BrokerToAAOS) -> None:
        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)

        self._some_ip_eth = SomeIPNamespace(IHU.someip_ns, client_id=3, broker_client=self._broker_client)
        # self._location_can = CanNamespace("IHU-LocationCan0", broker_client=self._broker_client)
        self.bm = BehavioralModel(
            IHU.ecu_name,
            namespaces=[self._some_ip_eth],
            broker_client=self._broker_client,
            input_handlers=[
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="TurnlightIndicator", event_name="TurnlightControlEvent")],
                    self.on_indicator,
                ),
                # self._location_can.create_input_handler(
                #     [filters.FrameFilter("LocationFrame")],
                #     self._location_listener,
                # ),
                # self._location_can.create_input_handler(
                #     [filters.FrameFilter("UISpeedFrame")],
                #     self._speed_listener,
                # )
            ],
        )
        self.br_emu = br_emu
        self.br_prop = br_prop

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

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

    # async def _speed_listener(self, frame: Frame) -> None:
    #     br_prop.set_property(291504647, 0, frame.signals["UISpeedFrame.uispeed"] / 3.6)  # Convert speed to m/s
    #     # set speed PERF_VEHICLE_SPEED

    # async def _location_listener(self, frame: Frame) -> None:
    #     br_emu.redirect_location_to_emulator_signals(frame.signals)


async def main(avp: BehavioralModelArgs, br_emu: brokerToEmu, br_prop: BrokerToAAOS):
    logger.info("Starting IHU ECU", args=avp)

    async with IHU(avp, br_emu, br_prop) as ihu:
        await ihu

if __name__ == "__main__":
    # Instantiate brokerToEmu and start location updates
    adb_device = adb.get_emulator_device()
    br_emu = brokerToEmu(adb_device)
    br_prop = BrokerToAAOS(adb_device)

    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args, br_emu, br_prop))
