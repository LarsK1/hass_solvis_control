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
from .utils.helpers import generate_device_info, conf_options_map, remove_old_entities, generate_unique_id

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

            # Check if the number entity is enabled based on configuration options
            if isinstance(register.conf_option, tuple):
                if not all(entry.data.get(conf_options_map[option]) for option in register.conf_option):
                    continue
            else:
                if register.conf_option in (0, 7):  # treat conf_option 7 like conf_option 0
                    pass
                elif not entry.data.get(conf_options_map.get(register.conf_option)):
                    continue

            device_version_str = entry.data.get(DEVICE_VERSION, "")

            _LOGGER.debug(f"Supported version: {device_version_str} / Register version: {register.supported_version}")

            try:
                device_version = int(device_version_str)
            except (ValueError, TypeError):
                device_version = None

            if device_version == 1 and int(register.supported_version) == 2:
                _LOGGER.debug(f"Skipping SC2 entity for SC3 device: {register.name}/{register.address}")
                continue

            if device_version == 2 and int(register.supported_version) == 1:
                _LOGGER.debug(f"Skipping SC3 entity for SC2 device: {register.name}/{register.address}")
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
        supported_version: int = 1,
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
        self.supported_version = supported_version
        self._attr_unique_id = generate_unique_id(modbus_address, supported_version, name)
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

        if self.coordinator.data is None:
            _LOGGER.warning("Data from coordinator is None. Skipping update")
            return

        if not isinstance(self.coordinator.data, dict):
            _LOGGER.warning("Invalid data from coordinator")
            self._attr_available = False
            self.schedule_update_ha_state()
            return

        if self._response_key not in self.coordinator.data:
            _LOGGER.debug(f"Skipping update for {self._response_key}: no data available in coordinator. Skipped update!?")
            return

        response_data = self.coordinator.data.get(self._response_key)

        if response_data is None:
            _LOGGER.warning(f"No data available for {self._response_key}")
            self._attr_available = False
            self.schedule_update_ha_state()
            return

        # Validate the data type received from the coordinator
        if not isinstance(response_data, (int, float, complex, Decimal)):
            _LOGGER.warning(f"Invalid response data type from coordinator. {response_data} has type {type(response_data)}")
            self._attr_available = False
            self.schedule_update_ha_state()
            return

        if response_data == -300:
            _LOGGER.warning(f"The coordinator failed to fetch data for entity: {self._response_key}")
            self._attr_available = False
            self.schedule_update_ha_state()
            return

        self._attr_available = True

        match self.data_processing:
            case _:
                self._attr_native_value = response_data  # Update the number value
        self._attr_extra_state_attributes = {"raw_value": response_data}
        self.schedule_update_ha_state()
        _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_native_value} (Raw: {response_data})")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        modbus_value = int(value / self.multiplier)
        try:
            await self.coordinator.modbus.connect()
            response = await self.coordinator.modbus.write_register(self.modbus_address, modbus_value, slave=1)
            # Prüfe, ob die Antwort einen Fehler enthält
            if response.isError():
                raise Exception(f"Modbus error response: {response}")
            _LOGGER.debug(f"[{self._response_key}] Successfully wrote value {modbus_value} to Modbus register {self.modbus_address}")

        except ConnectionException as e:
            _LOGGER.warning(f"[{self._response_key}] Couldn't connect to Modbus device: {e}")

        except Exception as e:
            _LOGGER.error(f"[{self._response_key}] Unexpected error while writing to Modbus: {e}")

        finally:
            self.coordinator.modbus.close()
