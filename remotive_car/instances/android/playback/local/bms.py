import asyncio
import os
import time
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


def _value(frame: Frame) -> float:
    # a VSS frame is a single signal, so it always carries a value
    return float(cast(float, frame.value))


@dataclass
class BMS:
    ecu_name: str = "BMS"
    vss_namespace_name: str = "BMS-VSS"
    chassis_can_namespace_name: str = "BMS-ChassisCan0"

    voltage_signal_vss: str = "Vehicle.Powertrain.TractionBattery.CurrentVoltage"
    current_signal_vss: str = "Vehicle.Powertrain.TractionBattery.CurrentCurrent"
    power_signal_vss: str = "Vehicle.Powertrain.TractionBattery.CurrentPower"
    soc_signal_vss: str = "Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed"

    voltage_signal: str = "BatteryMeasurement.BatteryVoltage"
    current_signal: str = "BatteryMeasurement.BatteryCurrent"
    power_signal: str = "BatteryStatus.BatteryPower"
    soc_signal: str = "BatteryStatus.StateOfCharge"

    # reserved value written by its DBC name; the broker encodes the raw code
    sna: str = "SNA"
    sna_signals: tuple[str, ...] = (voltage_signal, current_signal, power_signal, soc_signal)

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.chassis_can = CanNamespace(
            BMS.chassis_can_namespace_name,
            broker_client=self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=BMS.ecu_name)], delay_multiplier=avp.delay_multiplier)],
        )
        self.vss = GenericNamespace(
            BMS.vss_namespace_name,
            broker_client=self._broker_client,
        )
        self.bm = BehavioralModel(
            BMS.ecu_name,
            namespaces=[self.vss, self.chassis_can],
            broker_client=self._broker_client,
            input_handlers=[
                self.vss.create_input_handler([filters.FrameFilter(frame_name=BMS.voltage_signal_vss)], self.on_voltage),
                self.vss.create_input_handler([filters.FrameFilter(frame_name=BMS.current_signal_vss)], self.on_current),
                self.vss.create_input_handler([filters.FrameFilter(frame_name=BMS.power_signal_vss)], self.on_power),
                self.vss.create_input_handler([filters.FrameFilter(frame_name=BMS.soc_signal_vss)], self.on_soc),
            ],
        )

    @staticmethod
    def _read_input_timeout() -> float:
        raw = os.environ.get("SNA_ON_MISSING_INPUT_TIMEOUT", "").strip()
        try:
            return float(raw) if raw else 5.0
        except ValueError:
            logger.warning("Invalid SNA_ON_MISSING_INPUT_TIMEOUT, using default", value=raw, default=5.0)
            return 5.0

    async def __aenter__(self):
        await self._broker_client.connect()
        self._input_timeout_s = self._read_input_timeout()
        self._last_input = time.monotonic()
        self._sna_sent = False
        self._last_values: dict[str, float] = {}
        await self.bm.start()
        self._watchdog_task = asyncio.create_task(self._watchdog())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._watchdog_task.cancel()
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def _mark_input(self) -> None:
        self._last_input = time.monotonic()
        if self._sna_sent:
            # The VSS recording is change-based, so signals whose value did not
            # change across the gap will not be replayed: restore the last known
            # values instead of leaving them at SNA.
            logger.info("VSS input resumed, restoring last known values")
            self._sna_sent = False
            if self._last_values:
                await self.chassis_can.restbus.update_signals(
                    *[RestbusSignalConfig.set(name=name, value=value) for name, value in self._last_values.items()]
                )

    async def _watchdog(self) -> None:
        """Fall back to SNA when the VSS input goes quiet, e.g. playback stopped."""
        while True:
            remaining = self._last_input + self._input_timeout_s - time.monotonic()
            if self._sna_sent or remaining > 0:
                await asyncio.sleep(1.0 if self._sna_sent else remaining)
                continue
            logger.info("No VSS input, sending SNA", timeout_s=self._input_timeout_s)
            await self.chassis_can.restbus.update_signals(*[RestbusSignalConfig.set(name=name, value=BMS.sna) for name in BMS.sna_signals])
            self._sna_sent = True

    async def _forward(self, name: str, value: float) -> None:
        self._last_values[name] = value
        await self._mark_input()
        await self.chassis_can.restbus.update_signals(RestbusSignalConfig.set(name=name, value=value))

    async def on_voltage(self, frame: Frame) -> None:
        await self._forward(BMS.voltage_signal, _value(frame))

    async def on_current(self, frame: Frame) -> None:
        # VSS: positive = into battery (charging); DBC: positive = discharging
        await self._forward(BMS.current_signal, -_value(frame))

    async def on_power(self, frame: Frame) -> None:
        # VSS is W with positive = into battery (charging); DBC is kW with positive = discharging
        await self._forward(BMS.power_signal, -_value(frame) / 1000.0)

    async def on_soc(self, frame: Frame) -> None:
        await self._forward(BMS.soc_signal, _value(frame))


async def main(avp: BehavioralModelArgs):
    logger.info("Starting BMS ECU", args=avp)
    async with BMS(avp) as bms:
        await bms


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
