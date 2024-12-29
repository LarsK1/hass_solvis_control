"""Diagnostics support for Solvis Device."""

from .const import DOMAIN
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    return {
        "entry_data": entry.data,
        "data": entry.runtime_data.data,
    }


# async def async_get_device_diagnostics(hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry) -> dict[str, Any]:
#     """Return diagnostics for a device."""
#     appliance = _get_appliance_by_device_id(hass, device.id)
#     return {
#         "details": appliance.raw_data,
#         "data": appliance.data,
#     }
