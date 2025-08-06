from .libs.adb import device as adb
import socket
# from .libs.remotive.subscribe import parsing_to_subscribe, subscribe
import os

class brokerToEmu:
    def __init__(self, adb_dev):

        def get_emulator_socket(host="host.docker.internal", port=5554):
            auth_cmd = f"auth {os.environ.get('ANDROID_EMULATOR_AUTH', '')}"
            if os.environ.get('ANDROID_EMULATOR_AUTH') is None:
                raise RuntimeError("Environment variable ANDROID_EMULATOR_AUTH is not set or empty.")
            s = socket.create_connection((host, port))
            response = s.recv(2024)
            s.sendall(auth_cmd.encode('ascii') + b"\n")
            response = s.recv(2024)
            if response != b'OK\r\n':
                print(f"Inital emu socket response: {response}, command was: {auth_cmd}")
            return s

        # Get emulator via adb only once
        adb_dev.root()
        self.adb_dev = adb_dev
        # self.args_url, self.args_api_key, _cvd, self.signals = parsing_to_subscribe()
        # self.signal_name_latitude = self.signals[0][1]
        # self.signal_name_longitude = self.signals[1][1]
        self.lon = None
        self.lat = None
        # self.session = get_emulator_socket()

    def redirect_location_to_emulator_signals(self, signals: dict[str, float]):
        # print("Received signals:", signals)
        # Extract latitude and longitude from the signals dict
        lat = signals.get("LocationFrame.Latitude")
        lon = signals.get("LocationFrame.Longitude")
        if lat is not None and lon is not None:
            self.lat = lat
            self.lon = lon
            geofix_command = f"geo fix {self.lon} {self.lat}"
            self.session.sendall(geofix_command.encode('ascii') + b"\n")
            response = self.session.recv(2024)
            if response != b'OK\r\n':
                print(f"Unexpected emu socket response: {response}, command was: {geofix_command}")

    def redirect_location_to_emulator_signals(self, signals: dict[str, float]):
        # print("Received signals:", signals)
        # Extract latitude and longitude from the signals dict
        lat = signals.get("LocationFrame.Latitude")
        lon = signals.get("LocationFrame.Longitude")
        if lat is not None and lon is not None:
            self.lat = lat
            self.lon = lon
            # self.adb_dev.root()
            self.adb_dev.send_fix(str(self.lon), str(self.lat))

    def redirect_location_to_emulator(self, signals):
        for signal in signals:
            print(
                "{} {} {} ".format(
                    signal.id.name, signal.id.namespace.name, signal.double
                )
            )
            if signal.id.name == self.signal_name_latitude:
                self.lat = signal.double
            elif signal.id.name == self.signal_name_longitude:
                self.lon = signal.double

            if self.lat is not None and self.lon is not None:
                # self.adb_dev.root()
                self.adb_dev.send_fix(str(self.lon), str(self.lat))


    # def update_emu_location(self):
    #     subscribe(self.args_url, self.args_api_key, self.signals, on_subscribe=self.redirect_location_to_emulator, on_change=True)


if __name__ == "__main__":
    adb_device = adb.get_emulator_device()
    br_emu = brokerToEmu(adb_device)

    br_emu.update_emu_location()
