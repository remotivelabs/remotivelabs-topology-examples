import structlog

from .libs.cuttlefish.gnss.gnss_client import GnssClient
from .libs.cuttlefish.vhal.vhal_client import VhalClient

PERF_VEHICLE_SPEED = 0x11600207
HVAC_TEMPERATURE_SET = 0x15600503
GEAR_SELECTION = 0x11400400

logger = structlog.get_logger(__name__)


class BrokerToCuttlefish:
    def __init__(self, cuttlefish_gnss_url: str, cuttlefish_vhal_url: str, vhal_callback=None):
        self.gnss = GnssClient(cuttlefish_gnss_url)
        self.vhal = VhalClient(
            cuttlefish_vhal_url=cuttlefish_vhal_url,
            on_vhal_prop_change=self._on_vhal_prop_change,
            property_ids_to_subscribe=[HVAC_TEMPERATURE_SET],
        )
        self.vhal_callback = vhal_callback
        self.speed_mps = 0.0

    def redirect_location_signals_to_cuttlefish(self, lon: float, lat: float, heading: float):
        if lat != 0 and lon != 0:
            self.gnss.send_gps(longitude=lon, latitude=lat, bearing=heading, speed_mps=self.speed_mps)

    def update_speed_property(self, speed: float):
        self.speed_mps = speed / 3.6
        try:
            self.vhal.set_property(0, PERF_VEHICLE_SPEED, self.speed_mps)
        except Exception as e:
            logger.info(f"Error setting property ID 0x{PERF_VEHICLE_SPEED:08x}: {e}")

    def update_gear_property(self, gear: int):
        # gear: 0 = Reverse, 1 = Drive (from bodycan.dbc)
        # VHAL GEAR_SELECTION: 1 = Park, 2 = Reverse, 4 = Neutral, 8 = Drive
        vhal_gear = 8 if gear == 1 else 2  # Map 1->Drive(8), 0->Reverse(2)
        try:
            self.vhal.set_property(0, GEAR_SELECTION, vhal_gear)
        except Exception as e:
            logger.info(f"Error setting property ID 0x{GEAR_SELECTION:08x}: {e}")

    def _on_vhal_prop_change(self, area_id, property_id, value):
        logger.info(f"area_id:{area_id} - property_id:{property_id} - value:{value}")
        if self.vhal_callback is None:
            return

        if property_id != HVAC_TEMPERATURE_SET:
            return  # Exit if no value or the property ID doesn't match

        if value is None:
            return

        if area_id == 1:  # Left temperature
            self.vhal_callback(
                name="CompartmentControl",
                service_instance_name="HVACService",
                parameters={"LeftTemperature": value},
            )
        if area_id == 4:  # Right temperature
            self.vhal_callback(
                name="CompartmentControl",
                service_instance_name="HVACService",
                parameters={"RightTemperature": value},
            )
