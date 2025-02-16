"""Solvis Number Sensor."""

import logging
import re
from decimal import Decimal

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymodbus.exceptions import ConnectionException

from .const import (
    CONF_HOST,
    CONF_NAME,
    DATA_COORDINATOR,
    DOMAIN,
    MANUFACTURER,
    REGISTERS,
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
)
from .coordinator import SolvisModbusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solvis number entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return  # Exit if no host is configured

    # Generate device info
    if DEVICE_VERSION == 1:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=name,
            manufacturer=MANUFACTURER,
            model="Solvis Control 3",
        )
    elif DEVICE_VERSION == 2:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=name,
            manufacturer=MANUFACTURER,
            model="Solvis Control 2",
        )
    else:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=name,
            manufacturer=MANUFACTURER,
            model="Solvis Control",
        )

    # Add number entities
    numbers = []
    for register in REGISTERS:
        if register.input_type == 2:  # Check if the register represents a number
            # Check if the number entity is enabled based on configuration options

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
            _LOGGER.debug(
                f"Supported version: {entry.data.get(DEVICE_VERSION)} / Register version: {register.supported_version}"
            )
            if (
                int(entry.data.get(DEVICE_VERSION)) == 1
                and int(register.supported_version) == 2
            ):
                _LOGGER.debug(
                    f"Skipping SC2 entity for SC3 device: {register.name}/{register.address}"
                )
                continue
            if (
                int(entry.data.get(DEVICE_VERSION)) == 2
                and int(register.supported_version) == 1
            ):
                _LOGGER.debug(
                    f"Skipping SC3 entity for SC2 device: {register.name}/{register.address}"
                )
                continue

            numbers.append(
                SolvisNumber(
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
                )
            )

    async_add_entities(numbers)


class SolvisNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Solvis number entity."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address: int,
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
    ):
        """Initialize the Solvis number entity."""
        super().__init__(coordinator)

        self.multiplier = multiplier
        self.modbus_address = modbus_address
        self._address = address
        self._response_key = name
        self.entity_registry_enabled_default = enabled_by_default
        self.device_class = device_class
        self.state_class = state_class
        self.native_unit_of_measurement = unit_of_measurement
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.unique_id = f"{re.sub('^[A-Za-z0-9_-]*$', '', name)}_{name}"
        self.translation_key = name
        if step_size is not None:
            self.native_step = step_size
        else:
            self.native_step = 1.0

        # Set min/max values if provided in range_data
        if range_data:
            self.native_min_value = range_data[0]
            self.native_max_value = range_data[1]
        self.data_processing = data_processing
        self.poll_rate = poll_rate

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is None:
            _LOGGER.warning("Data from coordinator is None. Skipping update")
            return

        if not isinstance(self.coordinator.data, dict):
            _LOGGER.warning("Invalid data from coordinator")
            self._attr_available = False
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            _LOGGER.warning(f"No data available for {self._response_key}")
            self._attr_available = False
            return

        # Validate the data type received from the coordinator
        if not isinstance(response_data, (int, float, complex, Decimal)):
            _LOGGER.warning(
                f"Invalid response data type from coordinator. {response_data} has type {type(response_data)}"
            )
            self._attr_available = False
            return

        if response_data == -300:
            _LOGGER.warning(
                f"The coordinator failed to fetch data for entity: {self._response_key}"
            )
            self._attr_available = False
            return

        self._attr_available = True
        match self.data_processing:
            case _:
                self._attr_native_value = response_data  # Update the number value
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self.coordinator.modbus.connect()
            await self.coordinator.modbus.write_register(
                self.modbus_address, int(value / self.multiplier), slave=1
            )
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to device")
        finally:
            self.coordinator.modbus.close()
