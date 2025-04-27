"""
Tests for Solvis Binary Sensor Entity

Version: v2.0.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant
from custom_components.solvis_control.binary_sensor import SolvisBinarySensor, async_setup_entry, _LOGGER
from custom_components.solvis_control.const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, POLL_RATE_DEFAULT, POLL_RATE_SLOW, ModbusFieldConfig
from homeassistant.helpers.device_registry import DeviceInfo


@pytest.fixture
def mock_solvis_binary_sensor(mock_coordinator, mock_device_info):
    """Fixture returning a preconfigured SolvisBinarySensor instance."""
    sensor = SolvisBinarySensor(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="Test Binary Sensor",
        device_class="",
        state_class="",
        entity_category=None,
        enabled_by_default=True,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
        modbus_address=1,
    )
    return sensor


def test_sensor_initialization(mock_solvis_binary_sensor):
    """Test initialization of the binary sensor entity."""
    assert mock_solvis_binary_sensor is not None
    assert mock_solvis_binary_sensor._host == "test_host"
    assert mock_solvis_binary_sensor._response_key == "Test Binary Sensor"
    assert mock_solvis_binary_sensor.entity_registry_enabled_default is True
    assert mock_solvis_binary_sensor.device_info is not None
    assert mock_solvis_binary_sensor.supported_version == 1
    assert mock_solvis_binary_sensor.unique_id == "1_1_Test_Binary_Sensor"


@pytest.mark.asyncio
async def test_handle_coordinator_update_valid_on(mock_solvis_binary_sensor):
    """Test update when binary sensor should be on."""
    mock_solvis_binary_sensor.hass = MagicMock()

    # Simulate a valid update value causing sensor to be on
    mock_solvis_binary_sensor.coordinator.data = {"Test Binary Sensor": 1}
    mock_solvis_binary_sensor.data_processing = 0
    mock_solvis_binary_sensor._handle_coordinator_update()
    assert mock_solvis_binary_sensor._attr_is_on is True
    assert mock_solvis_binary_sensor._attr_extra_state_attributes["unprocessed_value"] == 1


@pytest.mark.asyncio
async def test_handle_coordinator_update_valid_off(mock_solvis_binary_sensor):
    """Test update when binary sensor should be off."""
    mock_solvis_binary_sensor.hass = MagicMock()
    mock_solvis_binary_sensor.coordinator.data = {"Test Binary Sensor": 0}
    mock_solvis_binary_sensor.data_processing = 0
    mock_solvis_binary_sensor._handle_coordinator_update()

    assert mock_solvis_binary_sensor._attr_is_on is False
    assert mock_solvis_binary_sensor._attr_extra_state_attributes["unprocessed_value"] == 0


@pytest.mark.asyncio
async def test_handle_coordinator_update_invalid_data(mock_solvis_binary_sensor):
    """Test update when coordinator data type is invalid."""
    mock_solvis_binary_sensor.hass = MagicMock()
    mock_solvis_binary_sensor.coordinator.data = {"Test Binary Sensor": {"unexpected": "dict"}}

    with patch("custom_components.solvis_control.utils.helpers._LOGGER.warning") as mock_logger:
        mock_solvis_binary_sensor._handle_coordinator_update()
        mock_logger.assert_called()
    assert mock_solvis_binary_sensor._attr_available is False


@pytest.mark.asyncio
async def test_handle_coordinator_update_diagnostic_bits(mock_solvis_binary_sensor):
    """Test diagnostic bit extraction for binary sensor (data_processing == 4)"""
    mock_solvis_binary_sensor.hass = MagicMock()
    mock_solvis_binary_sensor.data_processing = 4
    # Set a test value so that first_9_bits becomes 170 ("010101010")
    test_value = 170 << 8  # 43520
    mock_solvis_binary_sensor.coordinator.data = {"Test Binary Sensor": test_value}
    with patch("custom_components.solvis_control.binary_sensor._LOGGER.debug") as mock_debug:
        mock_solvis_binary_sensor._handle_coordinator_update()
        # Expected debug message format: "[Test Binary Sensor] Successfully updated value: True (Raw: 43520)"
        expected_debug = f"[Test Binary Sensor] Successfully updated value: True (Raw: {test_value})"
        mock_debug.assert_called_with(expected_debug)
    # Additional assertions on diagnostic extraction
    expected_first_9_bits = "010101010"
    expected_error_attributes = {
        "sicherung_netzbaugruppe": False,
        "brennerfehler": True,
        "stb1_fehler": False,
        "stb2_fehler": True,
        "brenner_cm424": False,
        "solardruck": True,
        "unbekannt": False,
        "anlagendruck": True,
        "kondensat": False,
    }
    expected_error_count = sum(expected_error_attributes.values())
    assert mock_solvis_binary_sensor._attr_is_on is True
    extra_attrs = mock_solvis_binary_sensor._attr_extra_state_attributes
    assert extra_attrs["unprocessed_value"] == test_value
    assert extra_attrs["error_count"] == expected_error_count
    assert extra_attrs["first_9_bits"] == expected_first_9_bits
    for key, expected in expected_error_attributes.items():
        assert key in extra_attrs
        assert extra_attrs[key] is expected


@pytest.mark.asyncio
async def test_handle_coordinator_update_diagnostic_bits_none(mock_solvis_binary_sensor):
    """Test diagnostic bit extraction for binary sensor (data_processing == 4) when no bits are set."""
    mock_solvis_binary_sensor.hass = MagicMock()
    mock_solvis_binary_sensor.data_processing = 4
    # Set a test value so that first_9_bits becomes 0 ("000000000")
    test_value = 0  # Equivalent to 0 << 8
    mock_solvis_binary_sensor.coordinator.data = {"Test Binary Sensor": test_value}
    with patch("custom_components.solvis_control.binary_sensor._LOGGER.debug") as mock_debug:
        mock_solvis_binary_sensor._handle_coordinator_update()
        expected_debug = f"[Test Binary Sensor] Successfully updated value: False (Raw: {test_value})"
        mock_debug.assert_called_with(expected_debug)
    expected_first_9_bits = "000000000"
    expected_error_attributes = {
        "sicherung_netzbaugruppe": False,
        "brennerfehler": False,
        "stb1_fehler": False,
        "stb2_fehler": False,
        "brenner_cm424": False,
        "solardruck": False,
        "unbekannt": False,
        "anlagendruck": False,
        "kondensat": False,
    }
    expected_error_count = sum(expected_error_attributes.values())  # 0
    assert mock_solvis_binary_sensor._attr_is_on is False
    extra_attrs = mock_solvis_binary_sensor._attr_extra_state_attributes
    assert extra_attrs["unprocessed_value"] == test_value
    assert extra_attrs["error_count"] == expected_error_count
    assert extra_attrs["first_9_bits"] == expected_first_9_bits
    for key in expected_error_attributes:
        if key in extra_attrs:
            assert extra_attrs[key] is False


@pytest.mark.asyncio
async def test_handle_coordinator_update_no_data(mock_solvis_binary_sensor):
    """Test update when no coordinator data is available."""
    mock_solvis_binary_sensor.hass = MagicMock(loop=MagicMock())
    mock_solvis_binary_sensor.coordinator.data = None
    mock_solvis_binary_sensor._handle_coordinator_update()

    assert mock_solvis_binary_sensor._attr_available is False


@pytest.mark.asyncio
async def test_async_setup_entry_no_host_binary_sensor(hass, mock_config_entry):
    """Test setup entry when no host is provided for binary sensor."""
    mock_config_entry.data.pop(CONF_HOST, None)
    with patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger:
        hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
        await async_setup_entry(hass, mock_config_entry, AsyncMock())
        mock_logger.assert_called_with("Device has no address")


@pytest.mark.asyncio
async def test_async_setup_entry_binary_sensor_entity_removal_exception(hass, mock_config_entry):
    """Test exception handling during entity removal for binary sensor."""
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
async def test_async_setup_entry_binary_sensor_existing_entities_handling(hass, mock_config_entry):
    """Test removal of existing binary sensor entities during setup."""
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
        input_type=4,
        conf_option=0,
        supported_version=0,
    )
    register2 = ModbusFieldConfig(
        name="new_sensor_2",
        address=200,
        unit=None,
        device_class=None,
        state_class=None,
        input_type=4,
        conf_option=0,
        supported_version=0,
    )

    with patch("homeassistant.helpers.entity_registry.async_get", return_value=mock_entity_registry):
        with patch("custom_components.solvis_control.utils.helpers.REGISTERS", [register1, register2]):
            with patch("custom_components.solvis_control.utils.helpers.async_resolve_entity_id") as mock_resolve:
                with patch("custom_components.solvis_control.utils.helpers._LOGGER.debug") as mock_log_debug:
                    # Mock async_resolve_entity_id()
                    mock_resolve.side_effect = lambda reg, uid: f"sensor_{uid[-1]}"
                    await async_setup_entry(hass, mock_config_entry, MagicMock())
                    mock_entity_registry.async_remove.assert_any_call("sensor_1")
                    mock_entity_registry.async_remove.assert_any_call("sensor_2")
                    assert mock_entity_registry.async_remove.call_count == 2
                    mock_log_debug.assert_any_call("Removed old entity: old_1 (entity_id: sensor_1)")
                    mock_log_debug.assert_any_call("Removed old entity: old_2 (entity_id: sensor_2)")
