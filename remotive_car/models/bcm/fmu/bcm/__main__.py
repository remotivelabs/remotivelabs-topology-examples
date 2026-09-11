from __future__ import annotations

import asyncio
from pathlib import Path

import structlog
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.fmu.behavioral_model import FMUBehavioralModel
from remotivelabs.topology.fmu.simulation import FMUSimulation, FMUVars
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig

from .log import configure_logging

logger = structlog.get_logger(__name__)

# ECU configuration. Must match values in interfaces.json.
ECU_NAME = "BCM"
SRC_NAMESPACE = "BCM-DriverCan0"
TARGET_NAMESPACE = "BCM-BodyCan0"

FMU_PATH = Path(__file__).parent / "model" / "BCM.fmu"

# Incoming DriverCan frames and signals, mapped to the FMU input variables they feed.
INPUT_MAPPING = {
    SRC_NAMESPACE: {
        "HazardLightButton": {"HazardLightButton.HazardLightButton": "hazard_button"},
        "TurnStalk": {"TurnStalk.TurnSignal": "turn_stalk"},
        "LightStalk": {
            "LightStalk.LightMode": "light_stalk_mode",
            "LightStalk.HighBeam": "light_stalk_high_beam",
        },
        "BrakePedalPositionSensor": {"BrakePedalPositionSensor.BrakePedalPosition": "brake_pedal_position"},
        "AcceleratorPedalPositionSensor": {"AcceleratorPedalPositionSensor.AcceleratorPedalPosition": "accelerator_pedal_position"},
        "GearShiftPaddles": {
            "GearShiftPaddles.GearShiftUp": "shift_up_button",
            "GearShiftPaddles.GearShiftDown": "shift_down_button",
        },
        "SteeringAngle": {"SteeringAngle.SteeringAngle": "steering_wheel"},
    }
}

# FMU output variables, mapped to the BodyCan signals they drive. All of them are
# integral (a light that is on or off, a raw pedal position, a gear) ...
INT_OUTPUT_MAPPING = {
    "left_turn_light": "TurnLightControl.LeftTurnLightRequest",
    "right_turn_light": "TurnLightControl.RightTurnLightRequest",
    "left_daylight_light": "DaylightRunningLightControl.LeftDaylightRunningLightRequest",
    "right_daylight_light": "DaylightRunningLightControl.RightDaylightRunningLightRequest",
    "left_lowbeam": "LowBeamLightControl.LeftLowBeamLightRequest",
    "right_lowbeam": "LowBeamLightControl.RightLowBeamLightRequest",
    "left_highbeam": "HighBeamLightControl.LeftHighBeamLightRequest",
    "right_highbeam": "HighBeamLightControl.RightHighBeamLightRequest",
    "left_brake_light": "BrakeLightControl.LeftBrakeLightRequest",
    "right_brake_light": "BrakeLightControl.RightBrakeLightRequest",
    "accelerator_pedal_angle": "AcceleratorPedalInfo.AcceleratorPedalPosition",
    "gear_info": "GearInfo.GearLeverPosition",
}

# ... except the steering wheel angle, which is a physical value in degrees.
FLOAT_OUTPUT_MAPPING = {
    "steering_wheel_info": "SteeringWheelInfo.SteeringWheelPosition",
}


async def main(avp: BehavioralModelArgs) -> None:
    logger.info("Starting BCM ECU", args=avp)

    async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
        body_can = CanNamespace(
            TARGET_NAMESPACE,
            broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=ECU_NAME)], delay_multiplier=avp.delay_multiplier)],
        )
        driver_can = CanNamespace(SRC_NAMESPACE, broker_client)

        async def on_output(output: FMUVars) -> None:
            """Publish the outputs of every FMU step on the BodyCan restbus."""
            await body_can.restbus.update_signals(
                *(RestbusSignalConfig.set(name=signal, value=int(output[var])) for var, signal in INT_OUTPUT_MAPPING.items()),
                *(RestbusSignalConfig.set(name=signal, value=float(output[var])) for var, signal in FLOAT_OUTPUT_MAPPING.items()),
            )

        fmu = FMUSimulation(FMU_PATH, on_output=on_output)

        async with FMUBehavioralModel(
            ECU_NAME,
            namespaces=[driver_can, body_can],
            broker_client=broker_client,
            fmu=fmu,
            input_mapping=INPUT_MAPPING,
        ) as bm:
            await bm.run_forever()


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(level=args.loglevel)
    asyncio.run(main(args))
