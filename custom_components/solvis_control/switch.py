"""
Solvis Switch Sensor.

Version: 1.2.0-alpha11
"""

import logging
import re
from decimal import Decimal

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
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
    """Set up Solvis switch entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add switch entities
    switches = []
    active_entity_ids = set()

    for register in REGISTERS:

        if register.input_type == 3:  # Check if the register represents a switch

            if should_skip_register(entry.data, register):
                continue

            entity = SolvisSwitch(
                coordinator,
                device_info,
                host,
                register.name,
                register.enabled_by_default,
                register.address,
                register.data_processing,
                register.poll_rate,
                register.supported_version,
            )
            switches.append(entity)
            active_entity_ids.add(entity.unique_id)
            _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        await remove_old_entities(hass, entry.entry_id, active_entity_ids)
    except Exception as e:
        _LOGGER.error(f"Error removing old entities: {e}")

    # add new entities to registry
    async_add_entities(switches)  # async_add_entities is synchroneous
    _LOGGER.info(f"Successfully added {len(switches)} switch entities")


class SolvisSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Solvis switch."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address: str,
        name: str,
        enabled_by_default: bool = True,
        modbus_address: int = None,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
    ):
        """Initialize the Solvis switch."""
        super().__init__(coordinator)

        self.modbus_address = modbus_address
        self._address = address
        self._response_key = name
        self.entity_registry_enabled_default = enabled_by_default
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        self._attr_unique_id = generate_unique_id(modbus_address, supported_version, name)
        self.translation_key = name
        self._attr_current_option = None
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
            self._attr_current_option = str(value)
            self._attr_is_on = bool(value)
            self._attr_extra_state_attributes = extra_attrs
            _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_current_option} (Raw: {value})")

        else:  # not available
            self._attr_extra_state_attributes = {}

        self.schedule_update_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        success = await write_modbus_value(self.coordinator.modbus, self.modbus_address, 1, self._response_key)
        if success:
            self._attr_is_on = True
        else:
            _LOGGER.error(f"[{self._response_key}] Failed to turn on (write value 1) at register {self.modbus_address}")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        success = await write_modbus_value(self.coordinator.modbus, self.modbus_address, 0, self._response_key)
        if success:
            self._attr_is_on = False
        else:
            _LOGGER.error(f"[{self._response_key}] Failed to turn off (write value 0) at register {self.modbus_address}")
        self.async_write_ha_state()
