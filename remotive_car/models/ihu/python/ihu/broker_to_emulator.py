from threading import Thread

import structlog

from .libs.emulator.adb.adb_emulator import AndroidEmulator
from .libs.emulator.vhal import vhal_emulator

PERF_VEHICLE_SPEED = 0x11600207
HVAC_TEMPERATURE_SET = 0x15600503

logger = structlog.get_logger(__name__)


class BrokerToEmulator:
    def __init__(self, emulator_name: str, vhal_callback=None):
        self.emulator = AndroidEmulator(emulator_name=emulator_name)
        self.vhal = vhal_emulator.Vhal(None)
        self.vhal_callback = vhal_callback
        self._start_rx_thread()
        self.vhal.set_callback(self._on_vhal_message)

    def _start_rx_thread(self):
        """
        Start the RX thread to listen for messages from the VHAL.
        """
        rx_thread = Thread(target=self.vhal.rxThread, daemon=True)
        rx_thread.start()

    def redirect_location_signals_to_emulator(self, lon: float, lat: float):
        if lat != 0 and lon != 0:
            self.emulator.send_fix(str(lon), str(lat))

    def update_speed_property(self, speed: float):
        speed_mps = speed / 3.6
        try:
            self.vhal.set_property(PERF_VEHICLE_SPEED, 0, speed_mps)
        except Exception as e:
            print(f"Error setting property ID 0x{PERF_VEHICLE_SPEED:08x}: {e}")

    def _on_vhal_message(self, msg):
        """
        Callback triggered when a message is received from the VHAL.
        """
        if self.vhal_callback is None:
            return

        # Extract the first value from the 'value' field if it exists
        value = next(iter(getattr(msg, "value", [])), None)
        if not value or getattr(value, "prop", None) != HVAC_TEMPERATURE_SET:
            return  # Exit if no value or the property ID doesn't match

        # Extract the temperature and area_id
        area_id = getattr(value, "area_id", None)
        temperature = next(iter(getattr(value, "float_values", [])), None)
        if temperature is None:
            return

        if area_id in {1, 49}:  # Left temperature
            self.vhal_callback(
                name="CompartmentControl",
                service_instance_name="HVACService",
                parameters={"LeftTemperature": temperature},
            )
        if area_id in {4, 68}:  # Right temperature
            self.vhal_callback(
                name="CompartmentControl",
                service_instance_name="HVACService",
                parameters={"RightTemperature": temperature},
            )
