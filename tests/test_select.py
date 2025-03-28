import pytest
import logging
from pytest import LogCaptureFixture
from unittest.mock import AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from custom_components.solvis_control.select import SolvisSelect, async_setup_entry, _LOGGER
from custom_components.solvis_control.const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, POLL_RATE_DEFAULT, POLL_RATE_SLOW, ModbusFieldConfig
from pymodbus.exceptions import ConnectionException
from homeassistant.helpers import entity_registry as er


@pytest.fixture
def select_entity(hass, mock_coordinator, mock_device_info):
    entity = SolvisSelect(mock_coordinator, mock_device_info, "host", "test", True)
    entity.hass = hass
    return entity


@pytest.fixture
def mock_solvis_select(mock_coordinator, mock_device_info):
    return SolvisSelect(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_host",
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
    assert mock_solvis_select._host == "test_host"
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
    mock_solvis_select.modbus_address = 1
    mock_solvis_select._response_key = "Test Entity"

    response_mock = MagicMock()
    response_mock.isError.return_value = False
    mock_solvis_select.coordinator.modbus.write_register = AsyncMock(return_value=response_mock)

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

    # Mock HomeAssistant instance to prevent AttributeError
    mock_solvis_select.hass = MagicMock(loop=MagicMock())

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
        host="test_host",
        name="Test Entity",
        enabled_by_default=True,
        options=None,  # None passed instead of a tuple
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
        host="test_host",
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


@pytest.mark.asyncio
async def test_handle_coordinator_update_skip_slow_polling(mock_solvis_select):
    """Test skipping updates for slow polling."""
    mock_solvis_select.hass = MagicMock()

    mock_solvis_select.coordinator.poll_rate_slow = 30
    register_mock = MagicMock()
    register_mock.poll_rate = 1
    register_mock.poll_time = 10  # Nicht identisch zu poll_rate_slow, daher Skip

    with patch("custom_components.solvis_control.select.REGISTERS", [register_mock]):
        mock_solvis_select._handle_coordinator_update()

    assert mock_solvis_select._attr_current_option is None


@pytest.mark.asyncio
async def test_handle_coordinator_update_skip_standard_polling(mock_solvis_select):
    """Test skipping updates for standard polling."""
    mock_solvis_select.hass = MagicMock()

    mock_solvis_select.coordinator.poll_rate_default = 10
    register_mock = MagicMock()
    register_mock.poll_rate = 0
    register_mock.poll_time = 5  # Nicht identisch zu poll_rate_default, daher Skip

    with patch("custom_components.solvis_control.select.REGISTERS", [register_mock]):
        mock_solvis_select._handle_coordinator_update()

    assert mock_solvis_select._attr_current_option is None


@pytest.mark.asyncio
async def test_async_setup_entry_entity_removal_exception(hass, mock_config_entry):
    """Test exception handling during entity removal."""
    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}

    with (
        patch("homeassistant.helpers.entity_registry.async_get", side_effect=Exception("Test Exception")),
        patch("custom_components.solvis_control.select.generate_device_info"),
        patch("custom_components.solvis_control.select.REGISTERS", []),
        patch("custom_components.solvis_control.select._LOGGER.error") as mock_log_error,
    ):

        mock_add_entities = MagicMock()
        await async_setup_entry(hass, mock_config_entry, mock_add_entities)

        mock_log_error.assert_called_with("Error removing old entities: Test Exception")
        mock_add_entities.assert_called()


def test_solvis_select_default_options():
    """Test default options set correctly when no options provided."""
    entity = SolvisSelect(
        coordinator=AsyncMock(),
        device_info=MagicMock(),
        host="test_host",
        name="TestEntity",
        modbus_address=1,
    )

    assert entity._attr_options == []


def test_translation_key(mock_solvis_select):
    """Test correct setting of translation_key."""
    assert mock_solvis_select.translation_key == "Test Entity"


def test_unique_id_all_special_chars():
    """Test unique_id with name having only special chars."""
    entity = SolvisSelect(
        coordinator=AsyncMock(),
        device_info=MagicMock(),
        host="test_host",
        name="!@#$%^&*()",
        modbus_address=1,
        supported_version=2,
    )

    assert entity.unique_id == "1_2"


@pytest.mark.asyncio
async def test_async_setup_entry_no_host(hass, mock_config_entry):
    """Test setup entry when no host is provided."""
    mock_config_entry.data.pop(CONF_HOST, None)

    with patch("custom_components.solvis_control.select._LOGGER.error") as mock_logger:
        hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
        await async_setup_entry(hass, mock_config_entry, AsyncMock())

        mock_logger.assert_called_with("Device has no address")


@pytest.mark.asyncio
async def test_async_setup_entry_skips_sc2_entity_on_sc3_device(hass, mock_config_entry):
    """Test if SC2 entities are skipped on SC3 device."""

    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
    mock_config_entry.data[DEVICE_VERSION] = "1"  # SC3

    mock_register = ModbusFieldConfig(
        name="test_entity_sc2",
        unit=None,
        device_class=None,
        state_class=None,
        address=123,
        input_type=1,
        supported_version=2,  # SC2
    )

    with patch("custom_components.solvis_control.select.REGISTERS", [mock_register]):
        with patch("custom_components.solvis_control.utils.helpers._LOGGER.debug") as mock_logger:
            await async_setup_entry(hass, mock_config_entry, MagicMock())
            mock_logger.assert_any_call("[test_entity_sc2 | 123] Skipping SC2 entity for SC3 device.")


@pytest.mark.asyncio
async def test_async_setup_entry_existing_entities_handling(hass, mock_config_entry):
    """Test removal of existing entities during setup."""

    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}

    mock_entity_registry = MagicMock()
    mock_entity_registry.entities = {
        "entity_1": MagicMock(unique_id="old_1", entity_id="entity_1", config_entry_id=mock_config_entry.entry_id),
        "entity_2": MagicMock(unique_id="old_2", entity_id="entity_2", config_entry_id=mock_config_entry.entry_id),
    }

    mock_entity_registry.async_remove = MagicMock()

    mock_register1 = ModbusFieldConfig(
        name="new 1",
        address=100,
        unit=None,
        device_class=None,
        state_class=None,
        input_type=1,
        conf_option=0,
        supported_version=0,
    )

    mock_register2 = ModbusFieldConfig(
        name="new 2",
        address=200,
        unit=None,
        device_class=None,
        state_class=None,
        input_type=1,
        conf_option=0,
        supported_version=0,
    )

    with patch("homeassistant.helpers.entity_registry.async_get", return_value=mock_entity_registry):
        with patch("custom_components.solvis_control.select.REGISTERS", [mock_register1, mock_register2]):
            with patch("custom_components.solvis_control.utils.helpers.async_resolve_entity_id") as mock_resolve:
                with patch("custom_components.solvis_control.utils.helpers._LOGGER.debug") as mock_log_debug:
                    # Mock async_resolve_entity_id()
                    mock_resolve.side_effect = lambda reg, uid: f"entity_{uid[-1]}"

                    await async_setup_entry(hass, mock_config_entry, MagicMock())

                    mock_entity_registry.async_remove.assert_any_call("entity_1")
                    mock_entity_registry.async_remove.assert_any_call("entity_2")
                    assert mock_entity_registry.async_remove.call_count == 2

                    mock_log_debug.assert_any_call("Removed old entity: old_1 (entity_id: entity_1)")
                    mock_log_debug.assert_any_call("Removed old entity: old_2 (entity_id: entity_2)")


@pytest.mark.asyncio
async def test_handle_coordinator_update_no_matching_register(mock_solvis_select):
    """Test _handle_coordinator_update when no matching register is found."""
    mock_solvis_select.hass = MagicMock()

    with patch("custom_components.solvis_control.select.REGISTERS", []):
        mock_solvis_select._handle_coordinator_update()

    assert mock_solvis_select._attr_available is False


@pytest.mark.asyncio
async def test_handle_coordinator_update_missing_poll_rate(mock_solvis_select):
    """Test _handle_coordinator_update when poll rate is missing."""
    mock_solvis_select.hass = MagicMock()
    mock_solvis_select.coordinator.poll_rate_slow = 30

    register_mock = MagicMock()
    register_mock.poll_rate = None

    with patch("custom_components.solvis_control.select.REGISTERS", [register_mock]):
        mock_solvis_select._handle_coordinator_update()

    assert mock_solvis_select._attr_available is False


@pytest.mark.asyncio
async def test_async_select_option_modbus_failure(mock_solvis_select):
    """Test async_select_option failure due to Modbus disconnection."""

    mock_solvis_select.coordinator.modbus.connect = AsyncMock(return_value=False)

    error_response = MagicMock()
    error_response.isError.return_value = True
    mock_solvis_select.coordinator.modbus.write_register = AsyncMock(return_value=error_response)

    with patch("custom_components.solvis_control.select._LOGGER.error") as mock_logger:
        await mock_solvis_select.async_select_option("1")

        mock_logger.assert_called_with("[Test Entity] Failed to send option 1 to register 1")


@pytest.mark.asyncio
async def test_handle_coordinator_update_unexpected_data_type(mock_solvis_select):
    """Test handling of unexpected data types in coordinator data."""
    mock_solvis_select.hass = MagicMock()
    mock_solvis_select.coordinator.data = {"Test Entity": {"unexpected": "dict"}}

    with patch("custom_components.solvis_control.utils.helpers._LOGGER.warning") as mock_logger:
        mock_solvis_select._handle_coordinator_update()

        mock_logger.assert_called_with("[Test Entity] Invalid response data type from coordinator: {'unexpected': 'dict'} has type <class 'dict'>")


@pytest.mark.asyncio
async def test_handle_coordinator_update_with_float_value(mock_solvis_select):
    """Test that float values are correctly processed in _handle_coordinator_update."""
    mock_solvis_select.hass = MagicMock()
    mock_solvis_select.coordinator.data = {"Test Entity": 12.34}

    mock_solvis_select._handle_coordinator_update()

    assert mock_solvis_select._attr_current_option == "12.34"
    assert mock_solvis_select._attr_extra_state_attributes["raw_value"] == 12.34
    assert mock_solvis_select._attr_available is True


@pytest.mark.asyncio
async def test_handle_coordinator_update_with_complex_value(mock_solvis_select):
    """Test that complex numbers are correctly rejected in _handle_coordinator_update."""
    mock_solvis_select.hass = MagicMock()
    mock_solvis_select.coordinator.data = {"Test Entity": complex(2, 3)}

    with patch("custom_components.solvis_control.utils.helpers._LOGGER.warning") as mock_logger:
        mock_solvis_select._handle_coordinator_update()

        mock_logger.assert_called_with("[Test Entity] Invalid response data type from coordinator: (2+3j) has type <class 'complex'>")

        assert mock_solvis_select._attr_available is False


@pytest.mark.asyncio
async def test_async_handle_coordinator_update_none_data(hass, mock_coordinator, mock_device_info):
    """Test handling coordinator update with None data."""
    select_entity = SolvisSelect(mock_coordinator, mock_device_info, "host", "test", True)
    select_entity.hass = hass
    select_entity.platform = MagicMock()
    select_entity.entity_id = "select.test"

    mock_coordinator.data = None
    select_entity._handle_coordinator_update()

    assert select_entity._attr_available is False


@pytest.mark.asyncio
async def test_async_handle_coordinator_update_invalid_data(hass, mock_coordinator, mock_device_info):
    """Test handling coordinator update with invalid data type."""
    select_entity = SolvisSelect(mock_coordinator, mock_device_info, "host", "test", True)
    select_entity.hass = hass
    select_entity.platform = MagicMock()
    select_entity.entity_id = "select.test"

    mock_coordinator.data = "invalid"

    select_entity._handle_coordinator_update()

    assert select_entity._attr_available is False


@pytest.mark.asyncio
async def test_async_handle_coordinator_update_missing_key(hass, mock_coordinator, mock_device_info):
    """Test handling coordinator update with missing response key."""
    select_entity = SolvisSelect(mock_coordinator, mock_device_info, "host", "missing_key", True)
    select_entity.hass = hass
    select_entity.platform = MagicMock()
    select_entity.entity_id = "select.missing_key"

    mock_coordinator.data = {"other_key": 123}
    select_entity._handle_coordinator_update()

    assert select_entity._attr_available is False


@pytest.mark.asyncio
async def test_async_select_option_invalid_option(hass, mock_coordinator, mock_device_info, caplog: LogCaptureFixture):
    """Test select_option with invalid (non-integer) input."""
    select_entity = SolvisSelect(mock_coordinator, mock_device_info, "host", "test", True, modbus_address=100)
    select_entity.hass = hass
    select_entity.platform = MagicMock()
    select_entity.entity_id = "select.test"

    with caplog.at_level(logging.WARNING):
        await select_entity.async_select_option("invalid")

    assert "Invalid option selected" in caplog.text


@pytest.mark.asyncio
async def test_async_select_option_connection_error(hass, mock_coordinator, mock_device_info):
    """Test handling connection error during option selection."""
    select_entity = SolvisSelect(mock_coordinator, mock_device_info, "host", "test", True, modbus_address=100)
    select_entity.hass = hass
    select_entity.platform = MagicMock()
    select_entity.entity_id = "select.test"

    mock_coordinator.modbus.connect = AsyncMock(return_value=False)
    mock_coordinator.modbus.write_register = AsyncMock()

    with patch("custom_components.solvis_control.select._LOGGER.error") as mock_logger:
        await select_entity.async_select_option("1")
        mock_logger.assert_called_with("[test] Failed to send option 1 to register 100")
