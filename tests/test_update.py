"""
Tests for Solvis Update Entity

Version: v2.0.0
"""

import pytest
from unittest.mock import MagicMock, patch

from custom_components.solvis_control.update import SolvisUpdateEntity
from custom_components.solvis_control.const import LATEST_SW_VERSION, DOMAIN


@pytest.fixture
def mock_solvis_update_entity_firmware(mock_coordinator, mock_device_info):
    """Fixture for a firmware update entity."""
    entity = SolvisUpdateEntity(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="version_sc",
        modbus_address=32770,  # Corresponds to VERSIONSC
    )
    entity.hass = MagicMock()
    return entity


@pytest.fixture
def mock_solvis_update_entity_hardware(mock_coordinator, mock_device_info):
    """Fixture for a hardware update entity."""
    entity = SolvisUpdateEntity(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="version_nbg",
        modbus_address=32771,  # Corresponds to VERSIONNBG
    )
    entity.hass = MagicMock()
    return entity


def test_firmware_update_initialization(mock_solvis_update_entity_firmware):
    """Test initialization of the firmware update entity."""
    entity = mock_solvis_update_entity_firmware
    assert entity.title == "Controller Firmware"
    assert entity.unique_id == "32770_1_version_sc"


def test_hardware_update_initialization(mock_solvis_update_entity_hardware):
    """Test initialization of the hardware update entity."""
    entity = mock_solvis_update_entity_hardware
    assert entity.title == "Network Board Firmware"
    assert entity.unique_id == "32771_1_version_nbg"


@pytest.mark.asyncio
async def test_firmware_update_version_processing(mock_solvis_update_entity_firmware):
    """Test the firmware update entity's version processing."""
    entity = mock_solvis_update_entity_firmware
    test_value = 32016  # Represents "3.20.16"

    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {})) as proc_patch, \
         patch("custom_components.solvis_control.update.dr.async_get") as mock_async_get:

        mock_device_registry = MagicMock()
        mock_device = MagicMock()
        mock_device.id = "test_device_id"
        mock_async_get.return_value = mock_device_registry
        mock_device_registry.async_get_device.return_value = mock_device

        entity._handle_coordinator_update()

        proc_patch.assert_called_with(entity.coordinator.data, "version_sc")
        assert entity.installed_version == "3.20.16"
        assert entity.latest_version == LATEST_SW_VERSION
        mock_device_registry.async_update_device.assert_called_once_with(mock_device.id, sw_version="3.20.16")


@pytest.mark.asyncio
async def test_hardware_update_version_processing(mock_solvis_update_entity_hardware):
    """Test the hardware update entity's version processing."""
    entity = mock_solvis_update_entity_hardware
    test_value = 10203  # Represents "1.02.03"

    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, test_value, {})) as proc_patch, \
         patch("custom_components.solvis_control.update.dr.async_get") as mock_async_get:

        mock_device_registry = MagicMock()
        mock_device = MagicMock()
        mock_device.id = "test_device_id"
        mock_async_get.return_value = mock_device_registry
        mock_device_registry.async_get_device.return_value = mock_device

        entity._handle_coordinator_update()

        proc_patch.assert_called_with(entity.coordinator.data, "version_nbg")
        assert entity.installed_version == "1.02.03"
        assert entity.latest_version == "1.02.03"  # Hardware version is its own latest
        mock_device_registry.async_update_device.assert_called_once_with(mock_device.id, hw_version="1.02.03")


@pytest.mark.asyncio
async def test_invalid_version_data(mock_solvis_update_entity_firmware):
    """Test that the entity handles invalid or incomplete version data."""
    entity = mock_solvis_update_entity_firmware

    # Test with None value
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, None, {})):
        entity._handle_coordinator_update()
        assert entity.installed_version is None
        assert entity.latest_version is None

    # Test with short value
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, 1234, {})):
        entity._handle_coordinator_update()
        assert entity.installed_version is None
        assert entity.latest_version is None
