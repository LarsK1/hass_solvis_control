"""
Solvis Binary Sensors.

Version: 1.2.0-alpha11
"""

import logging
import re
from decimal import Decimal

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_resolve_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, REGISTERS
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import generate_device_info, conf_options_map, remove_old_entities
from .utils.helpers import generate_unique_id, write_modbus_value, process_coordinator_data
from .utils.helpers import should_skip_register

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis binary sensors entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add sensor entities
    sensors = []
    active_entity_ids = set()

    for register in REGISTERS:

        if register.input_type == 4:  # Check if the register represents a binary sensor

            if should_skip_register(entry.data, register):
                continue

            entity = SolvisSensor(
                coordinator,
                device_info,
                host,
                register.name,
                register.device_class,
                register.state_class,
                register.entity_category,
                register.enabled_by_default,
                register.data_processing,
                register.poll_rate,
                register.supported_version,
                register.address,
            )
            sensors.append(entity)
            active_entity_ids.add(entity.unique_id)
            _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        await remove_old_entities(hass, entry.entry_id, active_entity_ids)
    except Exception as e:
        _LOGGER.error("Error removing old entities", exc_info=True)

    # add new entities to registry
    async_add_entities(sensors)
    _LOGGER.info(f"Successfully added {len(sensors)} binary sensor entities")


class SolvisSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        device_class: str | None = None,
        state_class: str | None = None,
        entity_category: str | None = None,
        enabled_by_default: bool = True,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
        modbus_address: int | None = None,
    ):
        """Initialize the Solvis sensor."""
        super().__init__(coordinator)

        self._host = host
        self.modbus_address = modbus_address
        self._response_key = name
        self._is_on = False
        self.entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None
        self.entity_registry_enabled_default = enabled_by_default
        self._attr_available = True
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        self._attr_unique_id = generate_unique_id(modbus_address, supported_version, name)
        self.translation_key = name
        self.data_processing = data_processing
        self.poll_rate = poll_rate

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        available, value, extra_attrs = process_coordinator_data(self.coordinator.data, self._response_key)

        if available is None:
            return

        self._attr_available = available

        if available:

            match self.data_processing:
                case 4:
                    # extract "first" 9 bits (which are bits 15 to 7 in big endian)
                    first_9_bits = (value >> 8) & 0x1FF
                    digin_error_keys = ["sicherung_netzbaugruppe", "brennerfehler", "stb1_fehler", "stb2_fehler", "brenner_cm424", "solardruck", "unbekannt", "anlagendruck", "kondensat"]
                    extra_attributes = {digin_error_keys[i]: bool(first_9_bits & (1 << (8 - i))) for i in range(9)}
                    error_count = sum(extra_attributes.values())
                    self._attr_is_on = any(extra_attributes.values())
                    self._attr_extra_state_attributes = {"unprocessed_value": value, "error_count": error_count, "first_9_bits": f"{first_9_bits:09b}"}
                    # save errors in attributes
                    if self._attr_is_on:
                        self._attr_extra_state_attributes.update(extra_attributes)
                case _:
                    self._attr_is_on = bool(value)  # Update the sensor value
                    self._attr_extra_state_attributes = {"unprocessed_value": value}

            _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_is_on} (Raw: {value})")

        else:  # not available
            self._attr_extra_state_attributes = {}

        self.schedule_update_ha_state()
