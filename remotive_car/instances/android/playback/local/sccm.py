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
class SCCM:
    ecu_name: str = "SCCM"
    vss_namespace_name: str = "SCCM-VSS"
    driver_can_namespace_name: str = "SCCM-DriverCan0"

    vss_indicator_left: str = "Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling"
    vss_indicator_right: str = "Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling"
    vss_steering_wheel_angle: str = "Vehicle.Chassis.SteeringWheel.Angle"
    vss_brake_pedal_position: str = "Vehicle.Chassis.Brake.PedalPosition"
    vss_accelerator_pedal_position: str = "Vehicle.Chassis.Accelerator.PedalPosition"

    turnstalk_frame: str = "TurnStalk"
    turnstalk_signal: str = "TurnStalk.TurnSignal"

    accelerator_pedal_frame: str = "AcceleratorPedalPositionSensor"
    accelerator_pedal_signal: str = "AcceleratorPedalPositionSensor.AcceleratorPedalPosition"

    brake_pedal_frame: str = "BrakePedalPositionSensor"
    brake_pedal_signal: str = "BrakePedalPositionSensor.BrakePedalPosition"

    steering_angle_frame: str = "SteeringAngle"
    steering_angle_signal: str = "SteeringAngle.SteeringAngle"

    indicator_left: bool | None = None
    indicator_right: bool | None = None
    accelerator_pedal: int = 0
    brake_pedal: int = 0
    steering_angle: float = 0.0

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.driver_can = CanNamespace(
            SCCM.driver_can_namespace_name,
            broker_client=self._broker_client,
            restbus_configs=[
                RestbusConfig(
                    [
                        filters.FrameFilter(frame_name=SCCM.turnstalk_frame),
                        filters.FrameFilter(frame_name=SCCM.accelerator_pedal_frame),
                        filters.FrameFilter(frame_name=SCCM.brake_pedal_frame),
                        filters.FrameFilter(frame_name=SCCM.steering_angle_frame),
                    ],
                    delay_multiplier=avp.delay_multiplier,
                )
            ],
        )
        self.vss = GenericNamespace(
            SCCM.vss_namespace_name,
            broker_client=self._broker_client,
        )
        self.bm = BehavioralModel(
            SCCM.ecu_name,
            namespaces=[self.vss, self.driver_can],
            broker_client=self._broker_client,
            input_handlers=[
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=SCCM.vss_indicator_left)],
                    self.on_indicator_left,
                ),
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=SCCM.vss_indicator_right)],
                    self.on_indicator_right,
                ),
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=SCCM.vss_accelerator_pedal_position)],
                    self.on_accelerator_pedal,
                ),
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=SCCM.vss_brake_pedal_position)],
                    self.on_brake_pedal,
                ),
                self.vss.create_input_handler(
                    [filters.FrameFilter(frame_name=SCCM.vss_steering_wheel_angle)],
                    self.on_steering_angle,
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

    async def on_indicator_left(self, frame: Frame) -> None:
        self.indicator_left = cast(bool, frame.value)
        await self._handle_direction_state()

    async def on_indicator_right(self, frame: Frame) -> None:
        self.indicator_right = cast(bool, frame.value)
        await self._handle_direction_state()

    async def on_accelerator_pedal(self, frame: Frame) -> None:
        self.accelerator_pedal = cast(int, frame.value)
        await self.driver_can.restbus.update_signals(
            RestbusSignalConfig.set(name=SCCM.accelerator_pedal_signal, value=self.accelerator_pedal),
        )

    async def on_brake_pedal(self, frame: Frame) -> None:
        self.brake_pedal = cast(int, frame.value)
        await self.driver_can.restbus.update_signals(
            RestbusSignalConfig.set(name=SCCM.brake_pedal_signal, value=self.brake_pedal),
        )

    async def on_steering_angle(self, frame: Frame) -> None:
        self.steering_angle = cast(int, frame.value)
        await self.driver_can.restbus.update_signals(
            RestbusSignalConfig.set(name=SCCM.steering_angle_signal, value=-self.steering_angle),
        )

    async def _handle_direction_state(self) -> None:
        if self.indicator_left:
            await self.driver_can.restbus.update_signals(
                RestbusSignalConfig.set(name=SCCM.turnstalk_signal, value=1),
            )
        elif self.indicator_right:
            await self.driver_can.restbus.update_signals(
                RestbusSignalConfig.set(name=SCCM.turnstalk_signal, value=2),
            )
        else:
            await self.driver_can.restbus.update_signals(
                RestbusSignalConfig.set(name=SCCM.turnstalk_signal, value=0),
            )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting SCCM ECU", args=avp)
    async with SCCM(avp) as sccm:
        await sccm


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
