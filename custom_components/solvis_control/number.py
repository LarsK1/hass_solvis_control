"""Solvis number sensor."""

from decimal import Decimal
import logging
import re

from pymodbus.exceptions import ConnectionException

from homeassistant.components.number import NumberEntity
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
    CONF_OPTION_3,
    CONF_OPTION_2,
    CONF_OPTION_1,
    CONF_OPTION_4,
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
        if not register.edit:
            continue
        if register.address in (2818, 2049, 3074, 3330):
            continue
        if not entry.data.get(CONF_OPTION_1) and register.conf_option == 1:
            continue
        if not entry.data.get(CONF_OPTION_2) and register.conf_option == 2:
            continue
        if not entry.data.get(CONF_OPTION_3) and register.conf_option == 3:
            continue
        if not entry.data.get(CONF_OPTION_4) and register.conf_option == 4:
            continue
        sensors_to_add.append(
            SolvisSensor(
                hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR],
                device_info,
                conf_host,
                register.name,
                register.unit,
                register.device_class,
                register.state_class,
                register.enabled_by_default,
                register.data,
                register.address,
            )
        )

    async_add_entities(sensors_to_add)


class SolvisSensor(CoordinatorEntity, NumberEntity):
    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address,
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
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
        self.device_class = device_class
        self.state_class = state_class
        self.native_unit_of_measurement = unit_of_measurement
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.unique_id = f"{re.sub('^[A-Za-z0-9_-]*$', '', name)}_{name}"
        self.translation_key = name
        self.native_min_value = data[0]
        self.native_max_value = data[1]
        self.native_step = 1.0

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
        self._attr_native_value = response_data
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self.coordinator.modbus.connect()
        except ConnectionException:
            self.logger.warning("Couldn't connect to device")
        if self.coordinator.modbus.connected:
            await self.coordinator.modbus.write_register(
                self.modbus_address, int(value), slave=1
            )
        self.coordinator.modbus.close()
