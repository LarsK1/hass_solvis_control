"""
Tests for Solvis Sensor Entity

Version: v2.0.0-beta.1
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
async def test_handle_coordinator_update_version_processing_valid(mock_solvis_sensor):
    """Test _handle_coordinator_update for version processing (data_processing == 1) with valid 5-digit value."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    test_value = 32016
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})) as proc_patch:
        mock_solvis_sensor._handle_coordinator_update()
        proc_patch.assert_called_with(mock_solvis_sensor.coordinator.data, "Test Number Sensor")
    assert mock_solvis_sensor._attr_native_value == "3.20.16"


@pytest.mark.asyncio
async def test_handle_coordinator_update_version_processing_invalid_length(mock_solvis_sensor):
    """Test _handle_coordinator_update for version processing (data_processing == 1) with invalid length value."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    test_value = 1234  # Length is 4, invalid
    with patch("custom_components.solvis_control.sensor._LOGGER.warning") as mock_warning:
        with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
            mock_solvis_sensor._handle_coordinator_update()
            mock_warning.assert_called_with("Couldn't process version string to Version.")
    assert mock_solvis_sensor._attr_native_value == test_value


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


@pytest.mark.asyncio
async def test_async_setup_entry_existing_entities_handling_sensor(hass, mock_config_entry):
    """Test removal of existing sensor entities during setup."""
    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
    mock_entity_registry = MagicMock()
    mock_entity_registry.entities = {
        "sensor_1": MagicMock(unique_id="old_1", entity_id="sensor_1", config_entry_id=mock_config_entry.entry_id),
        "sensor_2": MagicMock(unique_id="old_2", entity_id="sensor_2", config_entry_id=mock_config_entry.entry_id),
    }
    mock_entity_registry.async_remove = MagicMock()
    register1 = ModbusFieldConfig(
        name="new_sensor_1",
        address=100,
        unit=None,
        device_class=None,
        state_class=None,
        input_type=0,
        conf_option=0,
        supported_version=0,
        suggested_precision=2,
    )
    register2 = ModbusFieldConfig(
        name="new_sensor_2",
        address=200,
        unit=None,
        device_class=None,
        state_class=None,
        input_type=0,
        conf_option=0,
        supported_version=0,
        suggested_precision=2,
    )
    with patch("homeassistant.helpers.entity_registry.async_get", return_value=mock_entity_registry):
        with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [register1, register2]):
            with patch("custom_components.solvis_control.utils.helpers.async_resolve_entity_id") as mock_resolve:
                with patch("custom_components.solvis_control.utils.helpers._LOGGER.debug") as mock_log_debug:
                    mock_resolve.side_effect = lambda reg, uid: f"sensor_{uid[-1]}"
                    await async_setup_entry(hass, mock_config_entry, MagicMock())
                    mock_entity_registry.async_remove.assert_any_call("sensor_1")
                    mock_entity_registry.async_remove.assert_any_call("sensor_2")
                    assert mock_entity_registry.async_remove.call_count == 2
                    mock_log_debug.assert_any_call("Removed old entity: old_1 (entity_id: sensor_1)")
                    mock_log_debug.assert_any_call("Removed old entity: old_2 (entity_id: sensor_2)")


@pytest.mark.asyncio
async def test_handle_coordinator_update_version_processing_sw_update_issue(mock_solvis_sensor):
    """Test version processing branch for modbus_address 32770 with sw_version not equal to '3.20.16'."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    mock_solvis_sensor.modbus_address = 32770
    # Use a test value that converts to "3.21.16" (not equal to "3.20.16")
    test_value = 32116  # "3.21.16"
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        fake_device = MagicMock()
        fake_device.id = "device123"
        fake_registry = MagicMock()
        fake_registry.async_get_device.return_value = fake_device
        fake_registry.async_update_device = MagicMock()
        with patch("custom_components.solvis_control.sensor.dr.async_get", return_value=fake_registry):
            with patch("custom_components.solvis_control.sensor.ir.async_create_issue") as create_issue_patch:
                mock_solvis_sensor._handle_coordinator_update()
                fake_registry.async_update_device.assert_called_with("device123", sw_version="3.21.16")
                create_issue_patch.assert_called_with(
                    mock_solvis_sensor.hass,
                    DOMAIN,
                    "software_update",
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="software_update",
                )


@pytest.mark.asyncio
async def test_handle_coordinator_update_version_processing_hw_update(mock_solvis_sensor):
    """Test version processing branch for modbus_address 32771."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    mock_solvis_sensor.modbus_address = 32771
    # Use a test value that converts to "3.20.16"
    test_value = 32016  # "3.20.16"
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        fake_device = MagicMock()
        fake_device.id = "device456"
        fake_registry = MagicMock()
        fake_registry.async_get_device.return_value = fake_device
        fake_registry.async_update_device = MagicMock()
        with patch("custom_components.solvis_control.sensor.dr.async_get", return_value=fake_registry):
            mock_solvis_sensor._handle_coordinator_update()
            fake_registry.async_update_device.assert_called_with("device456", hw_version="3.20.16")


@pytest.mark.asyncio
async def test_handle_coordinator_update_not_available_extra_attrs(mock_solvis_sensor):
    """Test that when coordinator data is not available, extra state attributes are set to an empty dict."""
    mock_solvis_sensor.hass = MagicMock()
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(False, None, {"raw_value": None})):
        mock_solvis_sensor._handle_coordinator_update()
    assert mock_solvis_sensor._attr_extra_state_attributes == {}


@pytest.mark.asyncio
async def test_handle_coordinator_update_version_sw_equal(mock_solvis_sensor):
    """Test version processing for modbus_address 32770 with sw_version equal to '3.20.16'."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    mock_solvis_sensor.modbus_address = 32770
    test_value = 32016  # yields "3.20.16"
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        fake_device = MagicMock()
        fake_device.id = "device123"
        fake_registry = MagicMock()
        fake_registry.async_get_device.return_value = fake_device
        fake_registry.async_update_device = MagicMock()
        with patch("custom_components.solvis_control.sensor.dr.async_get", return_value=fake_registry):
            with patch("custom_components.solvis_control.sensor.ir.async_create_issue") as create_issue_patch:
                with patch("custom_components.solvis_control.sensor._LOGGER.debug") as debug_patch:
                    mock_solvis_sensor._handle_coordinator_update()
                    fake_registry.async_update_device.assert_called_with("device123", sw_version="3.20.16")
                    create_issue_patch.assert_not_called()
                    expected_debug = f"[{mock_solvis_sensor._response_key}] Successfully updated native value: 3.20.16 (Raw: {test_value})"
                    debug_patch.assert_called_with(expected_debug)


@pytest.mark.asyncio
async def test_handle_coordinator_update_version_sw_not_equal(mock_solvis_sensor):
    """Test version processing for modbus_address 32770 with sw_version not equal to '3.20.16'."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    mock_solvis_sensor.modbus_address = 32770
    test_value = 32116  # yields "3.21.16"
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        fake_device = MagicMock()
        fake_device.id = "device123"
        fake_registry = MagicMock()
        fake_registry.async_get_device.return_value = fake_device
        fake_registry.async_update_device = MagicMock()
        with patch("custom_components.solvis_control.sensor.dr.async_get", return_value=fake_registry):
            with patch("custom_components.solvis_control.sensor.ir.async_create_issue") as create_issue_patch:
                with patch("custom_components.solvis_control.sensor._LOGGER.debug") as debug_patch:
                    mock_solvis_sensor._handle_coordinator_update()
                    fake_registry.async_update_device.assert_called_with("device123", sw_version="3.21.16")
                    create_issue_patch.assert_called_with(
                        mock_solvis_sensor.hass,
                        DOMAIN,
                        "software_update",
                        is_fixable=False,
                        severity=ir.IssueSeverity.WARNING,
                        translation_key="software_update",
                    )
                    expected_debug = f"[{mock_solvis_sensor._response_key}] Successfully updated native value: 3.21.16 (Raw: {test_value})"
                    debug_patch.assert_called_with(expected_debug)


@pytest.mark.asyncio
async def test_handle_coordinator_update_hw_update(mock_solvis_sensor):
    """Test version processing for modbus_address 32771 updating hw_version."""
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    mock_solvis_sensor.modbus_address = 32771
    test_value = 32016  # yields "3.20.16"
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        fake_device = MagicMock()
        fake_device.id = "device456"
        fake_registry = MagicMock()
        fake_registry.async_get_device.return_value = fake_device
        fake_registry.async_update_device = MagicMock()
        with patch("custom_components.solvis_control.sensor.dr.async_get", return_value=fake_registry):
            with patch("custom_components.solvis_control.sensor._LOGGER.debug") as debug_patch:
                mock_solvis_sensor._handle_coordinator_update()
                fake_registry.async_update_device.assert_called_with("device456", hw_version="3.20.16")
                expected_debug = f"[{mock_solvis_sensor._response_key}] Successfully updated native value: 3.20.16 (Raw: {test_value})"
                debug_patch.assert_called_with(expected_debug)


@pytest.mark.asyncio
async def test_handle_coordinator_update_device_none_sensor(mock_solvis_sensor):
    """Test version processing when device is None for sensor (modbus_address 32770).
    Verify that the debug log message is called even when no device is found.
    """
    mock_solvis_sensor.hass = MagicMock()
    mock_solvis_sensor.data_processing = 1
    mock_solvis_sensor.modbus_address = 32770
    test_value = 32016  # Expected to yield "3.20.16"
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {"raw_value": test_value})):
        fake_registry = MagicMock()
        fake_registry.async_get_device.return_value = None  # Device is None
        with patch("custom_components.solvis_control.sensor.dr.async_get", return_value=fake_registry):
            with patch("custom_components.solvis_control.sensor._LOGGER.debug") as debug_patch:
                mock_solvis_sensor._handle_coordinator_update()
                expected_debug = f"[{mock_solvis_sensor._response_key}] Successfully updated native value: 3.20.16 (Raw: {test_value})"
                debug_patch.assert_called_with(expected_debug)
