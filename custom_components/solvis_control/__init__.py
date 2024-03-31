"""
Modul to integrate solvis heaters to.

Version: 0.1.1-alpha
"""
"""Solvis integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
)
from .coordinator import SolvisModbusCoordinator

PLATFORMS: [Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solvis device from a config entry."""

    address = entry.data.get(CONF_IP_ADDRESS)

    if address is None:
        return False
    
    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    # Create coordinator for polling
    coordinator = SolvisModbusCoordinator(hass, address)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_COORDINATOR, coordinator)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
