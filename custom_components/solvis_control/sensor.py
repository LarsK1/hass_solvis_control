"""
Solvis Sensor Entity.

Version: v2.0.0
"""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import async_setup_solvis_entities
from .entity import SolvisEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis sensor entities."""
    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisSensor,
        input_type=0,  # sensor
    )


class SolvisSensor(SolvisEntity, SensorEntity):
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
    ) -> None:
        """Initialize the Solvis sensor."""
        super().__init__(coordinator, device_info, host, name, modbus_address, supported_version, enabled_by_default, data_processing, poll_rate)

        self._attr_native_value = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None
        self.device_class = device_class
        self.state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self.suggested_display_precision = suggested_precision

    def _update_value(self, value, extra_attrs):
        match self.data_processing:
            case 2:
                if value != 0:
                    self._attr_native_value = (1 / (value / 60)) * 1000 / 2 / 42
                else:
                    _LOGGER.debug(f"Division by zero for {self._response_key} with value {value}")
                    self._attr_native_value = 0
            case 3:
                if value != 0:
                    self._attr_native_value = (1 / (value / 60)) * 1000 / 42
                else:
                    _LOGGER.debug(f"Division by zero for {self._response_key} with value {value}")
                    self._attr_native_value = 0
            case _:
                self._attr_native_value = value
        self._attr_extra_state_attributes = {"unprocessed_value": value}
        _LOGGER.debug(f"[{self._response_key}] Successfully updated native value: {self._attr_native_value} (Raw: {value})")

    def _reset_value(self):
        self._attr_extra_state_attributes = {}
