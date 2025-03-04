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
from .utils.helpers import generate_device_info, conf_options_map

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
            # Check if the switch is enabled based on configuration options
            if isinstance(register.conf_option, tuple):
                if not all(entry.data.get(conf_options_map[option]) for option in register.conf_option):
                    continue
            else:
                if register.conf_option == 0:
                    pass
                elif not entry.data.get(conf_options_map.get(register.conf_option)):
                    continue
            # SC3 - SC2
            _LOGGER.debug(f"Supported version: {entry.data.get(DEVICE_VERSION)} / Register version: {register.supported_version}")
            if int(entry.data.get(DEVICE_VERSION)) == 1 and int(register.supported_version) == 2:
                _LOGGER.debug(f"Skipping SC2 entity for SC3 device: {register.name}/{register.address}")
                continue
            if int(entry.data.get(DEVICE_VERSION)) == 2 and int(register.supported_version) == 1:
                _LOGGER.debug(f"Skipping SC3 entity for SC2 device: {register.name}/{register.address}")
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

    except Exception as e:
        _LOGGER.error(f"Error removing old entities: {e}")
    async_add_entities(switches)


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
        cleaned_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name)
        self.unique_id = f"{modbus_address}_{supported_version}_{cleaned_name}"
        self.translation_key = name
        self._attr_current_option = None
        self.data_processing = data_processing
        self.poll_rate = poll_rate

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        register = next((r for r in REGISTERS if r.name == self._response_key), None)

        # skip slow poll registers not being updated
        if register and (register.poll_rate == 1 and register.poll_time != self.coordinator.poll_rate_slow):
            _LOGGER.debug(f"Skipping update for {self._response_key} (slow polling active, remaining wait time: {register.poll_time}s)")
            return
        elif register and (register.poll_rate == 0 and register.poll_time != self.coordinator.poll_rate_default):
            _LOGGER.debug(f"Skipping update for {self._response_key} (standard polling active, remaining wait time: {register.poll_time}s)")
            return

        if self.coordinator.data is None:
            _LOGGER.warning("Data from coordinator is None. Skipping update")
            return

        elif not isinstance(self.coordinator.data, dict):
            _LOGGER.warning("Invalid data from coordinator")
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
            _LOGGER.warning(f"Invalid response data type from coordinator. {response_data} has type {type(response_data)}")
            self._attr_available = False
            self.async_write_ha_state()
            return

        if response_data == -300:
            _LOGGER.warning(f"The coordinator failed to fetch data for entity: {self._response_key}")
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._attr_current_option = str(response_data)
        _LOGGER.debug(f"Updated {self._response_key} to {response_data} / type: {type(response_data)}")
        self._attr_is_on = bool(response_data)  # Update the switch state
        self._attr_extra_state_attributes = {"raw_value": response_data}
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        try:
            await self.coordinator.modbus.connect()
            await self.coordinator.modbus.write_register(address=self.modbus_address, value=1, slave=1)
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to device")
        finally:
            self.coordinator.modbus.close()
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        try:
            await self.coordinator.modbus.connect()
            await self.coordinator.modbus.write_register(address=self.modbus_address, value=0, slave=1)
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to device")
        finally:
            self.coordinator.modbus.close()
            self._attr_is_on = False
            self.async_write_ha_state()
