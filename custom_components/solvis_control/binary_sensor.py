"""Solvis Sensors."""

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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_HOST,
    CONF_NAME,
    DATA_COORDINATOR,
    DOMAIN,
    DEVICE_VERSION,
    REGISTERS,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
)
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import generate_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis binary sensors entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if not host:
        _LOGGER.error("Device has no valid address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add sensor entities
    sensors = []
    active_entity_ids = set()
    for register in REGISTERS:
        if register.input_type == 4:  # Check if the register represents a binary sensor
            # Check if the sensor is enabled based on configuration options
            match register.conf_option:
                case 1:
                    if not entry.data.get(CONF_OPTION_1):
                        continue
                case 2:
                    if not entry.data.get(CONF_OPTION_2):
                        continue
                case 3:
                    if not entry.data.get(CONF_OPTION_3):
                        continue
                case 4:
                    if not entry.data.get(CONF_OPTION_4):
                        continue

            _LOGGER.debug(f"Supported version: {entry.data.get(DEVICE_VERSION)} / Register version: {register.supported_version}")
            if int(entry.data.get(DEVICE_VERSION)) == 1 and int(register.supported_version) == 2:
                _LOGGER.debug(f"Skipping SC2 entity for SC3 device: {register.name}/{register.address}")
                continue
            if int(entry.data.get(DEVICE_VERSION)) == 2 and int(register.supported_version) == 1:
                _LOGGER.debug(f"Skipping SC3 entity for SC2 device: {register.name}/{register.address}")
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
        entity_registry = er.async_get(hass)
        existing_entity_ids = {entity_entry.unique_id for entity_entry in entity_registry.entities.values() if entity_entry.config_entry_id == entry.entry_id}
        entities_to_remove = existing_entity_ids - active_entity_ids  # Set difference
        _LOGGER.debug(f"Vorhandene unique_ids: {existing_entity_ids}")
        _LOGGER.debug(f"Aktive unique_ids: {active_entity_ids}")
        _LOGGER.debug(f"Zu entfernende unique_ids: {entities_to_remove}")
        for entity_id in entities_to_remove:
            entity_entry = entity_registry.entities.get(entity_id)  # get the entity_entry by id
            if entity_entry:  # check if the entity_entry exists
                entity_registry.async_remove(entity_entry.entity_id)  # remove by entity_id
                _LOGGER.debug(f"Removed old entity: {entity_entry.entity_id}")
            else:
                _LOGGER.warning(f"Entity ID {entity_id} not found in registry")

    except Exception as e:
        _LOGGER.error("Fehler beim Entfernen alter Entities", exc_info=True)  # include stacktrace in log

    async_add_entities(sensors)


class SolvisSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address: int,
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

        self._address = address
        self.modbus_address = modbus_address
        self._response_key = name
        self._is_on = False
        self.entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None
        self.entity_registry_enabled_default = enabled_by_default
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        cleaned_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name)
        self.unique_id = f"{modbus_address}_{supported_version}_{cleaned_name}"
        self.translation_key = name
        self.data_processing = data_processing
        self.poll_rate = poll_rate

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is None:
            _LOGGER.warning(f"Data from coordinator for {self._response_key} is None. Skipping update")
            return

        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            _LOGGER.error(f"Invalid data from coordinator: {type(self.coordinator.data)} expected")
            self._attr_available = False
            self.async_write_ha_state()
            return

        response_data = self.coordinator.data.get(self._response_key)

        if response_data is None:
            _LOGGER.warning(f"No data available for {self._response_key}")
            self._attr_available = False
            self.async_write_ha_state()
            return

        # Validate the data type received from the coordinator
        if not isinstance(response_data, (int, float, complex, Decimal)):
            _LOGGER.error(f"Invalid response data type for {self._response_key} from coordinator. {response_data} has type {type(response_data)}")
            self._attr_available = False
            self.async_write_ha_state()
            return

        if response_data == -300:
            _LOGGER.warning(f"The coordinator failed to fetch data for entity: {self._response_key}")
            self._attr_available = False
            self.async_write_ha_state()
            return
        self._attr_available = True
        self._is_on = bool(response_data)  # Update the sensor value
        self.async_write_ha_state()
