from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient, Frame, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from remotivelabs.topology.namespaces.some_ip import SomeIPEvent, SomeIPNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class GWM:
    ecu_name: str = "GWM"
    someip_ns: str = "GWM-SOMEIP"
    can_ns: str = "GWM-BodyCan0"
    chassis_ns: str = "GWM-ChassisCan0"

    left_turn_light_request: str = "TurnLightControl.LeftTurnLightRequest"
    right_turn_light_request: str = "TurnLightControl.RightTurnLightRequest"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.someip_bus = SomeIPNamespace(
            GWM.someip_ns,
            client_id=99,
            broker_client=self._broker_client,
        )
        self.body_can_0 = CanNamespace(
            GWM.can_ns,
            broker_client=self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=GWM.ecu_name)], delay_multiplier=avp.delay_multiplier)],
        )
        self.chassis_can_0 = CanNamespace(GWM.chassis_ns, broker_client=self._broker_client)
        self.bm = BehavioralModel(
            GWM.ecu_name,
            namespaces=[self.someip_bus, self.body_can_0],
            broker_client=self._broker_client,
            input_handlers=[
                self.body_can_0.create_input_handler([filters.FrameFilter("TurnLightControl")], self.on_frame),
                self.body_can_0.create_input_handler([filters.FrameFilter("LocationFrame")], self.on_location_frame),
                self.chassis_can_0.create_input_handler([filters.FrameFilter("UISpeedFrame")], self.on_speed_frame),
                self.someip_bus.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="HVACService", event_name="CompartmentControl")],
                    self.on_hvac_control,
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

    async def on_frame(self, frame: Frame) -> None:
        await self.someip_bus.notify(
            SomeIPEvent(
                name="TurnlightControlEvent",
                service_instance_name="TurnlightIndicator",
                parameters={
                    "LeftTurnlight": frame.signals[self.left_turn_light_request],
                    "RightTurnlight": frame.signals[self.right_turn_light_request],
                },
            )
        )

    async def on_location_frame(self, frame: Frame) -> None:
        await self.someip_bus.notify(
            SomeIPEvent(
                name="LocationEvent",
                service_instance_name="LocationService",
                parameters={
                    "Longitude": frame.signals["LocationFrame.Longitude"],
                    "Latitude": frame.signals["LocationFrame.Latitude"],
                },
            )
        )

    async def on_speed_frame(self, frame: Frame) -> None:
        # Notify the SomeIPNamespace with the speed signal
        await self.someip_bus.notify(
            SomeIPEvent(
                name="SpeedEvent",
                service_instance_name="SpeedService",
                parameters={
                    "Speed": frame.signals["UISpeedFrame.uispeed"],
                },
            )
        )

    async def on_hvac_control(self, event: SomeIPEvent) -> None:
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set(name="HVACControl.LeftTemperature", value=float(event.parameters.get("LeftTemperature", 0))),
            RestbusSignalConfig.set(name="HVACControl.RightTemperature", value=float(event.parameters.get("RightTemperature", 0))),
        )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting GWM ECU", args=avp)
    async with GWM(avp) as gwm:
        await gwm


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
