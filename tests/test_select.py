import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get
from custom_components.solvis.select import SolvisSelect
from pymodbus.exceptions import ConnectionException

@pytest.fixture
def mock_coordinator():
    coordinator = AsyncMock()
    coordinator.data = {"test_key": 42}
    coordinator.poll_rate_slow = 60
    coordinator.poll_rate_default = 10
    return coordinator

@pytest.fixture
def mock_hass():
    return AsyncMock(spec=HomeAssistant)

async def test_handle_coordinator_update(mock_coordinator: AsyncMock, mock_hass: HomeAssistant):
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

    entity._handle_coordinator_update()
    assert entity._attr_current_option == "42"
    assert entity._attr_available is True

async def test_async_select_option(mock_coordinator: AsyncMock, mock_hass: HomeAssistant):
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

    with patch.object(entity.coordinator.modbus, "write_register", new=AsyncMock()) as mock_write_register:
        await entity.async_select_option("1")
        mock_write_register.assert_called_once_with(1, 1, slave=1)

async def test_async_select_option_connection_error(mock_coordinator: AsyncMock, mock_hass: HomeAssistant):
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

    with patch.object(entity.coordinator.modbus, "connect", side_effect=ConnectionException):
        await entity.async_select_option("1")
        assert entity._attr_available is False
