"""
Solvis Binary Sensor Entity.

Version: v2.1.0
"""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolvisModbusCoordinator
from .utils.helpers import async_setup_solvis_entities
from .entity import SolvisEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis binary sensors entities."""

    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisBinarySensor,
        input_type=4,  # binary sensor
    )


class SolvisBinarySensor(SolvisEntity, BinarySensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        device_class: str | None = None,
        state_class: str | None = None,
        entity_category: str | None = None,
        enabled_by_default: bool = True,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
        modbus_address: int | None = None,
    ) -> None:
        """Initialize the Solvis sensor."""
        super().__init__(coordinator, device_info, host, name, modbus_address, supported_version, enabled_by_default, data_processing, poll_rate)

        self.device_class = device_class
        self.state_class = state_class
        self._attr_is_on = False
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None

    def _update_value(self, value, extra_attrs) -> None:
        """Update the entity's state when data is available."""
        match self.data_processing:
            case 4:
                # extract "first" 9 bits (which are bits 15 to 7 in big endian)
                first_9_bits = (value >> 8) & 0x1FF
                digin_error_keys = ["sicherung_netzbaugruppe", "brennerfehler", "stb1_fehler", "stb2_fehler", "brenner_cm424", "solardruck", "unbekannt", "anlagendruck", "kondensat"]
                extra_attributes = {digin_error_keys[i]: bool(first_9_bits & (1 << (8 - i))) for i in range(9)}
                error_count = sum(extra_attributes.values())
                self._attr_is_on = any(extra_attributes.values())
                self._attr_extra_state_attributes = {"unprocessed_value": value, "error_count": error_count, "first_9_bits": f"{first_9_bits:09b}"}
                # save errors in attributes
                if self._attr_is_on:
                    self._attr_extra_state_attributes.update(extra_attributes)
            case _:
                self._attr_is_on = bool(value)  # Update the sensor value
                self._attr_extra_state_attributes = {"unprocessed_value": value}
        _LOGGER.debug(f"[{self._response_key}] Successfully updated value: {self._attr_is_on} (Raw: {value})")

    def _reset_value(self) -> None:
        """Reset the entity's state when data is not available."""
        self._attr_extra_state_attributes = {}
