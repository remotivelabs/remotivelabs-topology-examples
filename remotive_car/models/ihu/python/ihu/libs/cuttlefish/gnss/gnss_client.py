import json
import time

import requests
import urllib3


class GnssClient:
    def __init__(self, cuttlefish_url: str):
        urllib3.disable_warnings()  # Cuttlefish runs the grpc proxy over https using a self-signed certificate
        self.cuttlefish_url = cuttlefish_url

    def send_gps(self, longitude: float, latitude: float, speed_mps: float = 0.0, bearing: float = 0.0):
        elevation = 15
        accuracy_meters = 3
        speed_accuracy = 0.5
        bearing_accuracy = 1.0
        current_millis = round(time.time() * 1000)

        payload = {
            "gps": (
                f"Fix,GPS,{latitude},{longitude},{elevation},{speed_mps},"
                f"{accuracy_meters},{bearing},{current_millis},{speed_accuracy},"
                f"{bearing_accuracy},1"
            )
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.cuttlefish_url + "/services/GnssGrpcProxy/SendGps",
                headers=headers,
                data=json.dumps(payload),
                verify=False,  # Only use this in dev/testing
                timeout=10,  # Set a timeout of 10 seconds
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send location: {e}")
