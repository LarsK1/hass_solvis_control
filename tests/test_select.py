"""
Tests for Solvis Select Entity

Version: v2.1.0
"""

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

# # # Tests for initialization # # #


def test_select_solvis_select_initialization(dummy_solvisselect_entity):
    select_entity = dummy_solvisselect_entity()
    assert select_entity is not None
    assert select_entity._host == "test_host"
    assert select_entity._response_key == "Test Entity"
    assert select_entity.entity_registry_enabled_default is True
    assert select_entity.device_info is not None
    assert select_entity.supported_version == 1
    assert select_entity.unique_id == "1_1_Test_Entity"
    assert select_entity._attr_options == ("Option 1", "Option 2")
    assert select_entity.data_processing == 0
    assert select_entity.modbus_address == 1


def test_select_translation_key(dummy_solvisselect_entity):
    """Test correct setting of translation_key."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    assert select_entity.translation_key == "Test Entity"


# # # Tests for select_option # # #


@pytest.mark.asyncio
async def test_async_select_option(dummy_solvisselect_entity):
    select_entity = dummy_solvisselect_entity(name="Test Entity", modbus_address=1)
    select_entity._response_key = "Test Entity"
    response_mock = MagicMock()
    response_mock.isError.return_value = False
    select_entity.coordinator.modbus.write_register = AsyncMock(return_value=response_mock)
    await select_entity.async_select_option("1")
    select_entity.coordinator.modbus.write_register.assert_awaited_once_with(1, 1, slave=1)


@pytest.mark.asyncio
async def test_async_select_option_connection_exception(dummy_solvisselect_entity):
    """Test handling of a ConnectionException during modbus.write_register."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", modbus_address=1, entity_id="select.test")
    select_entity.coordinator.modbus.write_register = AsyncMock(side_effect=ConnectionException)
    await select_entity.async_select_option("1")
    select_entity.coordinator.modbus.write_register.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_select_option_modbus_failure(dummy_solvisselect_entity):
    """Test async_select_option failure due to error in modbus.write_register."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", modbus_address=1, entity_id="select.test")
    select_entity.coordinator.modbus.connect = AsyncMock(return_value=False)
    error_response = MagicMock()
    error_response.isError.return_value = True
    select_entity.coordinator.modbus.write_register = AsyncMock(return_value=error_response)
    with patch("custom_components.solvis_control.select._LOGGER.error") as mock_logger:
        await select_entity.async_select_option("1")
        mock_logger.assert_called_with("[Test Entity] Failed to send option 1 to register 1")


@pytest.mark.asyncio
async def test_async_select_option_invalid_option(hass, mock_coordinator, mock_device_info, dummy_solvisselect_entity, caplog: LogCaptureFixture):
    """Test select_option with invalid (non-integer) input."""
    select_entity = dummy_solvisselect_entity(host="host", name="test", enabled_by_default=True, modbus_address=100, entity_id="select.test")
    with caplog.at_level(logging.WARNING):
        await select_entity.async_select_option("invalid")
    assert "Invalid option selected" in caplog.text


# # # Tests for handle_coordinator_update # # #


def test_handle_coordinator_update(dummy_solvisselect_entity):
    """Test coordinator update handling with valid data."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    # Simulate a valid update from the coordinator.
    select_entity.coordinator.data = {"Test Entity": 2}
    select_entity._handle_coordinator_update()
    # Check that the current option and extra attributes are set correctly.
    assert select_entity._attr_current_option == "2"
    assert select_entity._attr_extra_state_attributes["raw_value"] == 2
    assert select_entity._attr_available is True


def test_handle_coordinator_update_no_data(dummy_solvisselect_entity):
    """Test coordinator update when no data is available."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.data = None
    select_entity.hass = MagicMock(loop=MagicMock())
    select_entity._handle_coordinator_update()
    assert select_entity._attr_available is False


def test_handle_coordinator_update_invalid_data(dummy_solvisselect_entity):
    """Test coordinator update when data type is invalid."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.hass = MagicMock()
    select_entity.coordinator.data = {"Test Entity": "invalid_value"}
    select_entity._handle_coordinator_update()
    assert select_entity._attr_available is False


def test_handle_coordinator_update_error_code(dummy_solvisselect_entity):
    """Test coordinator update when response is error code (-300)."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.data = {"Test Entity": -300}
    select_entity._handle_coordinator_update()
    assert select_entity._attr_available is False


def test_handle_coordinator_update_skip_slow_polling(dummy_solvisselect_entity):
    """Test skipping updates for slow polling."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.poll_rate_slow = 30
    register_mock = MagicMock()
    register_mock.poll_rate = 1
    register_mock.poll_time = 10
    with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [register_mock]):
        select_entity._handle_coordinator_update()
    assert select_entity._attr_current_option is None


def test_handle_coordinator_update_skip_standard_polling(dummy_solvisselect_entity):
    """Test skipping updates for standard polling."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.poll_rate_default = 10
    register_mock = MagicMock()
    register_mock.poll_rate = 0
    register_mock.poll_time = 5
    with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [register_mock]):
        select_entity._handle_coordinator_update()
    assert select_entity._attr_current_option is None


def test_handle_coordinator_update_no_matching_register(dummy_solvisselect_entity):
    """Test _handle_coordinator_update when no matching register is found."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    with patch("custom_components.solvis_control.utils.helpers.REGISTERS", []):
        select_entity._handle_coordinator_update()
    assert select_entity._attr_available is False


def test_handle_coordinator_update_missing_poll_rate(dummy_solvisselect_entity):
    """Test _handle_coordinator_update when poll rate is missing."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.poll_rate_slow = 30
    register_mock = MagicMock()
    register_mock.poll_rate = None
    with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [register_mock]):
        select_entity._handle_coordinator_update()
    assert select_entity._attr_available is False


def test_handle_coordinator_update_unexpected_data_type(dummy_solvisselect_entity):
    """Test handling of unexpected data types in coordinator data."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.data = {"Test Entity": {"unexpected": "dict"}}

    with patch("custom_components.solvis_control.utils.helpers._LOGGER.warning") as mock_logger:
        select_entity._handle_coordinator_update()
        mock_logger.assert_called_with("[Test Entity] Invalid response data type from coordinator: {'unexpected': 'dict'} has type <class 'dict'>")


def test_handle_coordinator_update_with_float_value(dummy_solvisselect_entity):
    """Test that float values are correctly processed in _handle_coordinator_update."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.data = {"Test Entity": 12.34}
    select_entity._handle_coordinator_update()
    assert select_entity._attr_current_option == "12.34"
    assert select_entity._attr_extra_state_attributes["raw_value"] == 12.34
    assert select_entity._attr_available is True


def test_handle_coordinator_update_with_complex_value(dummy_solvisselect_entity):
    """Test that complex numbers are correctly rejected in _handle_coordinator_update."""
    select_entity = dummy_solvisselect_entity(name="Test Entity", entity_id="select.test")
    select_entity.coordinator.data = {"Test Entity": complex(2, 3)}
    with patch("custom_components.solvis_control.utils.helpers._LOGGER.warning") as mock_logger:
        select_entity._handle_coordinator_update()
        mock_logger.assert_called_with("[Test Entity] Invalid response data type from coordinator: (2+3j) has type <class 'complex'>")
        assert select_entity._attr_available is False


def test_handle_coordinator_update_missing_key(hass, mock_coordinator, mock_device_info, dummy_solvisselect_entity):
    """Test handling coordinator update with missing response key."""
    select_entity = dummy_solvisselect_entity(host="host", name="missing_key", enabled_by_default=True, entity_id="select.missing_key")
    mock_coordinator.data = {"other_key": 123}
    select_entity._handle_coordinator_update()
    assert select_entity._attr_available is False


# # # Tests for select_options # # #


def test_select_options(dummy_solvisselect_entity):
    """Test that options are correctly assigned."""
    select_entity = dummy_solvisselect_entity()
    assert select_entity._attr_options == ("Option 1", "Option 2")


def test_select_options_none(dummy_solvisselect_entity):
    """Test that options default to an empty list when None is passed."""
    select_entity = dummy_solvisselect_entity(options=None)
    assert select_entity._attr_options == []


# # # Tests for unique_id # # #


def test_select_unique_id(dummy_solvisselect_entity):
    """Test that unique_id is generated correctly."""
    select_entity = dummy_solvisselect_entity()
    assert select_entity.unique_id == "1_1_Test_Entity"


def test_select_unique_id_special_chars(dummy_solvisselect_entity):
    """Test unique_id generation with special characters in name."""
    select_entity = dummy_solvisselect_entity(name="Test! Entity@#")
    assert select_entity.unique_id == "1_1_Test_Entity"


def test_select_unique_id_all_special_chars(dummy_solvisselect_entity):
    """Test unique_id with name having only special chars."""
    entity = dummy_solvisselect_entity(name="!@#$%^&*()", supported_version=2)
    assert entity.unique_id == "1_2"


# # # Tests for setup_entry


@pytest.mark.asyncio
async def test_select_async_setup_entry_entity_removal_exception(hass, mock_config_entry):
    """Test exception handling during entity removal."""
    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
    with (
        patch("homeassistant.helpers.entity_registry.async_get", side_effect=Exception("Test Exception")),
        patch("custom_components.solvis_control.utils.helpers.generate_device_info"),
        patch("custom_components.solvis_control.utils.helpers.REGISTERS", []),
        patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_log_error,
    ):
        mock_add_entities = MagicMock()
        await async_setup_entry(hass, mock_config_entry, mock_add_entities)
        mock_log_error.assert_called_with("Error removing old entities: Test Exception", exc_info=True)
        mock_add_entities.assert_called()


@pytest.mark.asyncio
async def test_select_async_setup_entry_no_host(hass, mock_config_entry):
    """Test setup entry when no host is provided."""
    mock_config_entry.data.pop(CONF_HOST, None)
    with patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger:
        hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
        await async_setup_entry(hass, mock_config_entry, AsyncMock())
        mock_logger.assert_called_with("Device has no address")


@pytest.mark.asyncio
async def test_select_async_setup_entry_skips_sc2_entity_on_sc3_device(hass, mock_config_entry):
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
    with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [mock_register]):
        with patch("custom_components.solvis_control.utils.helpers._LOGGER.debug") as mock_logger:
            await async_setup_entry(hass, mock_config_entry, MagicMock())
            mock_logger.assert_any_call("[test_entity_sc2 | 123] Skipping SC2 entity for SC3 device.")


@pytest.mark.asyncio
async def test_select_async_setup_entry_existing_entities_handling(hass, mock_config_entry):
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
        with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [mock_register1, mock_register2]):
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
