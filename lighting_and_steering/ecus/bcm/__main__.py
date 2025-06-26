from __future__ import annotations

import asyncio
from enum import Enum
from typing import cast

import structlog
from remotivelabs.broker import BrokerClient, Frame, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel, RebootRequest
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.control import (
    ControlRequest,
    ControlResponse,
)
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig

from .log import configure_logging
from .state_machines.beams import BeamsStateMachine, LightModePosition
from .state_machines.turn_signals import TurnSignalsStateMachine, TurnStalkPosition

logger = structlog.get_logger(__name__)

# Predefined signal values for daylight running lights, low beams and high beams
BEAMS_OUTPUT_FOR_STATE = {
    "off": {"daylight_running_lights": 0, "low_beams": 0},
    "drl": {"daylight_running_lights": 1, "low_beams": 0},
    "low": {"daylight_running_lights": 1, "low_beams": 1},
}

# Predefined signal values for turn signals
TURN_SIGNAL_OUTPUT_PER_STATE = {
    "left_on": {"left": 1, "right": 0},
    "left_off": {"left": 0, "right": 0},
    "right_on": {"left": 0, "right": 1},
    "right_off": {"left": 0, "right": 0},
    "hazard_on": {"left": 1, "right": 1},
    "hazard_off": {"left": 0, "right": 0},
    "off": {"left": 0, "right": 0},
}


class OperatingMode(str, Enum):
    NORMAL = "normal"
    EMERGENCY = "emergency"


class BCM:
    """
    BCM (Body Control Module) handles incoming signals from the DriverCan bus and, using the state machines, determines what output signals
    to send on the BodyCan bus.

    Note that some of the signals that the BCM produce are blinking signals, i.e. the signals are toggled on and off at a fixed interval.
    """

    # ECU configuration. Must match values in interfaces.json.
    ecu_name: str = "BCM"
    src_namespace: str = "BCM-DriverCan0"
    target_namespace: str = "BCM-BodyCan0"
    virt_interface_name: str = "virt"

    # Signals on source namespace (DriverCan) we're interested in. Must match values in the signal database
    turn_stalk_frame: str = "TurnStalk"
    hazard_button_frame: str = "HazardLightButton"
    light_stalk_frame: str = "LightStalk"
    brake_pedal_position_frame: str = "BrakePedalPositionSensor"
    steering_angle_frame: str = "SteeringAngle"

    # Signals on target namespace (BodyCan) we want to send. Must match values in the signal database
    left_turn_light_signal: str = "TurnLightControl.LeftTurnLightRequest"
    right_turn_light_signal: str = "TurnLightControl.RightTurnLightRequest"
    left_brake_light_signal: str = "BrakeLightControl.LeftBrakeLightRequest"
    right_brake_light_signal: str = "BrakeLightControl.RightBrakeLightRequest"
    left_daylight_running_light_signal: str = "DaylightRunningLightControl.LeftDaylightRunningLightRequest"
    right_daylight_running_light_signal: str = "DaylightRunningLightControl.RightDaylightRunningLightRequest"
    left_low_beam_signal: str = "LowBeamLightControl.LeftLowBeamLightRequest"
    right_low_beam_signal: str = "LowBeamLightControl.RightLowBeamLightRequest"
    left_high_beam_signal: str = "HighBeamLightControl.LeftHighBeamLightRequest"
    right_high_beam_signal: str = "HighBeamLightControl.RightHighBeamLightRequest"
    steering_wheel_position_signal: str = "SteeringWheelInfo.SteeringWheelPosition"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)
        self.body_can_0 = CanNamespace(
            BCM.target_namespace,
            self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=BCM.ecu_name)], delay_multiplier=avp.delay_multiplier)],
        )

        self.driver_can_0 = CanNamespace(BCM.src_namespace, self._broker_client)

        self.bm = BehavioralModel(
            BCM.ecu_name,
            namespaces=[self.body_can_0, self.driver_can_0],
            broker_client=self._broker_client,
            input_handlers=[
                self.driver_can_0.create_input_handler([filters.FrameFilter(BCM.turn_stalk_frame)], self.on_turn_stalk),
                self.driver_can_0.create_input_handler([filters.FrameFilter(BCM.hazard_button_frame)], self.on_hazard_button),
                self.driver_can_0.create_input_handler([filters.FrameFilter(BCM.light_stalk_frame)], self.on_light_mode),
                self.driver_can_0.create_input_handler([filters.FrameFilter(BCM.light_stalk_frame)], self.on_high_beam),
                self.driver_can_0.create_input_handler([filters.FrameFilter(BCM.brake_pedal_position_frame)], self.on_brake),
                self.driver_can_0.create_input_handler([filters.FrameFilter(BCM.steering_angle_frame)], self.on_steering_angle),
            ],
            control_handlers=[
                ("emergency_mode", self.on_set_emergency_mode),
                # override built-in RebootRequest so that we can reset the state machine(s) as well
                (RebootRequest.type, self.on_reboot),
            ],
        )
        self.beams_machine = BeamsStateMachine()
        self.beams_output_for_state = BEAMS_OUTPUT_FOR_STATE

        self.turn_signals_machine = TurnSignalsStateMachine(callback=self._on_toggle_turn_signals)
        self.turn_signal_output_per_state = TURN_SIGNAL_OUTPUT_PER_STATE

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.turn_signals_machine.close()
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def on_reboot(self, request: ControlRequest) -> ControlResponse:  # noqa: ARG002
        logger.info("Rebooting BCM")
        self.turn_signals_machine.reset()
        self.beams_machine.reset()
        await self.reset_restbus()
        return ControlResponse(status="ok")

    async def reset_restbus(self) -> None:
        await self.body_can_0.restbus.reset()

    async def on_light_mode(self, frame: Frame) -> None:
        """Handle light mode position change"""
        signal = frame.signals["LightStalk.LightMode"]
        light_mode = LightModePosition.OFF
        if signal == 1:
            light_mode = LightModePosition.DRL
        elif signal == 2:
            light_mode = LightModePosition.LOW
        new_state = self.beams_machine.set_light_mode_position(light_mode)
        await self._set_lights(state=new_state)

    async def on_high_beam(self, frame: Frame) -> None:
        """Handle high beam button press"""
        signal = cast(int, frame.signals["LightStalk.HighBeam"])
        high_beams = 1 if signal > 0 else 0
        logger.debug("Setting high beams", high_beams=high_beams)
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set(name=BCM.left_high_beam_signal, value=high_beams),
            RestbusSignalConfig.set(name=BCM.right_high_beam_signal, value=high_beams),
        )

    async def on_turn_stalk(self, frame: Frame) -> None:
        """Handle turn stalk position change"""
        signal = frame.signals["TurnStalk.TurnSignal"]
        movement = TurnStalkPosition.OFF
        if signal == 1:
            movement = TurnStalkPosition.LEFT
        elif signal == 2:
            movement = TurnStalkPosition.RIGHT
        logger.debug("Incoming turn stalk signal", movement=movement)
        new_state = self.turn_signals_machine.set_turn_stalk_position(movement)
        await self._set_turn_lights(state=new_state)

    async def on_set_emergency_mode(self, request: ControlRequest) -> ControlResponse:
        try:
            mode = OperatingMode(request.argument)
        except ValueError:
            logger.warning(f"Ignoring invalid operating mode request: '{request.type}'. Allowed modes: {[m.value for m in OperatingMode]}")
            return ControlResponse(status="invalid_operating_mode")

        if mode == OperatingMode.NORMAL:
            if self.turn_signals_machine.is_hazard_enabled():
                logger.info("Received normal operation mode request")
                new_state = self.turn_signals_machine.set_hazard_button_pressed()
                await self._set_turn_lights(state=new_state)

        elif mode == OperatingMode.EMERGENCY:
            logger.info("Recieved emergency operation mode request")
            new_state = self.turn_signals_machine.set_emergency_mode()
            await self._set_turn_lights(state=new_state)

        return ControlResponse(status="ok")

    async def on_hazard_button(self, frame: Frame) -> None:
        """
        Incoming hazard button signal.

        Only update the state if the button is pressed. It needs to be clicked a second time to turn off the hazard lights.
        """
        signal = frame.signals["HazardLightButton.HazardLightButton"]
        logger.debug("Incoming hazard button signal", payload=signal)
        if signal:  # if signal is non zero (truthy), the button is clicked.
            new_state = self.turn_signals_machine.set_hazard_button_pressed()
            await self._set_turn_lights(state=new_state)

    async def _on_toggle_turn_signals(self, state: str) -> None:
        """Handle turn signal toggle"""
        await self._set_turn_lights(state=state)

    async def on_brake(self, frame: Frame) -> None:
        """Handle brake pedal position change (simple remap to brake lights signals)"""
        signal = cast(int, frame.signals["BrakePedalPositionSensor.BrakePedalPosition"])
        brake_light = 1 if signal > 0 else 0
        logger.debug("Setting brake lights", brake_light=brake_light)
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set(name=BCM.left_brake_light_signal, value=brake_light),
            RestbusSignalConfig.set(name=BCM.right_brake_light_signal, value=brake_light),
        )

    async def on_steering_angle(self, frame: Frame) -> None:
        """Handle steering angle change (simple remap to steering wheel position signal)"""
        steering_angle = frame.signals["SteeringAngle.SteeringAngle"]
        logger.debug("Setting steering wheel position", steering_angle=steering_angle)
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set(name=BCM.steering_wheel_position_signal, value=steering_angle),
        )

    async def _set_lights(self, state: str) -> None:
        default_config = self.beams_output_for_state["off"]
        beam_config = self.beams_output_for_state.get(state, default_config)

        logger.debug("Setting lights", state=state, beam_config=beam_config)
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set(name=BCM.left_daylight_running_light_signal, value=beam_config["daylight_running_lights"]),
            RestbusSignalConfig.set(name=BCM.right_daylight_running_light_signal, value=beam_config["daylight_running_lights"]),
            RestbusSignalConfig.set(name=BCM.left_low_beam_signal, value=beam_config["low_beams"]),
            RestbusSignalConfig.set(name=BCM.right_low_beam_signal, value=beam_config["low_beams"]),
        )

    async def _set_turn_lights(self, state: str) -> None:
        default_config = self.turn_signal_output_per_state["off"]
        signal_config = self.turn_signal_output_per_state.get(state, default_config)

        logger.debug("Setting turn signals", state=state, signal_config=signal_config)
        await self.body_can_0.restbus.update_signals(
            RestbusSignalConfig.set(name=BCM.left_turn_light_signal, value=signal_config["left"]),
            RestbusSignalConfig.set(name=BCM.right_turn_light_signal, value=signal_config["right"]),
        )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting BCM ECU", args=avp)
    async with BCM(avp) as bcm:
        await bcm


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(level=args.loglevel)
    asyncio.run(main(args))
