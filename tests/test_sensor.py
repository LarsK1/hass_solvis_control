"""
Tests for Solvis Sensor Entity

Version: v2.0.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from custom_components.solvis_control.sensor import SolvisSensor, async_setup_entry, _LOGGER
from custom_components.solvis_control.const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, ModbusFieldConfig
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import issue_registry as ir


def test_sensor_initialization(mock_solvis_sensor):
    """Test initialization of the sensor entity."""
    assert mock_solvis_sensor is not None
    assert mock_solvis_sensor._host == "test_host"
    assert mock_solvis_sensor._response_key == "Test Number Sensor"
    assert mock_solvis_sensor.native_unit_of_measurement == "°C"
    assert mock_solvis_sensor.device_class == "temperature"
    assert mock_solvis_sensor.state_class == "measurement"
    assert mock_solvis_sensor.suggested_display_precision == 2
    assert mock_solvis_sensor.unique_id == "1_1_Test_Number_Sensor"


@pytest.mark.asyncio
async def test_handle_coordinator_update_case2_nonzero(mock_solvis_sensor):
    """Test _handle_coordinator_update for case 2 (data_processing == 2) with nonzero value."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 2
    test_value = 30
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        mock_solvis_sensor._handle_coordinator_update()
    expected = (1 / (test_value / 60)) * 1000 / 2 / 42
    assert pytest.approx(mock_solvis_sensor._attr_native_value, rel=1e-2) == expected


@pytest.mark.asyncio
async def test_handle_coordinator_update_case2_zero(mock_solvis_sensor):
    """Test _handle_coordinator_update for case 2 (data_processing == 2) with zero value."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 2
    test_value = 0
    with patch("custom_components.solvis_control.sensor._LOGGER.debug") as mock_warning:
        with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
            mock_solvis_sensor._handle_coordinator_update()
            mock_warning.assert_any_call(f"Division by zero for {mock_solvis_sensor._response_key} with value {test_value}")
    assert mock_solvis_sensor._attr_native_value == test_value


@pytest.mark.asyncio
async def test_handle_coordinator_update_case3_nonzero(mock_solvis_sensor):
    """Test _handle_coordinator_update for case 3 (data_processing == 3) with nonzero value."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 3
    test_value = 30
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        mock_solvis_sensor._handle_coordinator_update()
    expected = (1 / (test_value / 60)) * 1000 / 42
    assert pytest.approx(mock_solvis_sensor._attr_native_value, rel=1e-2) == expected


@pytest.mark.asyncio
async def test_handle_coordinator_update_case3_zero(mock_solvis_sensor):
    """Test _handle_coordinator_update for case 3 (data_processing == 3) with zero value."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 3
    test_value = 0
    with patch("custom_components.solvis_control.sensor._LOGGER.debug") as mock_warning:
        with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
            mock_solvis_sensor._handle_coordinator_update()
            mock_warning.assert_any_call(f"Division by zero for {mock_solvis_sensor._response_key} with value {test_value}")
    assert mock_solvis_sensor._attr_native_value == test_value


@pytest.mark.asyncio
async def test_handle_coordinator_update_default(mock_solvis_sensor):
    """Test _handle_coordinator_update default branch when data_processing is not 1,2,3."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 99
    test_value = 123
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        mock_solvis_sensor._handle_coordinator_update()
    assert mock_solvis_sensor._attr_native_value == test_value


@pytest.mark.asyncio
async def test_async_setup_entry_no_host_sensor(hass, mock_config_entry):
    """Test setup entry when no host is provided for sensor."""
    mock_config_entry.data.pop(CONF_HOST, None)
    with patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger:
        hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
        await async_setup_entry(hass, mock_config_entry, AsyncMock())
        mock_logger.assert_called_with("Device has no address")


@pytest.mark.asyncio
async def test_async_setup_entry_entity_removal_exception_sensor(hass, mock_config_entry):
    """Test exception handling during removal of old sensor entities."""
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
        mock_add_entities.assert_called()


