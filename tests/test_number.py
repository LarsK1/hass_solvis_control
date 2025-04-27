"""
Tests for Solvis Number Entity

Version: v2.0.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from custom_components.solvis_control.number import SolvisNumber, async_setup_entry, _LOGGER
from custom_components.solvis_control.const import CONF_HOST, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, ModbusFieldConfig
from homeassistant.helpers.device_registry import DeviceInfo


@pytest.fixture
def mock_solvis_number(mock_coordinator, mock_device_info):
    """Fixture returning a preconfigured SolvisNumber instance."""
    return SolvisNumber(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="Test Number Sensor",
        unit_of_measurement="°C",
        device_class="temperature",
        state_class="measurement",
        enabled_by_default=True,
        range_data=(0, 100),
        step_size=0.5,
        modbus_address=1,
        multiplier=2.0,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )


def test_number_initialization(mock_solvis_number):
    """Test initialization of the number sensor entity."""
    assert mock_solvis_number is not None
    assert mock_solvis_number._host == "test_host"
    assert mock_solvis_number._response_key == "Test Number Sensor"
    assert mock_solvis_number.native_unit_of_measurement == "°C"
    assert mock_solvis_number.device_class == "temperature"
    assert mock_solvis_number.state_class == "measurement"
    assert mock_solvis_number.native_step == 0.5
    assert mock_solvis_number.native_min_value == 0
    assert mock_solvis_number.native_max_value == 100
    assert mock_solvis_number.unique_id == "1_1_Test_Number_Sensor"


def test_number_initialization_default_step():
    """Test initialization when step_size is None (default native_step)."""
    number_entity = SolvisNumber(
        coordinator=AsyncMock(),
        device_info=MagicMock(),
        host="test_host",
        name="Test Number Default Step",
        unit_of_measurement="°C",
        device_class="",
        state_class="",
        enabled_by_default=True,
        range_data=None,
        step_size=None,
        modbus_address=2,
        multiplier=1.0,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )
    # native_step should default to 1.0 if step_size is not provided
    assert number_entity.native_step == 1.0


@pytest.mark.asyncio
async def test_handle_coordinator_update_valid(mock_solvis_number):
    """Test _handle_coordinator_update when coordinator data is valid."""
    mock_solvis_number.hass = MagicMock()
    # Simulate valid update value: coordinator returns 42
    mock_solvis_number.coordinator.data = {"Test Number Sensor": 42}
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, 42, {"raw_value": 42})) as proc_patch:
        mock_solvis_number._handle_coordinator_update()
        proc_patch.assert_called_with({"Test Number Sensor": 42}, "Test Number Sensor")
    assert mock_solvis_number._attr_native_value == 42
    assert mock_solvis_number._attr_extra_state_attributes["raw_value"] == 42
    assert mock_solvis_number._attr_available is True


@pytest.mark.asyncio
async def test_handle_coordinator_update_not_available(mock_solvis_number):
    """Test _handle_coordinator_update when coordinator data indicates not available."""
    mock_solvis_number.hass = MagicMock()
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(False, None, {})) as proc_patch:
        mock_solvis_number._handle_coordinator_update()
        proc_patch.assert_called_with(mock_solvis_number.coordinator.data, "Test Number Sensor")
    assert mock_solvis_number._attr_extra_state_attributes == {}


@pytest.mark.asyncio
async def test_handle_coordinator_update_no_data(mock_solvis_number):
    """Test _handle_coordinator_update when coordinator data is None."""
    mock_solvis_number.hass = MagicMock(loop=MagicMock())
    mock_solvis_number.coordinator.data = None
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(None, None, {})) as proc_patch:
        mock_solvis_number._handle_coordinator_update()
        proc_patch.assert_called_with(None, "Test Number Sensor")
    assert mock_solvis_number._attr_available is False


@pytest.mark.asyncio
async def test_async_set_native_value_success(mock_solvis_number):
    """Test async_set_native_value when write_modbus_value returns True."""
    mock_solvis_number.hass = MagicMock()
    # With multiplier=2.0, value 10.0 should yield modbus_value = 5
    with patch("custom_components.solvis_control.number.write_modbus_value", new=AsyncMock(return_value=True)) as write_patch:
        await mock_solvis_number.async_set_native_value(10.0)
        write_patch.assert_awaited_once_with(mock_solvis_number.coordinator.modbus, 1, 5, "Test Number Sensor")


@pytest.mark.asyncio
async def test_async_set_native_value_failure(mock_solvis_number):
    """Test async_set_native_value when write_modbus_value returns False."""
    mock_solvis_number.hass = MagicMock()
    with patch("custom_components.solvis_control.number.write_modbus_value", new=AsyncMock(return_value=False)) as write_patch:
        with patch("custom_components.solvis_control.number._LOGGER.error") as log_error:
            await mock_solvis_number.async_set_native_value(10.0)
            write_patch.assert_awaited_once_with(mock_solvis_number.coordinator.modbus, 1, 5, "Test Number Sensor")
            log_error.assert_called_with("[Test Number Sensor] Failed to write value 5 to register 1")


@pytest.mark.asyncio
async def test_async_setup_entry_no_host_number(hass, mock_config_entry):
    """Test setup entry when no host is provided for number sensor."""
    mock_config_entry.data.pop(CONF_HOST, None)
    with patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger:
        hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
        await async_setup_entry(hass, mock_config_entry, AsyncMock())
        mock_logger.assert_called_with("Device has no address")


@pytest.mark.asyncio
async def test_async_setup_entry_entity_removal_exception_number(hass, mock_config_entry):
    """Test exception handling during removal of old number entities."""
    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
    with (
        patch("custom_components.solvis_control.utils.helpers.remove_old_entities", side_effect=Exception("Test Exception")),
        patch("custom_components.solvis_control.utils.helpers.generate_device_info"),
        patch("custom_components.solvis_control.utils.helpers.REGISTERS", []),
        patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger,
    ):
        mock_add_entities = MagicMock()
        await async_setup_entry(hass, mock_config_entry, mock_add_entities)
        mock_logger.assert_called_with("Error removing old entities: Test Exception", exc_info=True)
