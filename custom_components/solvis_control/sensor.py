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
from homeassistant.helpers.device_registry import async_get

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

    # Add sensor entities
    sensors = []
    for register in REGISTERS:
        if register.input_type == 0:  # Check if the register represents a sensor
            # Check if the sensor is enabled based on configuration options
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
                    register.data_processing,
                    register.poll_rate,
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
        data_processing: int = 0,
        poll_rate: bool = False,
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
        self.data_processing = data_processing
        self.poll_rate = poll_rate

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
            case 1:  # Version
                if len(str(response_data)) == 5:
                    response_data = str(response_data)
                    self._attr_native_value = (
                        f"{response_data[0]}.{response_data[1:3]}.{response_data[3:5]}"
                    )
                    if self._address in (32770, 32771):
                        # Hole den Device-Registry
                        device_registry = async_get(self.hass)

                        # Aktualisiere Geräteinformationen
                        device = device_registry.async_get_device(
                            self.device_info.identifiers
                        )
                        if device is not None:
                            if self._address == 32770:
                                device_registry.async_update_device(
                                    device.id,
                                    sw_version=self._attr_native_value,
                                )
                            elif self._address == 32771:
                                device_registry.async_update_device(
                                    device.id,
                                    hw_version=self._attr_native_value,
                                )
                else:
                    _LOGGER.warning("Couldn't process version string to Version.")
                    self._attr_native_value = response_data
            case (
                2
            ):  # https://github.com/LarsK1/hass_solvis_control/issues/58#issuecomment-2496245943
                self._attr_native_value = ((1 / (response_data / 60)) * 1000) / 42 * 60
            case _:
                self._attr_native_value = response_data  # Update the sensor value
        self.async_write_ha_state()
