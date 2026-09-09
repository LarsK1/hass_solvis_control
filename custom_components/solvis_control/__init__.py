"""
Module to integrate solvis heaters to.

Version: v2.1.3
"""

"""Solvis integration."""

import logging
import os, json

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.config_entries import ConfigEntryNotReady
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol

from .utils.helpers import create_modbus_client
from .coordinator import SolvisModbusCoordinator
from .diagnostics import scan_modbus_range

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
    CONF_OPTION_13,
    POLL_RATE_SLOW,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    CONF_HKR1_NAME,
    CONF_HKR2_NAME,
    CONF_HKR3_NAME,
)

PLATFORMS: [Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.UPDATE,
]

_LOGGER = logging.getLogger(__name__)
SERVICE_SCAN_MODBUS_RANGE = "scan_modbus_range"
SCAN_MODBUS_RANGE_SCHEMA = vol.Schema(
    {
        vol.Optional("config_entry_id"): str,
        vol.Required("start_address"): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
        vol.Required("end_address"): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
        vol.Optional("register_type", default="both"): vol.In(["input", "holding", "both"]),
        vol.Optional("slave_id", default=1): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
        vol.Optional("delay", default=0.05): vol.All(vol.Coerce(float), vol.Range(min=0, max=5)),
        vol.Optional("batch_size", default=20): vol.All(vol.Coerce(int), vol.Range(min=1, max=125)),
    }
)


# read version from manifest.json
manifest = json.load(open(os.path.join(os.path.dirname(__file__), "manifest.json")))
VERSION = manifest.get("version", "unbekannt")


def _resolve_scan_entry(hass: HomeAssistant, config_entry_id: str | None) -> ConfigEntry:
    """Resolve the config entry used for the Modbus scan action."""
    entries = hass.config_entries.async_entries(DOMAIN)

    if not entries:
        raise HomeAssistantError("No Solvis Control config entry is available.")

    if config_entry_id is not None:
        for entry in entries:
            if entry.entry_id == config_entry_id:
                return entry

        raise HomeAssistantError(f"Config entry '{config_entry_id}' was not found.")

    if len(entries) > 1:
        raise HomeAssistantError(
            "Multiple Solvis Control config entries are configured. Specify config_entry_id."
        )

    return entries[0]


def _register_scan_service(hass: HomeAssistant) -> None:
    """Register the Home Assistant action/service for wide Modbus scans."""
    if hass.services.has_service(DOMAIN, SERVICE_SCAN_MODBUS_RANGE):
        return

    async def _handle_scan_service(call: ServiceCall) -> dict:
        entry = _resolve_scan_entry(hass, call.data.get("config_entry_id"))

        start_address = call.data["start_address"]
        end_address = call.data["end_address"]
        if end_address < start_address:
            raise HomeAssistantError(
                "end_address must be greater than or equal to start_address."
            )

        result = await scan_modbus_range(
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            start_address=start_address,
            end_address=end_address,
            register_type=call.data["register_type"],
            slave_id=call.data["slave_id"],
            delay=call.data["delay"],
            batch_size=call.data["batch_size"],
        )
        result["config_entry_id"] = entry.entry_id
        return result

    hass.services.async_register(
        DOMAIN,
        SERVICE_SCAN_MODBUS_RANGE,
        _handle_scan_service,
        schema=SCAN_MODBUS_RANGE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )


def _remove_scan_service_if_unused(hass: HomeAssistant) -> None:
    """Remove the scan service when no Solvis entries remain loaded."""
    if hass.data.get(DOMAIN):
        return

    if hass.services.has_service(DOMAIN, SERVICE_SCAN_MODBUS_RANGE):
        hass.services.async_remove(DOMAIN, SERVICE_SCAN_MODBUS_RANGE)


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
    unsub_options_update_listener = entry.async_on_unload(entry.add_update_listener(options_update_listener))

    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Create modbus client
    version = int(entry.data.get(DEVICE_VERSION, 0))
    client = create_modbus_client(
        host=conf_host,
        port=conf_port,
        device_version=version,
    )
    entry.runtime_data = {"modbus": client}

    try:
        connected = await entry.runtime_data["modbus"].connect()
        if not connected:
            raise RuntimeError("Modbus connect failed: connect() returned False")

    except Exception as err:
        _LOGGER.error(f"Modbus connect failed: {err}")
        raise ConfigEntryNotReady("Solvis Control not reachable. Try again later...") from err

    # Create coordinator for polling
    coordinator: SolvisModbusCoordinator = SolvisModbusCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_COORDINATOR, coordinator)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_scan_service(hass)

    _LOGGER.info(f"Solvis Control - Version {VERSION}")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        _remove_scan_service_if_unused(hass)

    try:
        entry.runtime_data["modbus"].close()
        _LOGGER.debug("Modbus connection closed on unload")
    except Exception as e:
        _LOGGER.error(f"Error closing Modbus on unload: {e}")
        hass.data[DOMAIN].pop(entry.entry_id)
        _remove_scan_service_if_unused(hass)

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

    if current_version == 2 and current_minor_version == 4:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_OPTION_13 not in new_data:
            new_data[CONF_OPTION_13] = None
        current_minor_version = 5

    if current_version == 2 and current_minor_version == 5:
        _LOGGER.info(f"Migrating from version {current_version}_{current_minor_version}")
        if CONF_HKR1_NAME not in new_data:
            new_data[CONF_HKR1_NAME] = None
        if CONF_HKR2_NAME not in new_data:
            new_data[CONF_HKR2_NAME] = None
        if CONF_HKR3_NAME not in new_data:
            new_data[CONF_HKR3_NAME] = None
        current_minor_version = 6

    hass.config_entries.async_update_entry(
        config_entry,
        data=new_data,
        minor_version=current_minor_version,
        version=current_version,
    )

    _LOGGER.info(f"Migration to version {current_version}_{current_minor_version} successful")

    return True
