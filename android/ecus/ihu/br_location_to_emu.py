from remotivelabs.broker import SignalValue

from .libs.adb.adb_emulator import AndroidEmulator


class BrokerToEmu:
    def __init__(self, emulator: AndroidEmulator):
        self.emulator = emulator

    def redirect_location_signals_to_emulator(self, signals: dict[str, SignalValue]):
        # Extract latitude and longitude from the signals dict
        lon = float(signals.get("Longitude", 0))
        lat = float(signals.get("Latitude", 0))
        if lat is not None and lon is not None:
            self.emulator.send_fix(str(lon), str(lat))
