import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_get_current_platform
from homeassistant.config_entries import ConfigEntry
from custom_components.solvis_control.select import SolvisSelect
from custom_components.solvis_control.const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, POLL_RATE_DEFAULT, POLL_RATE_SLOW
from pymodbus.exceptions import ConnectionException
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import entity_registry as er


@pytest.fixture
def mock_coordinator():
    coordinator = AsyncMock()
    coordinator.data = {"TestEntity": 1}
    coordinator.poll_rate_slow = 30
    coordinator.poll_rate_default = 10
    coordinator.modbus = AsyncMock()
    coordinator.modbus.connect = AsyncMock()
    coordinator.modbus.write_register = AsyncMock()
    coordinator.modbus.close = AsyncMock()
    return coordinator


@pytest.fixture
def mock_config_entry():
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_HOST: "127.0.0.1",
        CONF_NAME: "TestDevice",
        DEVICE_VERSION: 1,
        POLL_RATE_DEFAULT: 10,
        POLL_RATE_SLOW: 30,
    }
    return entry


@pytest.fixture
def mock_entity_registry(hass):
    return er.async_get(hass)


@pytest.fixture
def mock_hass():
    hass = AsyncMock(spec=HomeAssistant)
    hass.data = {}
    return hass


@pytest.fixture
def mock_platform():
    platform = MagicMock()
    platform.platform_name = "solvis_control"
    platform.domain = "select"
    return platform


@pytest.fixture
def mock_device_info():
    return DeviceInfo(
        identifiers={("solvis", "test_address")},
        connections={("mac", "00:1A:2B:3C:4D:5E")},
        name="Test Device",
        manufacturer="Solvis",
        model="Test Model",
        model_id="SM-1000",
        sw_version="1.0.0",
        hw_version="1.0",
        via_device=("solvis", "hub_identifier"),
        configuration_url="http://192.168.1.100/config",
        suggested_area="Boiler Room",
    )


@pytest.fixture
def mock_solvis_select(mock_coordinator, mock_device_info):
    return SolvisSelect(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        address="test_address",
        name="Test Entity",
        enabled_by_default=True,
        options=("Option 1", "Option 2"),
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )


def test_solvis_select_initialization(mock_solvis_select):
    assert mock_solvis_select is not None

    assert mock_solvis_select._address == "test_address"
    assert mock_solvis_select._response_key == "Test Entity"
    assert mock_solvis_select.entity_registry_enabled_default is True
    assert mock_solvis_select.device_info is not None
    assert mock_solvis_select.supported_version == 1
    assert mock_solvis_select.unique_id == "1_1_Test_Entity"
    assert mock_solvis_select._attr_options == ("Option 1", "Option 2")
    assert mock_solvis_select.data_processing == 0
    assert mock_solvis_select.modbus_address == 1


@pytest.mark.asyncio
async def test_async_select_option(mock_solvis_select):
    mock_solvis_select.coordinator.modbus.write_register = AsyncMock()

    await mock_solvis_select.async_select_option("1")

    mock_solvis_select.coordinator.modbus.write_register.assert_awaited_once_with(1, 1, slave=1)


@pytest.mark.asyncio
async def test_async_select_option_connection_exception(mock_solvis_select):
    """Test handling of a Modbus connection failure."""

    # Mock write_register to raise a ConnectionException
    mock_solvis_select.coordinator.modbus.write_register = AsyncMock(side_effect=ConnectionException)

    # Call async_select_option with a valid option (should not crash)
    await mock_solvis_select.async_select_option("1")

    # Ensure write_register was attempted once
    mock_solvis_select.coordinator.modbus.write_register.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_coordinator_update(mock_solvis_select):
    """Test coordinator update handling with valid data."""

    # Mock HomeAssistant instance to prevent AttributeError
    mock_solvis_select.hass = MagicMock()

    # Mock Coordinator Data (Simulating a valid update)
    mock_solvis_select.coordinator.data = {"Test Entity": 2}

    # Call the update method
    mock_solvis_select._handle_coordinator_update()

    # Ensure the new value is correctly set
    assert mock_solvis_select._attr_current_option == "2"
    assert mock_solvis_select._attr_extra_state_attributes["raw_value"] == 2
    assert mock_solvis_select._attr_available is True


@pytest.mark.asyncio
async def test_handle_coordinator_update_no_data(mock_solvis_select):
    """Test coordinator update when no data is available."""

    # Simulate missing coordinator data
    mock_solvis_select.coordinator.data = None

    # Call the update method
    mock_solvis_select._handle_coordinator_update()

    # Ensure entity becomes unavailable
    assert mock_solvis_select._attr_available is False


@pytest.mark.asyncio
async def test_handle_coordinator_update_invalid_data(mock_solvis_select):
    """Test coordinator update when data type is invalid."""

    # Mock HomeAssistant instance to prevent AttributeError
    mock_solvis_select.hass = MagicMock()

    # Set invalid data (e.g., string instead of number)
    mock_solvis_select.coordinator.data = {"Test Entity": "invalid_value"}

    # Call update method
    mock_solvis_select._handle_coordinator_update()

    # Ensure entity becomes unavailable
    assert mock_solvis_select._attr_available is False


@pytest.mark.asyncio
async def test_handle_coordinator_update_error_code(mock_solvis_select):
    """Test coordinator update when response is error code (-300)."""

    # Mock HomeAssistant instance
    mock_solvis_select.hass = MagicMock()

    # Set coordinator data to error code
    mock_solvis_select.coordinator.data = {"Test Entity": -300}

    # Call update method
    mock_solvis_select._handle_coordinator_update()

    # Ensure entity is unavailable
    assert mock_solvis_select._attr_available is False


def test_select_options(mock_solvis_select):
    """Test that options are correctly assigned."""

    # Ensure the options list is correctly set
    assert mock_solvis_select._attr_options == ("Option 1", "Option 2")


def test_select_options_none():
    """Test that options default to an empty list when None is passed."""

    # Create an instance with options=None
    select_entity = SolvisSelect(
        coordinator=AsyncMock(),
        device_info=MagicMock(),
        address="test_address",
        name="Test Entity",
        enabled_by_default=True,
        options=None,  # <- None passed instead of a tuple
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )

    # Ensure options defaults to an empty list
    assert select_entity._attr_options == []


def test_select_unique_id(mock_solvis_select):
    """Test that unique_id is generated correctly."""

    # Ensure unique_id follows the expected pattern
    assert mock_solvis_select.unique_id == "1_1_Test_Entity"


def test_select_unique_id_special_chars():
    """Test unique_id generation with special characters in name."""

    # Create an instance with special characters in the name
    select_entity = SolvisSelect(
        coordinator=AsyncMock(),
        device_info=MagicMock(),
        address="test_address",
        name="Test! Entity@#",
        enabled_by_default=True,
        options=("Option 1", "Option 2"),
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )

    # Ensure special characters are replaced with underscores
    assert select_entity.unique_id == "1_1_Test_Entity"
