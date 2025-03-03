import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_get_current_platform
from custom_components.solvis_control.select import SolvisSelect
from pymodbus.exceptions import ConnectionException


@pytest.fixture
def mock_coordinator():
    coordinator = AsyncMock()
    coordinator.data = {"test_key": 42}
    coordinator.poll_rate_slow = 60
    coordinator.poll_rate_default = 10
    coordinator.modbus = AsyncMock()
    return coordinator


@pytest.fixture
def mock_hass():
    return AsyncMock(spec=HomeAssistant)


@pytest.fixture
def mock_platform():
    platform = MagicMock()
    platform.platform_name = "solvis_control"
    platform.domain = "select"
    return platform


async def test_handle_coordinator_update(mock_coordinator: AsyncMock, mock_hass: HomeAssistant, mock_platform):
    entity = SolvisSelect(
        coordinator=mock_coordinator,
        device_info={},
        address="test_address",
        name="test_key",
        options=("Option1", "Option2"),
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )
    entity.hass = mock_hass
    mock_hass.loop = asyncio.get_event_loop()  # mock_hass needs a loop for schedule_update_ha_state()
    entity.platform = mock_platform
    entity.async_write_ha_state = AsyncMock()  # async_write_ha_state is @callback - can't be awaited

    await entity._handle_coordinator_update()
    assert entity._attr_current_option == "42"
    assert entity._attr_available is True
    entity.async_write_ha_state.assert_called()


async def test_async_select_option(mock_coordinator: AsyncMock, mock_hass: HomeAssistant, mock_platform):
    entity = SolvisSelect(
        coordinator=mock_coordinator,
        device_info={},
        address="test_address",
        name="test_key",
        options=("Option1", "Option2"),
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )
    entity.hass = mock_hass
    entity.platform = mock_platform

    with patch.object(entity.coordinator.modbus, "write_register", new=AsyncMock()) as mock_write_register:
        await entity.async_select_option("1")
        mock_write_register.assert_called_once_with(1, 1, slave=1)


async def test_async_select_option_connection_error(mock_coordinator: AsyncMock, mock_hass: HomeAssistant, mock_platform):
    entity = SolvisSelect(
        coordinator=mock_coordinator,
        device_info={},
        address="test_address",
        name="test_key",
        options=("Option1", "Option2"),
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )
    entity.hass = mock_hass
    entity.platform = mock_platform

    with patch.object(entity.coordinator.modbus, "connect", side_effect=ConnectionException):
        await entity.async_select_option("1")
        assert entity._attr_available is False
