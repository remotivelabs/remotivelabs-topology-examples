import structlog

from .libs.cuttlefish.gnss.gnss_client import GnssClient
from .libs.cuttlefish.vhal.vhal_client import VhalClient

PERF_VEHICLE_SPEED = 0x11600207
HVAC_TEMPERATURE_SET = 0x15600503

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

    def redirect_location_signals_to_cuttlefish(self, lon: float, lat: float):
        if lat != 0 and lon != 0:
            self.gnss.send_gps_vector(longitude=lon, latitude=lat)

    def update_speed_property(self, speed: float):
        speed_mps = speed / 3.6
        try:
            self.vhal.set_property(0, PERF_VEHICLE_SPEED, speed_mps)
        except Exception as e:
            logger.info(f"Error setting property ID 0x{PERF_VEHICLE_SPEED:08x}: {e}")

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
