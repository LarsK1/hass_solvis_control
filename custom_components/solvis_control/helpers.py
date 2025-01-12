"""Solvis Number Sensor."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    MANUFACTURER,
    DEVICE_VERSION,
)


def generate_device_info(entry: ConfigEntry, host: str, name: str) -> DeviceInfo:
    model = {
        1: "Solvis Control 3",
        2: "Solvis Control 2",
    }.get(DEVICE_VERSION, "Solvis Control (unbekannt)")

    info = {
        "identifiers": {(DOMAIN, host)},
        "name": name,
        "manufacturer": MANUFACTURER,
        "model": model,
    }

    if "VERSIONSC" in entry.data:
        info["sw_version"] = entry.data["VERSIONSC"]
    if "VERSIONNBG" in entry.data:
        info["hw_version"] = entry.data["VERSIONNBG"]

    return DeviceInfo(**info)
