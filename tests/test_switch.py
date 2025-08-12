"""
Tests for Solvis Switch Entity

Version: v2.1.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from custom_components.solvis_control.switch import SolvisSwitch, async_setup_entry, _LOGGER
from custom_components.solvis_control.const import CONF_HOST, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, ModbusFieldConfig
from homeassistant.helpers.device_registry import DeviceInfo


@pytest.fixture
def mock_solvis_switch(mock_coordinator, mock_device_info):
    """Fixture returning a preconfigured SolvisSwitch instance."""
    return SolvisSwitch(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_address",
        name="Test Switch",
        enabled_by_default=True,
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
    )


def test_switch_initialization(mock_solvis_switch):
    """Test initialization of the switch entity."""
    assert mock_solvis_switch is not None
    assert mock_solvis_switch._host == "test_address"
    assert mock_solvis_switch._response_key == "Test Switch"
    assert mock_solvis_switch.entity_registry_enabled_default is True
    assert mock_solvis_switch.device_info is not None
    assert mock_solvis_switch.supported_version == 1
    assert mock_solvis_switch.unique_id == "1_1_Test_Switch"


@pytest.mark.asyncio
async def test_handle_coordinator_update_valid(mock_solvis_switch):
    """Test _handle_coordinator_update when coordinator data is valid."""
    mock_solvis_switch.hass = MagicMock()
    # Simulate valid update: coordinator returns 1
    mock_solvis_switch.coordinator.data = {"Test Switch": 1}
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, 1, {"raw_value": 1})) as proc_patch:
        mock_solvis_switch._handle_coordinator_update()
        proc_patch.assert_called_with(mock_solvis_switch.coordinator.data, "Test Switch")
    assert mock_solvis_switch._attr_current_option == "1"
    assert mock_solvis_switch._attr_is_on is True


@pytest.mark.asyncio
async def test_handle_coordinator_update_not_available(mock_solvis_switch):
    """Test _handle_coordinator_update when coordinator data indicates not available."""
    mock_solvis_switch.hass = MagicMock()
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(False, None, {})) as proc_patch:
        mock_solvis_switch._handle_coordinator_update()
        proc_patch.assert_called_with(mock_solvis_switch.coordinator.data, "Test Switch")
    assert mock_solvis_switch._attr_extra_state_attributes == {}


@pytest.mark.asyncio
async def test_async_turn_on_success(mock_solvis_switch):
    """Test async_turn_on when write_modbus_value returns True."""
    mock_solvis_switch.hass = MagicMock()
    with patch("custom_components.solvis_control.switch.write_modbus_value", new=AsyncMock(return_value=True)) as write_patch:
        with patch.object(mock_solvis_switch, "async_write_ha_state") as write_state_patch:
            await mock_solvis_switch.async_turn_on()
            write_patch.assert_awaited_once_with(mock_solvis_switch.coordinator.modbus, 1, 1)
            assert mock_solvis_switch._attr_is_on is True
            write_state_patch.assert_called()


@pytest.mark.asyncio
async def test_async_turn_on_failure(mock_solvis_switch):
    """Test async_turn_on when write_modbus_value returns False."""
    mock_solvis_switch.hass = MagicMock()
    with patch("custom_components.solvis_control.switch.write_modbus_value", new=AsyncMock(return_value=False)) as write_patch:
        with patch("custom_components.solvis_control.switch._LOGGER.error") as log_error:
            with patch.object(mock_solvis_switch, "async_write_ha_state") as write_state_patch:
                await mock_solvis_switch.async_turn_on()
                write_patch.assert_awaited_once_with(mock_solvis_switch.coordinator.modbus, 1, 1)
                log_error.assert_called_with("[Test Switch] Failed to turn on (write value 1) at register 1")
                write_state_patch.assert_called()


@pytest.mark.asyncio
async def test_async_turn_off_success(mock_solvis_switch):
    """Test async_turn_off when write_modbus_value returns True."""
    mock_solvis_switch.hass = MagicMock()
    # Set initial state to on
    mock_solvis_switch._attr_is_on = True
    with patch("custom_components.solvis_control.switch.write_modbus_value", new=AsyncMock(return_value=True)) as write_patch:
        with patch.object(mock_solvis_switch, "async_write_ha_state") as write_state_patch:
            await mock_solvis_switch.async_turn_off()
            write_patch.assert_awaited_once_with(mock_solvis_switch.coordinator.modbus, 1, 0)
            assert mock_solvis_switch._attr_is_on is False
            write_state_patch.assert_called()


@pytest.mark.asyncio
async def test_async_turn_off_failure(mock_solvis_switch):
    """Test async_turn_off when write_modbus_value returns False."""
    mock_solvis_switch.hass = MagicMock()
    # Set initial state to on
    mock_solvis_switch._attr_is_on = True
    with patch("custom_components.solvis_control.switch.write_modbus_value", new=AsyncMock(return_value=False)) as write_patch:
        with patch("custom_components.solvis_control.switch._LOGGER.error") as log_error:
            with patch.object(mock_solvis_switch, "async_write_ha_state") as write_state_patch:
                await mock_solvis_switch.async_turn_off()
                write_patch.assert_awaited_once_with(mock_solvis_switch.coordinator.modbus, 1, 0)
                log_error.assert_called_with("[Test Switch] Failed to turn off (write value 0) at register 1")
                write_state_patch.assert_called()


@pytest.mark.asyncio
async def test_async_setup_entry_no_host_switch(hass, mock_config_entry):
    """Test async_setup_entry when no host is provided for switch."""
    mock_config_entry.data.pop(CONF_HOST, None)
    with patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger:
        hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
        await async_setup_entry(hass, mock_config_entry, AsyncMock())
        mock_logger.assert_called_with("Device has no address")


@pytest.mark.asyncio
async def test_async_setup_entry_switch_entity_removal_exception(hass, mock_config_entry):
    """Test exception handling during removal of old switch entities."""
    hass.data = {DOMAIN: {mock_config_entry.entry_id: {DATA_COORDINATOR: AsyncMock()}}}
    with (
        patch("custom_components.solvis_control.utils.helpers.generate_device_info"),
        patch("custom_components.solvis_control.utils.helpers.REGISTERS", []),
        patch("custom_components.solvis_control.utils.helpers.remove_old_entities", side_effect=Exception("Test Exception")),
        patch("custom_components.solvis_control.utils.helpers._LOGGER.error") as mock_logger,
    ):
        mock_add_entities = MagicMock()
        await async_setup_entry(hass, mock_config_entry, mock_add_entities)
        mock_logger.assert_called_with("Error removing old entities: Test Exception", exc_info=True)
