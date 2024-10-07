"""
Modul to integrate solvis heaters to.

Version: 1.0.1-release
"""

"""Solvis integration."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_PORT,
    DATA_COORDINATOR,
    DOMAIN,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
)
from .coordinator import SolvisModbusCoordinator

PLATFORMS: [Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solvis device from a config entry."""

    conf_host = entry.data.get(CONF_HOST)
    conf_port = entry.data.get(CONF_PORT)

    if conf_host is None or conf_port is None:
        return False

    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    # Create coordinator for polling
    coordinator = SolvisModbusCoordinator(
        hass,
        conf_host,
        conf_port,
        CONF_OPTION_1,
        CONF_OPTION_2,
        CONF_OPTION_3,
        CONF_OPTION_4,
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_COORDINATOR, coordinator)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
