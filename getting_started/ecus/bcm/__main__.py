import asyncio
import logging
from dataclasses import dataclass

from remotivelabs.broker import BrokerClient, Frame, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig


# This dataclass defines the behavioral logic for the BCM (Body Control Module).
# It receives CAN frames and updates the state of turn signals based on input.
@dataclass
class BCM:
    body_can_0: CanNamespace

    """BCM handles incoming signals and transition lights between states"""

    async def on_hazard_light(self, frame: Frame) -> None:
        # Extract the hazard light signal value from the incoming frame.
        # This value is typically 0.0 (OFF) or 1.0 (ON).
        hazard_signal = frame.signals["HazardLightButton.HazardLightButton"]

        # Forward the same signal value to both the left and right turn lights.
        # This simulates hazard lights by activating both sides simultaneously.
        # Note: This example keeps the lights ON/OFF, not blinking.
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set("TurnLightControl.RightTurnLightRequest", value=hazard_signal),
            RestbusSignalConfig.set("TurnLightControl.LeftTurnLightRequest", value=hazard_signal),
        )


async def main(avp: BehavioralModelArgs):
    logging.info("Starting BCM simulator")

    # Create a BrokerClient instance to communicate with the RemotiveBroker
    async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
        # Define a CAN namespace and configure its restbus
        body_can_0 = CanNamespace(
            "BCM-BodyCan0",
            broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name="BCM")], delay_multiplier=avp.delay_multiplier)],
        )

        # Define a CAN namespace which will only be used to receive inputs
        driver_can_0 = CanNamespace("BCM-DriverCan0", broker_client)

        bcm = BCM(body_can_0)

        # Create a BehavioralModel which will start restbusses, handle inputs and receive control messages
        async with BehavioralModel(
            "BCM",
            namespaces=[body_can_0, driver_can_0],
            broker_client=broker_client,
            input_handlers=[
                driver_can_0.create_input_handler(
                    [filters.FrameFilter("HazardLightButton")],
                    bcm.on_hazard_light,
                )
            ],
        ) as bm:
            await bm.run_forever()


if __name__ == "__main__":
    # The command line argument parser from RemotiveLabs will pick up the settings from the generated topology
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel)
    logging.getLogger("remotivelabs.topology").setLevel(logging.DEBUG)
    asyncio.run(main(args))
