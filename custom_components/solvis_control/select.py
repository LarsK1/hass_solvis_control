"""
Solvis Select Entity.

Version: v2.0.0-beta.1
"""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import SolvisModbusCoordinator
from .utils.helpers import write_modbus_value, async_setup_solvis_entities
from .entity import SolvisEntity


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis select entities."""

    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisSelect,
        input_type=1,  # select
    )


class SolvisSelect(SolvisEntity, SelectEntity):
    """Representation of a Solvis select entity."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        enabled_by_default: bool = True,
        options: tuple = None,
        modbus_address: int = None,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
    ) -> None:
        """Initialize the Solvis select entity."""
        super().__init__(coordinator, device_info, host, name, modbus_address, supported_version, enabled_by_default, data_processing, poll_rate)

        self._attr_current_option = None
        self._attr_options = options if options is not None else []  # Set the options for the select entity

    def _update_value(self, value, extra_attrs):
        match self.data_processing:
            case _:
                self._attr_current_option = str(value)
        self._attr_extra_state_attributes = extra_attrs
        _LOGGER.debug(f"[{self._response_key}] Successfully updated current option: {self._attr_current_option} (Raw: {value})")

    def _reset_value(self):
        self._attr_extra_state_attributes = {}

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            option_value = int(option)
            success = await write_modbus_value(self.coordinator.modbus, self.modbus_address, option_value, self._response_key)
            if success:
                _LOGGER.debug(f"[{self._response_key}] Option {option} successfully sent to register {self.modbus_address}")
            else:
                _LOGGER.error(f"[{self._response_key}] Failed to send option {option} to register {self.modbus_address}")
        except ValueError as e:
            _LOGGER.warning(f"[{self._response_key}] Invalid option selected ({option}): {e}")
