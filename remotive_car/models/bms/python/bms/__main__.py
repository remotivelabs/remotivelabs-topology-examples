from __future__ import annotations

import asyncio
import math
import os
import time
from typing import cast

import structlog
from remotivelabs.broker import BrokerClient, Frame
from remotivelabs.topology.behavioral_model import BehavioralModel, RebootRequest
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.control import ControlRequest, ControlResponse
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig

from .log import configure_logging

logger = structlog.get_logger(__name__)


class BatteryPack:
    """Simple high-voltage battery pack model.

    StateOfCharge is estimated by coulomb counting: no sensor measures SOC,
    the BMS integrates the current it draws against the pack capacity.
    Terminal voltage is the open-circuit voltage minus the drop over the
    internal resistance, so it sags under load and rises during regen.
    """

    capacity_kwh: float = 75.0
    ocv_empty_v: float = 330.0  # open-circuit voltage at 0 % SOC
    ocv_full_v: float = 420.0  # open-circuit voltage at 100 % SOC
    internal_resistance_ohm: float = 0.05

    def __init__(self, soc: float) -> None:
        self.soc = soc

    def open_circuit_voltage(self) -> float:
        return self.ocv_empty_v + (self.ocv_full_v - self.ocv_empty_v) * self.soc / 100.0

    def step(self, power_w: float, dt_s: float) -> tuple[float, float]:
        """Draw power_w (negative = charge) for dt_s. Returns (voltage, current)."""
        if self.soc <= 0.0:
            power_w = min(power_w, 0.0)  # empty pack cannot deliver
        if self.soc >= 100.0:
            power_w = max(power_w, 0.0)  # full pack cannot absorb regen
        ocv = self.open_circuit_voltage()
        current = power_w / ocv
        voltage = ocv - current * self.internal_resistance_ohm
        current = power_w / voltage
        drawn_wh = power_w * dt_s / 3600.0
        self.soc = min(100.0, max(0.0, self.soc - drawn_wh / (self.capacity_kwh * 1000.0) * 100.0))
        return voltage, current


class BMS:
    ecu_name: str = "BMS"
    chassis_ns: str = "BMS-ChassisCan0"

    motor_info_frame: str = "MotorInfo"
    motor_speed_signal: str = "MotorInfo.MotorSpeed"
    motor_torque_signal: str = "MotorInfo.MotorTorque"

    voltage_signal: str = "BatteryMeasurement.BatteryVoltage"
    current_signal: str = "BatteryMeasurement.BatteryCurrent"
    soc_signal: str = "BatteryStatus.StateOfCharge"
    power_signal: str = "BatteryStatus.BatteryPower"

    # reserved values are written by their DBC names; the broker encodes the raw code
    error: str = "Error"
    sna: str = "SNA"

    aux_load_w: float = 300.0  # 12V system, computers, ...
    drivetrain_efficiency: float = 0.9
    tick_s: float = 0.1

    initial_soc_env: str = "INITIAL_STATE_OF_CHARGE"
    input_timeout_env: str = "SNA_ON_MISSING_INPUT_TIMEOUT"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)
        self.chassis_can_0 = CanNamespace(
            BMS.chassis_ns,
            self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=BMS.ecu_name)], delay_multiplier=avp.delay_multiplier)],
            decode_named_values=True,  # Error/SNA arrive as their names, not as raw codes
        )
        self.bm = BehavioralModel(
            BMS.ecu_name,
            namespaces=[self.chassis_can_0],
            broker_client=self._broker_client,
            input_handlers=[
                self.chassis_can_0.create_input_handler([filters.FrameFilter(BMS.motor_info_frame)], self.on_motor_info),
            ],
            control_handlers=[
                (RebootRequest.type, self.on_reboot),
                ("set_batterystatus_stateofcharge", self.on_set_soc),
            ],
            # MotorInfo doubles as the liveness signal for the input timeout, so every transmission
            # must be delivered, not only those where a value changed.
            on_change=False,
        )
        # Until the BMS knows its state of charge (INITIAL_STATE_OF_CHARGE env
        # or a set_batterystatus_stateofcharge control message) it reports SNA;
        # if it receives motor data it should compute from but has no state of
        # charge (missing or invalid default), it reports Error instead.
        self.pack: BatteryPack | None = None
        self._default_soc, self._default_soc_invalid = self._read_default_soc()
        self._input_timeout_s = self._read_input_timeout()
        self._has_motor_data = False
        self._motor_power_w = 0.0
        self._last_motor_input = time.monotonic()
        self._input_missing = False
        self._tick_task: asyncio.Task[None] | None = None

    @staticmethod
    def _read_input_timeout() -> float:
        raw = os.environ.get(BMS.input_timeout_env, "").strip()
        try:
            return float(raw) if raw else 5.0
        except ValueError:
            logger.warning("Invalid SNA_ON_MISSING_INPUT_TIMEOUT, using default", value=raw, default=5.0)
            return 5.0

    @staticmethod
    def _read_default_soc() -> tuple[float | None, bool]:
        raw = os.environ.get(BMS.initial_soc_env, "").strip()
        if not raw:
            return None, False
        try:
            soc = float(raw)
        except ValueError:
            return None, True
        if not 0.0 <= soc <= 100.0:
            return None, True
        return soc, False

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        self._tick_task = asyncio.create_task(self._tick_forever())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._tick_task is not None:
            self._tick_task.cancel()
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def on_reboot(self, request: ControlRequest) -> ControlResponse:  # noqa: ARG002
        logger.info("Rebooting BMS")
        self.pack = None
        self._has_motor_data = False
        self._motor_power_w = 0.0
        self._last_motor_input = time.monotonic()
        self._input_missing = False
        await self.chassis_can_0.restbus.reset()
        return ControlResponse(status="ok")

    async def on_set_soc(self, request: ControlRequest) -> ControlResponse:
        try:
            soc = float(str(request.argument))
        except (TypeError, ValueError):
            return ControlResponse(status="error", data="set_batterystatus_stateofcharge requires a numeric argument in 0..100")
        if not 0.0 <= soc <= 100.0:
            return ControlResponse(status="error", data="set_batterystatus_stateofcharge requires a numeric argument in 0..100")
        self.pack = BatteryPack(soc=soc)
        return ControlResponse(status="ok")

    async def on_motor_info(self, frame: Frame) -> None:
        """Derive electrical power demand from the drive unit's torque and speed."""
        speed_rpm = frame.signals[BMS.motor_speed_signal]
        torque_nm = frame.signals[BMS.motor_torque_signal]
        self._last_motor_input = time.monotonic()
        if self._input_missing:
            logger.info("MotorInfo input resumed")
            self._input_missing = False
        if isinstance(speed_rpm, str) or isinstance(torque_nm, str):
            # a named value (Error/SNA), e.g. a PCM that has no reading yet: nothing to compute from
            self._motor_power_w = 0.0
            return
        self._has_motor_data = True
        mechanical_w = cast(float, torque_nm) * cast(float, speed_rpm) * 2.0 * math.pi / 60.0
        if mechanical_w >= 0:
            self._motor_power_w = mechanical_w / BMS.drivetrain_efficiency
        else:
            self._motor_power_w = mechanical_w * BMS.drivetrain_efficiency

    async def _tick_forever(self) -> None:
        while True:
            await asyncio.sleep(BMS.tick_s)
            try:
                await self._tick()
            except Exception:
                logger.exception("tick failed")

    async def _tick(self) -> None:
        if self._default_soc_invalid:
            # misconfigured INITIAL_STATE_OF_CHARGE: the BMS knows it is broken
            await self._send_error()
            return
        if self.pack is None:
            if self._has_motor_data and self._default_soc is not None:
                # calculation can begin: motor data arrived and we have a valid default
                self.pack = BatteryPack(soc=self._default_soc)
            elif self._has_motor_data:
                # motor data to compute from, but no state of charge to start from
                await self._send_error()
                return
            else:
                await self._send_sna()
                return
        if time.monotonic() - self._last_motor_input > self._input_timeout_s:
            # MotorInfo frames stopped arriving (bus/PCM failure): the demand is
            # unknown, so the derived values are SNA. StateOfCharge is the BMS's
            # own state and stays valid, but frozen: integration is paused.
            if not self._input_missing:
                logger.info("No MotorInfo input, sending SNA for derived values", timeout_s=self._input_timeout_s)
                self._input_missing = True
            await self._send_sna(soc=round(self.pack.soc, 1))
            return
        power_w = self._motor_power_w + BMS.aux_load_w
        voltage, current = self.pack.step(power_w, BMS.tick_s)
        await self._send_all(round(voltage, 2), round(current, 1), round(self.pack.soc, 1), round(power_w / 1000.0, 1))

    async def _send_error(self) -> None:
        await self._send_all(BMS.error, BMS.error, BMS.error, BMS.error)

    async def _send_sna(self, soc: float | None = None) -> None:
        """Derived values are SNA; StateOfCharge too, unless the BMS knows it."""
        await self._send_all(BMS.sna, BMS.sna, BMS.sna if soc is None else soc, BMS.sna)

    async def _send_all(self, voltage: float | str, current: float | str, soc: float | str, power_kw: float | str) -> None:
        await self.chassis_can_0.restbus.update_signals(
            (BMS.voltage_signal, voltage),
            (BMS.current_signal, current),
            (BMS.soc_signal, soc),
            (BMS.power_signal, power_kw),
        )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting BMS ECU", args=avp)
    async with BMS(avp) as bms:
        await bms


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
