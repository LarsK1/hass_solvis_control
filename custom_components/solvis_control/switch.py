"""Solvis Switch Sensor."""

import logging
import re
from decimal import Decimal

from pymodbus.exceptions import ConnectionException

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_HOST,
    CONF_NAME,
    DATA_COORDINATOR,
    DOMAIN,
    DEVICE_VERSION,
    MANUFACTURER,
    REGISTERS,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
)
from .coordinator import SolvisModbusCoordinator

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
    if "VERSIONSC" in entry.data:
        device_info.sw_version = entry.data["VERSIONSC"]
    if "VERSIONNBG" in entry.data:
        device_info.hw_version = entry.data["VERSIONNBG"]

    # Add switch entities
    switches = []
    for register in REGISTERS:
        if register.input_type == 3:  # Check if the register represents a switch
            # Check if the switch is enabled based on configuration options
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
            if DEVICE_VERSION == 1 and register.supported_version == 2:
                continue
            elif DEVICE_VERSION == 2 and register.supported_version == 1:
                continue

            switches.append(
                SolvisSwitch(
                    coordinator,
                    device_info,
                    host,
                    register.name,
                    register.enabled_by_default,
                    register.address,
                    register.data_processing,
                    register.poll_rate,
                )
            )

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
        self.unique_id = f"{re.sub('^[A-Za-z0-9_-]*$', '', name)}_{name}"
        self.translation_key = name
        self._attr_current_option = None
        self.data_processing = data_processing
        self.poll_rate = poll_rate

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is None:
            _LOGGER.warning("Data from coordinator is None. Skipping update")
            self._attr_available = False
            return

        elif not isinstance(self.coordinator.data, dict):
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
            _LOGGER.warning(f"Invalid response data type from coordinator. {response_data} has type {type(response_data)}")

            self._attr_available = False
            return

        if response_data == -300:
            _LOGGER.warning(f"The coordinator failed to fetch data for entity: {self._response_key}")
            self._attr_available = False
            return

        self._attr_available = True
        self._attr_current_option = str(response_data)
        self._attr_is_on = bool(response_data)  # Update the switch state
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        try:
            await self.coordinator.modbus.connect()
            await self.coordinator.modbus.write_register(self.modbus_address, 1, slave=1)
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to device")
        finally:
            self.coordinator.modbus.close()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        try:
            await self.coordinator.modbus.connect()
            await self.coordinator.modbus.write_register(self.modbus_address, 0, slave=1)
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to device")
        finally:
            self.coordinator.modbus.close()
