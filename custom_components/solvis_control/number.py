"""
Solvis Number Sensor.

Version: 1.2.0-alpha11
"""

import logging
import re
from decimal import Decimal

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymodbus.exceptions import ConnectionException

from .const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, REGISTERS, DEVICE_VERSION
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import generate_device_info, conf_options_map, remove_old_entities
from .utils.helpers import generate_unique_id, write_modbus_value, process_coordinator_data
from .utils.helpers import should_skip_register

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis number entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add number entities
    numbers = []
    active_entity_ids = set()

    for register in REGISTERS:

        if register.input_type == 2:  # Check if the register represents a number

            if should_skip_register(entry.data, register):
                continue

            entity = SolvisNumber(
                coordinator,
                device_info,
                host,
                register.name,
                register.unit,
                register.device_class,
                register.state_class,
                register.enabled_by_default,
                register.range_data,
                register.step_size,
                register.address,
                register.multiplier,
                register.data_processing,
                register.poll_rate,
                register.supported_version,
            )
            numbers.append(entity)
            active_entity_ids.add(entity.unique_id)
            _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        await remove_old_entities(hass, entry.entry_id, active_entity_ids)
    except Exception as e:
        _LOGGER.error(f"Error removing old entities: {e}")

    # add new entities to registry
    async_add_entities(numbers)  # async_add_entities is synchroneous
    _LOGGER.info(f"Successfully added {len(numbers)} number entities")


class SolvisNumber(NumberEntity, CoordinatorEntity):
    """Representation of a Solvis number entity."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        enabled_by_default: bool = True,
        range_data: tuple = None,
        step_size: int | None = None,
        modbus_address: int = None,
        multiplier: float = 1,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
    ):
        """Initialize the Solvis number entity."""
        super().__init__(coordinator)

        self.multiplier = multiplier
        self.modbus_address = modbus_address
        self._host = host
        self._response_key = name
        self.entity_registry_enabled_default = enabled_by_default
        self.device_class = device_class
        self.state_class = state_class
        self.native_unit_of_measurement = unit_of_measurement
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        self._attr_unique_id = generate_unique_id(modbus_address, supported_version, name)
        self.translation_key = name
        self.data_processing = data_processing
        self.poll_rate = poll_rate

        if step_size is not None:
            self.native_step = step_size
        else:
            self.native_step = 1.0

        # Set min/max values if provided in range_data
        if range_data:
            self.native_min_value = range_data[0]
            self.native_max_value = range_data[1]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        # register = next((r for r in REGISTERS if r.name == self._response_key), None)

        # no special treat for treat conf_option 7 necessary
        # if register.conf_option == 7:
        #     _LOGGER.debug(f"Skipping update for {self._response_key} (write entity)")
        #     self.async_set_native_value(self._attr_native_value)
        #     _LOGGER.debug(f"Updated write entity {self._response_key} with value {self._attr_native_value}")
        #     return

        # skip slow poll registers not being updated
        # ---
        # buggy: entities are already filtered by polling interval
        # in coordinator > removed to fix #172
        # ---
        # if register and (register.poll_rate == 1 and register.poll_time != self.coordinator.poll_rate_slow):
        #     _LOGGER.debug(f"Skipping update for {self._response_key} (slow polling active, remaining wait time: {register.poll_time}s)")
        #     return
        # elif register and (register.poll_rate == 0 and register.poll_time != self.coordinator.poll_rate_default):
        #     _LOGGER.debug(f"Skipping update for {self._response_key} (standard polling active, remaining wait time: {register.poll_time}s)")
        #     return

        available, value, extra_attrs = process_coordinator_data(self.coordinator.data, self._response_key)

        if available is None:
            return

        self._attr_available = available

        if available:
            match self.data_processing:
                case _:
                    self._attr_native_value = value  # Update the number value
            self._attr_extra_state_attributes = extra_attrs
            _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_native_value} (Raw: {value})")

        else:  # not available
            self._attr_extra_state_attributes = {}

        self.schedule_update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        modbus_value = int(value / self.multiplier)
        success = await write_modbus_value(self.coordinator.modbus, self.modbus_address, modbus_value, self._response_key)
        if not success:
            _LOGGER.error(f"[{self._response_key}] Failed to write value {modbus_value} to register {self.modbus_address}")
