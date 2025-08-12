"""
Tests for Solvis Sensor Entity

Version: v2.1.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from custom_components.solvis_control.sensor import SolvisSensor, async_setup_entry, _LOGGER, SolvisDerivativeSensor
from custom_components.solvis_control.const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, ModbusFieldConfig, CONF_OPTION_13, STORAGE_TYPE_CONFIG
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
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
async def test_handle_coordinator_update_not_available_extra_attrs(mock_solvis_sensor):
    """Test that when coordinator data is not available, extra state attributes are set to an empty dict."""
    mock_solvis_sensor.hass = MagicMock()
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(False, None, {"raw_value": None})):
        mock_solvis_sensor._handle_coordinator_update()
    assert mock_solvis_sensor._attr_extra_state_attributes == {}

class DummyConfigEntry:
    def __init__(self, data):
        self.data = data
        self.options = {}


def test_compute_stored_energy_12_valid(monkeypatch, mock_coordinator):
    storage_type = next(iter(STORAGE_TYPE_CONFIG.keys()))
    cfg_entry = DummyConfigEntry({CONF_OPTION_13: storage_type})

    t1, t2, t3, t4 = 20.0, 22.0, 24.0, 26.0

    v1, v2, v3 = STORAGE_TYPE_CONFIG[storage_type]["volumes"]
    rho = 1.0
    c = 4.186
    t_zone1 = (t1 + t2) / 2  # 21.0
    t_zone2 = (t2 + t3) / 2  # 23.0
    t_zone3 = (t3 + t4) / 2  # 25.0
    e1 = v1 * rho * c * (t_zone1 - 12)
    e2 = v2 * rho * c * (t_zone2 - 12)
    e3 = v3 * rho * c * (t_zone3 - 12)
    expected_kwh = (e1 + e2 + e3) / 3600

    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})
    sensor = SolvisDerivativeSensor(
        coordinator=mock_coordinator,
        device_info=dummy_device_info,
        host="dummy_host",
        name="test_energy",
        source_keys=["warm1", "warm2", "warm3", "warm4"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=2,
        compute_mode="stored_energy_12",
        config_entry=cfg_entry,
    )

    mock_coordinator.data = {
        "warm1": t1,
        "warm2": t2,
        "warm3": t3,
        "warm4": t4,
    }

    result = sensor._compute_stored_energy_12([t1, t2, t3, t4])

    assert pytest.approx(result, rel=1e-6) == expected_kwh


def test_compute_stored_energy_12_invalid_type(monkeypatch, mock_coordinator):
    cfg_entry = DummyConfigEntry({})

    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})
    sensor = SolvisDerivativeSensor(
        coordinator=mock_coordinator,
        device_info=dummy_device_info,
        host="dummy",
        name="test_energy",
        source_keys=["a", "b", "c", "d"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=2,
        compute_mode="stored_energy_12",
        config_entry=cfg_entry,
    )

    result = sensor._compute_stored_energy_12([1, 2, 3, 4])
    assert result == 0.0

    cfg_entry_bad = DummyConfigEntry({CONF_OPTION_13: "NichtExistierend"})
    sensor_bad = SolvisDerivativeSensor(
        coordinator=mock_coordinator,
        device_info=dummy_device_info,
        host="dummy",
        name="test_bad",
        source_keys=["a", "b", "c", "d"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=2,
        compute_mode="stored_energy_12",
        config_entry=cfg_entry_bad,
    )
    result_bad = sensor_bad._compute_stored_energy_12([1, 2, 3, 4])
    assert result_bad == 0.0


def test_compute_combined_fallback(monkeypatch, mock_coordinator):
    dummy_entry = DummyConfigEntry({CONF_OPTION_13: next(iter(STORAGE_TYPE_CONFIG.keys()))})
    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})

    sensor = SolvisDerivativeSensor(
        coordinator=mock_coordinator,
        device_info=dummy_device_info,
        host="h",
        name="c",
        source_keys=["x", "y"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=2,
        compute_mode=None,
        config_entry=dummy_entry,
    )

    mock_coordinator.data = {"x": 2.5, "y": 3.5}
    result = sensor._compute_combined()
    assert result == 6.0


def test_compute_combined_missing_key(monkeypatch, mock_coordinator):
    dummy_entry = DummyConfigEntry({CONF_OPTION_13: next(iter(STORAGE_TYPE_CONFIG.keys()))})
    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})
    sensor = SolvisDerivativeSensor(
        coordinator=mock_coordinator,
        device_info=dummy_device_info,
        host="h",
        name="c",
        source_keys=["x", "z"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=2,
        compute_mode=None,
        config_entry=dummy_entry,
    )

    mock_coordinator.data = {"x": 2.5}
    result = sensor._compute_combined()
    assert result is None


@pytest.mark.asyncio
async def test_async_update_from_coordinator_sets_value(monkeypatch):
    storage_type = next(iter(STORAGE_TYPE_CONFIG.keys()))
    cfg_entry = DummyConfigEntry({CONF_OPTION_13: storage_type})

    coord = SolvisModbusCoordinator.__new__(SolvisModbusCoordinator)
    coord.supported_version = None
    coord.async_add_listener = lambda _callback: None
    coord.data = {
        "t1": 20.0,
        "t2": 22.0,
        "t3": 24.0,
        "t4": 26.0,
    }

    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})
    sensor = SolvisDerivativeSensor(
        coordinator=coord,
        device_info=dummy_device_info,
        host="h",
        name="c",
        source_keys=["t1", "t2", "t3", "t4"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=3,
        compute_mode="stored_energy_12",
        config_entry=cfg_entry,
    )
    sensor.hass = MagicMock()
    sensor.async_write_ha_state = lambda: None

    assert sensor._attr_native_value is None

    sensor._async_update_from_coordinator()

    expected_raw = {
        "t1": 20.0,
        "t2": 22.0,
        "t3": 24.0,
        "t4": 26.0,
    }
    assert isinstance(sensor._attr_native_value, float)
    assert "raw_values" in sensor._attr_extra_state_attributes
    assert sensor._attr_extra_state_attributes["raw_values"] == expected_raw


@pytest.mark.asyncio
async def test_async_update_from_coordinator_missing(monkeypatch):
    storage_type = next(iter(STORAGE_TYPE_CONFIG.keys()))
    cfg_entry = DummyConfigEntry({CONF_OPTION_13: storage_type})

    coord = SolvisModbusCoordinator.__new__(SolvisModbusCoordinator)
    coord.supported_version = None
    coord.async_add_listener = lambda _callback: None
    coord.data = {"t1": 20.0}

    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})
    sensor = SolvisDerivativeSensor(
        coordinator=coord,
        device_info=dummy_device_info,
        host="h",
        name="c",
        source_keys=["t1", "t2", "t3", "t4"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=3,
        compute_mode="stored_energy_12",
        config_entry=cfg_entry,
    )
    sensor.hass = MagicMock()
    sensor.async_write_ha_state = lambda: None

    sensor._attr_native_value = 99.9
    sensor._attr_extra_state_attributes = {"foo": "bar"}

    sensor._async_update_from_coordinator()
    assert sensor._attr_native_value is None
    assert sensor._attr_extra_state_attributes == {}


def test_handle_coordinator_update_noop(monkeypatch, mock_coordinator):
    storage_type = next(iter(STORAGE_TYPE_CONFIG.keys()))
    cfg_entry = DummyConfigEntry({CONF_OPTION_13: storage_type})

    coord = mock_coordinator
    coord.data = {"any": 1.0}

    dummy_device_info = DeviceInfo(identifiers={("solvis", "dummy")})
    sensor = SolvisDerivativeSensor(
        coordinator=coord,
        device_info=dummy_device_info,
        host="h",
        name="c",
        source_keys=["any"],
        unit="kWh",
        device_class=None,
        state_class=None,
        entity_category=None,
        suggested_display_precision=2,
        compute_mode=None,
        config_entry=cfg_entry,
    )

    sensor._attr_native_value = 42.0
    sensor._attr_extra_state_attributes = {"foo": "bar"}

    sensor._handle_coordinator_update()

    assert sensor._attr_native_value == 42.0
    assert sensor._attr_extra_state_attributes == {"foo": "bar"}