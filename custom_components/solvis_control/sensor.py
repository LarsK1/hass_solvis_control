"""
Solvis Sensors.

Version: 1.2.0-alpha11
"""

import logging
import re
from decimal import Decimal

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, REGISTERS
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import generate_device_info, conf_options_map, remove_old_entities
from .utils.helpers import generate_unique_id, write_modbus_value, process_coordinator_data
from .utils.helpers import should_skip_register

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis sensor entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no valid address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add sensor entities
    sensors = []
    active_entity_ids = set()

    for register in REGISTERS:

        if register.input_type == 0:

            if should_skip_register(entry.data, register):
                continue

            entity = SolvisSensor(
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
                register.supported_version,
                register.address,
                register.suggested_precision,
            )
            sensors.append(entity)
            active_entity_ids.add(entity.unique_id)
            _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        await remove_old_entities(hass, entry.entry_id, active_entity_ids)
    except Exception as e:
        _LOGGER.error("Error removing old entities", exc_info=True)

    # add new entities to registry
    async_add_entities(sensors)
    _LOGGER.info(f"Successfully added {len(sensors)} sensor entities")


class SolvisSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        entity_category: str | None = None,
        enabled_by_default: bool = True,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
        modbus_address: int | None = None,
        suggested_precision: int | None = 1,
    ):
        """Initialize the Solvis sensor."""
        super().__init__(coordinator)

        self._host = host
        self.modbus_address = modbus_address
        self._response_key = name
        self._attr_native_value = None
        self.entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None
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
        self.suggested_display_precision = suggested_precision

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        available, value, extra_attrs = process_coordinator_data(self.coordinator.data, self._response_key)

        if available is None:
            return

        self._attr_available = available

        if available:
            self._attr_extra_state_attributes = {"unprocessed_value": value}
            match self.data_processing:
                case 1:  # Version processing
                    if len(str(value)) == 5:
                        value_str = str(value)
                        self._attr_native_value = f"{value_str[0]}.{value_str[1:3]}.{value_str[3:5]}"
                        if self.modbus_address in (32770, 32771):
                            # get device registry
                            device_registry = dr.async_get(self.hass)
                            # get device info
                            device = device_registry.async_get_device(self.device_info["identifiers"])
                            if device is not None:
                                if self.modbus_address == 32770:
                                    device_registry.async_update_device(device.id, sw_version=self._attr_native_value)
                                    if self._attr_native_value != "3.20.16":
                                        ir.async_create_issue(
                                            self.hass,
                                            DOMAIN,
                                            "software_update",
                                            is_fixable=False,
                                            severity=ir.IssueSeverity.WARNING,
                                            translation_key="software_update",
                                        )
                                elif self.modbus_address == 32771:
                                    device_registry.async_update_device(device.id, hw_version=self._attr_native_value)
                    else:
                        _LOGGER.warning("Couldn't process version string to Version.")
                        self._attr_native_value = value
                case 2:  # https://github.com/LarsK1/hass_solvis_control/issues/58#issuecomment-2496245943
                    if value != 0:
                        self._attr_native_value = (1 / (value / 60)) * 1000 / 2 / 42
                    else:
                        _LOGGER.warning(f"Division by zero for {self._response_key} with value {value}")
                        self._attr_native_value = 0
                case 3:
                    if value != 0:
                        self._attr_native_value = (1 / (value / 60)) * 1000 / 42
                    else:
                        _LOGGER.warning(f"Division by zero for {self._response_key} with value {value}")
                        self._attr_native_value = 0
                case _:
                    self._attr_native_value = value

            _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_native_value} (Raw: {value})")

        else:  # not available
            self._attr_extra_state_attributes = {}

        self.schedule_update_ha_state()
