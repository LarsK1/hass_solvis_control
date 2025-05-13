"""
Solvis Update Entity.

Version: v2.0.0
"""

import logging

from homeassistant.components.update import UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolvisModbusCoordinator
from .utils.helpers import async_setup_solvis_entities
from .entity import SolvisEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis update entitie."""

    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisUpdate,
        input_type=3,  # switch
    )


class SolvisUpdate(SolvisEntity, UpdateEntity):
    """Representation of a Solvis switch."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        enabled_by_default: bool = True,
        modbus_address: int = None,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
    ) -> None:
        """Initialize the Solvis update entity."""
        super().__init__(coordinator, device_info, host, name, modbus_address, supported_version, enabled_by_default, data_processing, poll_rate)

        self._attr_current_option = None

    def _update_value(self, value, extra_attrs) -> None:
        """Update state from coordinator data."""
        self._attr_current_option = str(value)
        self._attr_is_on = bool(value)
        self._attr_extra_state_attributes = extra_attrs
        _LOGGER.debug(f"[{self._response_key}] Successfully updated current option: {self._attr_current_option} (Raw: {value})")
