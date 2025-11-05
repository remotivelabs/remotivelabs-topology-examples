from threading import Thread

from remotivelabs.broker import SignalValue

from .libs.adb.adb_emulator import AndroidEmulator
from .libs.vhal import vhal_emulator as vhal_emu
from .libs.vhal.vhal_prop_consts_2_0 import vhal_props


class BrokerToAAOS:
    def __init__(self, android_emulator: AndroidEmulator, user_callback=None):
        # Get the emulator device via adb only once
        self.vhal = vhal_emu.Vhal(device=android_emulator.emulator_name)
        self.vhal.set_callback(self._on_vhal_message)  # Set the callback
        self._start_rx_thread()  # Start the RX thread
        self.user_callback = user_callback

    def _start_rx_thread(self):
        """
        Start the RX thread to listen for messages from the VHAL.
        """
        rx_thread = Thread(target=self.vhal.rxThread, daemon=True)
        rx_thread.start()

    def _on_vhal_message(self, msg):
        """
        Callback triggered when a message is received from the VHAL.
        """
        if self.user_callback is None:
            return

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
            self.user_callback(
                name="CompartmentControl",
                service_instance_name="HVACService",
                parameters={"LeftTemperature": temperature},
            )
        # elif area_id == 68:  # Right temperature (ROW_1_RIGHT | ROW_2_RIGHT)
        # self.user_callback(
        #     name="CompartmentControl",
        #     service_instance_name="HVACService",
        #     parameters={"RightTemperature": temperature},
        # )

    def _set_property(self, property_id, area_id, value):
        """Set a property in AAOS via VHAL"""
        try:
            self.vhal.set_property(property_id, area_id, value)
            # print(f"Property set: ID=0x{property_id:08x}, Area=0x{area_id:08x}, Value={value}")
        except Exception as e:
            print(f"Error setting property ID 0x{property_id:08x}: {e}")

    def update_speed_property(self, signals: dict[str, SignalValue]):
        speed = float(signals.get("Speed", 0))  # Extract speed from the event
        speed_mps = speed / 3.6
        self._set_property(vhal_props.PERF_VEHICLE_SPEED, 0, speed_mps)
