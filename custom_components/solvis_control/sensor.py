"""Solvis Sensors."""

from decimal import Decimal
import logging
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
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
    """Set up Solvis sensor entities."""

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

    # Add sensor entities
    sensors = []
    for register in REGISTERS:
        if register.input_type == 0:  # Check if the register represents a sensor
            # Check if the sensor is enabled based on configuration options
            if (
                (not entry.data.get(CONF_OPTION_1) and register.conf_option == 1)
                or (not entry.data.get(CONF_OPTION_2) and register.conf_option == 2)
                or (not entry.data.get(CONF_OPTION_3) and register.conf_option == 3)
                or (not entry.data.get(CONF_OPTION_4) and register.conf_option == 4)
            ):
                continue

            sensors.append(
                SolvisSensor(
                    coordinator,
                    device_info,
                    host,
                    register.name,
                    register.unit,
                    register.device_class,
                    register.state_class,
                    register.entity_category,
                    register.enabled_by_default,
                )
            )

    async_add_entities(sensors)



class SolvisSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address: int,
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        entity_category: str | None = None,
        enabled_by_default: bool = True,
    ):
        """Initialize the Solvis sensor."""
        super().__init__(coordinator)

        self._address = address
        self._response_key = name
        if entity_category == "diagnostic":  # Set entity category if specified
            self.entity_category = EntityCategory.DIAGNOSTIC
        self.entity_registry_enabled_default = enabled_by_default
        self.device_class = device_class
        self.state_class = state_class
        self.native_unit_of_measurement = unit_of_measurement
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.unique_id = f"{re.sub('^[A-Za-z0-9_-]*$', '', name)}_{name}"
        self.translation_key = name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is None:
            _LOGGER.warning("Data from coordinator is None. Skipping update")
            self._attr_available = False
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
        self._attr_native_value = response_data  # Update the sensor value
        self.async_write_ha_state()
