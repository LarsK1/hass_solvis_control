"""Solvis Select Entity."""  # More accurate name

from decimal import Decimal
import logging
import re

from pymodbus.exceptions import ConnectionException

from homeassistant.components.select import SelectEntity
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
    MANUFACTURER,
    REGISTERS,
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
    """Set up Solvis select entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name=name,
        manufacturer=MANUFACTURER,
        model="Solvis Control 3",
    )

    # Add select entities
    selects = []
    for register in REGISTERS:
        if register.input_type == 1:  # Check if the register represents a select entity
            # Check if the select entity is enabled based on configuration options
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

            selects.append(
                SolvisSelect(
                    coordinator,
                    device_info,
                    host,
                    register.name,
                    register.enabled_by_default,
                    register.options,  # These are the options for the select entity
                    register.address,
                )
            )

    async_add_entities(selects)


class SolvisSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Solvis select entity."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address: str,
        name: str,
        enabled_by_default: bool = True,
        options: tuple = None,  # Renamed for clarity
        modbus_address: int = None,
    ):
        """Initialize the Solvis select entity."""
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
        self._attr_options = options  # Set the options for the select entity

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
            _LOGGER.warning("No data available for (%s)", self._response_key)
            self._attr_available = False
            return

        # Validate the data type received from the coordinator
        if not isinstance(response_data, (int, float, complex, Decimal)):
            _LOGGER.warning(
                "Invalid response data type from coordinator. %s has type %s",
                response_data,
                type(response_data),
            )
            self._attr_available = False
            return

        self._attr_available = True
        self._attr_current_option = str(response_data)  # Update the selected option
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await self.coordinator.modbus.connect()
            await self.coordinator.modbus.write_register(
                self.modbus_address, int(option), slave=1
            )
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to device")
        finally:
            self.coordinator.modbus.close()
