"""
Modul to integrate solvis heaters to.

Version: v2.0.0-beta.1
"""

from .coordinator import SolvisModbusCoordinator

"""Solvis integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pymodbus.client import AsyncModbusTcpClient

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
    CONF_OPTION_8,
    CONF_OPTION_9,
    CONF_OPTION_10,
    CONF_OPTION_11,
    CONF_OPTION_12,
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
    # unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    unsub_options_update_listener = entry.async_on_unload(entry.add_update_listener(options_update_listener))

    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data
    entry.runtime_data = {"modbus": AsyncModbusTcpClient(host=conf_host, port=conf_port)}

    # Create coordinator for polling
    coordinator: SolvisModbusCoordinator = SolvisModbusCoordinator(hass, entry)
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
    # Merge options into data so that new conf_options are used.
    new_data = {**config_entry.data, **config_entry.options}
    hass.config_entries.async_update_entry(config_entry, data=new_data)

    # Trigger a full reload of the config entry. This unloads and then sets up the integration again.
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug(f"Migrating configuration from version {config_entry.version}.{config_entry.minor_version}")

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
        current_version = 2
        current_minor_version = 0

    if current_version == 2 and current_minor_version == 0:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_OPTION_5 not in new_data:
            new_data[CONF_OPTION_5] = False
        current_minor_version = 1

    if current_version == 2 and current_minor_version == 1:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_OPTION_6 not in new_data:
            new_data[CONF_OPTION_6] = False
        if CONF_OPTION_7 not in new_data:
            new_data[CONF_OPTION_7] = False
        if POLL_RATE_HIGH not in new_data:
            new_data[POLL_RATE_HIGH] = 10
        current_minor_version = 2

    if current_version == 2 and current_minor_version == 2:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_OPTION_8 not in new_data:
            new_data[CONF_OPTION_8] = False
        current_minor_version = 3

    if current_version == 2 and current_minor_version == 3:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_OPTION_6 not in new_data:
            new_data[CONF_OPTION_6] = False
        else:  # keep read-setting for all sensors, if read was set
            new_data[CONF_OPTION_9] = new_data[CONF_OPTION_6]
            new_data[CONF_OPTION_11] = new_data[CONF_OPTION_6]
        if CONF_OPTION_7 not in new_data:
            new_data[CONF_OPTION_7] = False
        else:  # keep write-setting for all sensors, if write was set
            new_data[CONF_OPTION_10] = new_data[CONF_OPTION_7]
            new_data[CONF_OPTION_12] = new_data[CONF_OPTION_7]
        if CONF_OPTION_9 not in new_data:
            new_data[CONF_OPTION_9] = False
        if CONF_OPTION_10 not in new_data:
            new_data[CONF_OPTION_10] = False
        if CONF_OPTION_11 not in new_data:
            new_data[CONF_OPTION_11] = False
        if CONF_OPTION_12 not in new_data:
            new_data[CONF_OPTION_12] = False
        current_minor_version = 4

    hass.config_entries.async_update_entry(
        config_entry,
        data=new_data,
        minor_version=current_minor_version,
        version=current_version,
    )

    _LOGGER.info(f"Migration to version {current_version}_{current_minor_version} successful")

    return True
