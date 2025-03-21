"""
Solvis Select Entity.

Version: 1.2.0-alpha11
"""

import logging
import re
from decimal import Decimal

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import async_resolve_entity_id
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymodbus.exceptions import ConnectionException

from .const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, REGISTERS
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import generate_device_info, conf_options_map, remove_old_entities
from .utils.helpers import generate_unique_id, write_modbus_value, process_coordinator_data
from .utils.helpers import should_skip_register

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis select entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add select entities
    selects = []
    active_entity_ids = set()

    for register in REGISTERS:

        if register.input_type == 1:  # Check if the register represents a select entity

            if should_skip_register(entry.data, register):
                continue

            entity = SolvisSelect(
                coordinator,
                device_info,
                host,
                register.name,
                register.enabled_by_default,
                register.options,  # These are the options for the select entity
                register.address,
                register.data_processing,
                register.poll_rate,
                register.supported_version,
            )
            selects.append(entity)
            active_entity_ids.add(entity.unique_id)
            _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        await remove_old_entities(hass, entry.entry_id, active_entity_ids)
    except Exception as e:
        _LOGGER.error(f"Error removing old entities: {e}")

    # add new entities to registry
    async_add_entities(selects)  # async_add_entities is synchroneous
    _LOGGER.info(f"Successfully added {len(selects)} select entities")


class SolvisSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Solvis select entity."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        enabled_by_default: bool = True,
        options: tuple = None,  # Renamed for clarity
        modbus_address: int = None,
        data_processing: int = None,
        poll_rate: bool = False,
        supported_version: int = 1,
    ):
        """Initialize the Solvis select entity."""
        super().__init__(coordinator)

        self.modbus_address = modbus_address
        self._host = host
        self._response_key = name
        self.entity_registry_enabled_default = enabled_by_default
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        self._attr_unique_id = generate_unique_id(modbus_address, supported_version, name)
        self.translation_key = name
        self._attr_current_option = None
        self._attr_options = options if options is not None else []  # Set the options for the select entity
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
                case _:
                    self._attr_current_option = str(value)  # Update the selected option
            self._attr_extra_state_attributes = extra_attrs
            _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_current_option} (Raw: {value})")

        else:  # not available
            self._attr_extra_state_attributes = {}

        self.schedule_update_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            option_value = int(option)
            success = await write_modbus_value(self.coordinator.modbus, self.modbus_address, option_value, self._response_key)
            if success:
                _LOGGER.debug(f"[{self._response_key}] Option {option} successfully sent to register {self.modbus_address}")
            else:
                _LOGGER.error(f"[{self._response_key}] Failed to send option {option} to register {self.modbus_address}")
        except ValueError as e:
            _LOGGER.warning(f"[{self._response_key}] Invalid option selected ({option}): {e}")
