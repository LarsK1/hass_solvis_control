"""
Modul to integrate solvis heaters to.

Version: 1.2.0-alpha6
"""

"""Solvis integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_PORT,
    DATA_COORDINATOR,
    DOMAIN,
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    POLL_RATE_SLOW,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
)
from .coordinator import SolvisModbusCoordinator

PLATFORMS: [Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solvis device from a config entry."""

    if not await async_migrate_entry(hass, entry):
        return False

    conf_host = entry.data.get(CONF_HOST)
    conf_port = entry.data.get(CONF_PORT)

    if conf_host is None or conf_port is None:
        return False

    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    hass_data = dict(entry.data)
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Create coordinator for polling
    coordinator = SolvisModbusCoordinator(
        hass,
        conf_host,
        conf_port,
        entry.data.get(DEVICE_VERSION),
        entry.data.get(CONF_OPTION_1),
        entry.data.get(CONF_OPTION_2),
        entry.data.get(CONF_OPTION_3),
        entry.data.get(CONF_OPTION_4),
        entry.data.get(CONF_OPTION_5),
        entry.data.get(CONF_OPTION_6),
        entry.data.get(CONF_OPTION_7),
        entry.data.get(POLL_RATE_DEFAULT),
        entry.data.get(POLL_RATE_SLOW),
        entry.data.get(POLL_RATE_HIGH),
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


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    # Unload the existing platforms
    await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    # Reload the platforms to reflect the updated configuration
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Refresh the coordinator to get the latest data
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )
    current_version = config_entry.version
    current_minor_version = config_entry.minor_version

    new_data = {**config_entry.data}
    if current_version == 1 and current_minor_version < 3:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_OPTION_1 not in new_data:
            new_data[CONF_OPTION_1] = False
        if CONF_OPTION_2 not in new_data:
            new_data[CONF_OPTION_2] = False
        if CONF_OPTION_3 not in new_data:
            new_data[CONF_OPTION_3] = False
        if CONF_OPTION_4 not in new_data:
            new_data[CONF_OPTION_4] = False
        if DEVICE_VERSION not in new_data:
            new_data[DEVICE_VERSION] = "SC3"
        current_minor_version = 3
    if current_version == 1 and current_minor_version < 4:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if POLL_RATE_DEFAULT not in new_data:
            new_data[POLL_RATE_DEFAULT] = 30
        if POLL_RATE_SLOW not in new_data:
            new_data[POLL_RATE_SLOW] = 300
        current_minor_version = 4
    if current_version == 1 and current_minor_version == 4:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        current_minor_version = 0
        current_version = 2
    if current_version == 2 and current_minor_version == 0:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        current_minor_version = 1
        if not CONF_OPTION_5 in new_data:
            new_data[CONF_OPTION_5] = False
    if current_version == 2 and current_minor_version == 1:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        current_minor_version = 2
        if not CONF_OPTION_6 in new_data:
            new_data[CONF_OPTION_6] = True
        if not CONF_OPTION_7 in new_data:
            new_data[CONF_OPTION_7] = False
        if not POLL_RATE_HIGH in new_data:
            new_data[POLL_RATE_HIGH] = 10

    hass.config_entries.async_update_entry(
        config_entry,
        data=new_data,
        minor_version=current_minor_version,
        version=current_version,
    )
    _LOGGER.info(f"Migration to version {current_version}_{current_minor_version} successful")

    return True
