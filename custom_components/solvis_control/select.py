"""Solvis number sensor."""

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
)
from .coordinator import SolvisModbusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entities."""

    conf_host = entry.data.get(CONF_HOST)
    if conf_host is None:
        _LOGGER.error("Device has no address")
    # Generate device info

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data.get(CONF_HOST))},
        name=entry.data.get(CONF_NAME),
        manufacturer=MANUFACTURER,
        model="Solvis Control 3",
    )

    # Add sensors

    sensors_to_add = []

    for register in REGISTERS:
        if register.address not in (2818,):
            continue
        sensors_to_add.append(
            SolvisSensor(
                hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR],
                device_info,
                conf_host,
                register.name,
                register.enabled_by_default,
                register.data,
                register.address,
            )
        )
    async_add_entities(sensors_to_add)


class SolvisSensor(CoordinatorEntity, SelectEntity):
    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address,
        name: str,
        enabled_by_default: bool = True,
        data: tuple = None,
        modbus_address: int = None,
    ):
        """Init entity."""
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
        self._attr_options = data

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
            _LOGGER.warning("No data for available for (%s)", self._response_key)
            self._attr_available = False
            return
        if (
            not isinstance(response_data, int)
            and not isinstance(response_data, float)
            and not isinstance(response_data, complex)
            and not isinstance(response_data, Decimal)
        ):
            _LOGGER.warning(
                "Invalid response data type from coordinator. %s has type %s",
                response_data,
                type(response_data),
            )
            self._attr_available = False
            return
        self._attr_available = True
        self._attr_current_option = str(response_data)
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await self.coordinator.modbus.connect()
        except ConnectionException:
            self.logger.warning("Couldn't connect to device")
        if self.coordinator.modbus.connected:
            await self.coordinator.modbus.write_register(
                self.modbus_address, int(option), slave=1
            )
        self.coordinator.modbus.close()
