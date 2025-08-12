"""
Tests for Solvis Entity

Version: v2.1.0
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from custom_components.solvis_control.entity import SolvisEntity
from custom_components.solvis_control.utils.helpers import generate_unique_id


class DummySolvisEntity(SolvisEntity):
    def _update_value(self, value, extra_attrs):
        self._value = value
        self._extra_attrs = extra_attrs

    def _reset_value(self):
        self._value = None
        self._extra_attrs = {}


class MinimalSolvisEntity(SolvisEntity):
    pass


@pytest.fixture
def dummy_entity(hass, dummy_coordinator, mock_device_info, mock_platform):
    entity = DummySolvisEntity(
        coordinator=dummy_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="Test Entity",
        modbus_address=1,
        supported_version=1,
        enabled_by_default=True,
        data_processing=0,
        poll_rate=False,
    )
    entity.hass = hass
    entity.schedule_update_ha_state = MagicMock()
    return entity


@pytest.fixture
def minimal_entity(hass, dummy_coordinator, mock_device_info, mock_platform):
    entity = MinimalSolvisEntity(
        coordinator=dummy_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="Test Entity",
        modbus_address=1,
        supported_version=1,
        enabled_by_default=True,
        data_processing=0,
        poll_rate=False,
    )
    entity.hass = hass
    entity.platform = mock_platform
    entity.schedule_update_ha_state = MagicMock()
    return entity


def test_entity_initialization(dummy_entity):
    assert dummy_entity._host == "test_host"
    assert dummy_entity.modbus_address == 1
    assert dummy_entity._response_key == "Test Entity"
    assert dummy_entity.entity_registry_enabled_default is True
    assert dummy_entity.device_info is not None
    assert dummy_entity.supported_version == 1
    expected_unique_id = generate_unique_id(1, 1, "Test Entity")
    assert dummy_entity._attr_unique_id == expected_unique_id
    assert dummy_entity.translation_key == "Test Entity"
    assert dummy_entity.data_processing == 0
    assert dummy_entity.poll_rate is False


def test_handle_coordinator_update_available(dummy_entity, dummy_coordinator):
    # Simulate available data via process_coordinator_data
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(True, "new_value", {"attr": "val"})):
        dummy_coordinator.data = {"Test Entity": 123}
        dummy_entity._handle_coordinator_update()
        assert dummy_entity._value == "new_value"
        assert dummy_entity._extra_attrs == {"attr": "val"}
        dummy_entity.schedule_update_ha_state.assert_called_once()


def test_handle_coordinator_update_unavailable(dummy_entity, dummy_coordinator):
    # Simulate unavailable data (False)
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(False, "old_value", {"attr": "val"})):
        dummy_coordinator.data = {"Test Entity": 456}
        dummy_entity._value = "prev_value"
        dummy_entity._extra_attrs = {"old": "data"}
        dummy_entity._handle_coordinator_update()
        assert dummy_entity._value is None
        assert dummy_entity._extra_attrs == {}
        dummy_entity.schedule_update_ha_state.assert_called_once()


def test_handle_coordinator_update_no_update(dummy_entity):
    with patch("custom_components.solvis_control.entity.process_coordinator_data", return_value=(None, None, None)):
        dummy_entity._value = "previous"
        dummy_entity._extra_attrs = {"old": "data"}
        dummy_entity._handle_coordinator_update()
        assert dummy_entity._value == "previous"
        assert dummy_entity._extra_attrs == {"old": "data"}
        dummy_entity.schedule_update_ha_state.assert_not_called()


def test_update_value_not_overridden(minimal_entity):
    """Test that calling _update_value without override raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        minimal_entity._update_value("dummy_value", {"attr": "val"})


def test_reset_value_default(minimal_entity):
    """Test that _reset_value default implementation does nothing (returns None)."""
    result = minimal_entity._reset_value()
    assert result is None


@pytest.mark.asyncio
async def test_async_added_to_hass_custom_name(hass, dummy_coordinator, mock_device_info):
    ent = DummySolvisEntity(dummy_coordinator, mock_device_info, "host", "reg1", 1)
    ent.hass, ent.entity_id, ent._attr_name = hass, "sensor.reg1", "Wohnzimmer"

    mock_entry = MagicMock(original_name="Altname", name="Altname")
    mock_registry = MagicMock(async_get=MagicMock(return_value=mock_entry))
    mock_registry.async_update_entity = MagicMock()

    with (
        patch(
            "custom_components.solvis_control.entity.CoordinatorEntity.async_added_to_hass",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.solvis_control.entity.er.async_get",
            return_value=mock_registry,
        ),
        patch(
            "custom_components.solvis_control.entity.async_get_translations",
            return_value={},
        ),
    ):
        ent.async_write_ha_state = MagicMock()
        await ent.async_added_to_hass()

    mock_registry.async_update_entity.assert_called_once_with(ent.entity_id, name="Wohnzimmer")
    ent.async_write_ha_state.assert_called_once()


@pytest.mark.asyncio
async def test_async_added_to_hass_clear_name(hass, dummy_coordinator, mock_device_info):
    ent = DummySolvisEntity(dummy_coordinator, mock_device_info, "host", "reg2", 2)
    ent.hass, ent.entity_id, ent._attr_name = hass, "sensor.reg2", ""

    mock_entry = MagicMock(original_name="reg2", name="Benutzername")
    mock_registry = MagicMock(async_get=MagicMock(return_value=mock_entry))
    mock_registry.async_update_entity = MagicMock()

    with (
        patch(
            "custom_components.solvis_control.entity.CoordinatorEntity.async_added_to_hass",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.solvis_control.entity.er.async_get",
            return_value=mock_registry,
        ),
        patch(
            "custom_components.solvis_control.entity.async_get_translations",
            return_value={},
        ),
    ):
        ent.async_write_ha_state = MagicMock()
        await ent.async_added_to_hass()

    assert not hasattr(ent, "_attr_name")
    mock_registry.async_update_entity.assert_called_once_with(ent.entity_id, name=None)
    ent.async_write_ha_state.assert_called_once()


@pytest.mark.parametrize(
    ("translated", "old", "new", "expected"),
    [
        ("HKR1: Vorlauf", "HKR1", "Heizung EG", "Heizung EG: Vorlauf"),
        ("HKR2-Vorlauf", "HKR2", "Heizung OG", "Heizung OG-Vorlauf"),
        ("Temperatur HKR3", "HKR3", "Heizung DG", "Temperatur Heizung DG"),
    ],
)
def test_replace_hkr_prefix_varianten(dummy_coordinator, mock_device_info, translated, old, new, expected):
    ent = MinimalSolvisEntity(dummy_coordinator, mock_device_info, "host", "dummy", 1)
    assert ent._replace_hkr_prefix(translated, old, new) == expected


@pytest.mark.asyncio
async def test_async_added_to_hass_custom_name_no_update(hass, dummy_coordinator, mock_device_info):
    ent = DummySolvisEntity(dummy_coordinator, mock_device_info, "host", "reg3", 3)
    ent.hass, ent.entity_id, ent._attr_name = hass, "sensor.reg3", "Wohnzimmer"

    mock_entry = MagicMock(original_name="Wohnzimmer", name="Wohnzimmer")
    mock_registry = MagicMock(async_get=MagicMock(return_value=mock_entry))
    mock_registry.async_update_entity = MagicMock()

    with (
        patch(
            "custom_components.solvis_control.entity.CoordinatorEntity.async_added_to_hass",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.solvis_control.entity.er.async_get",
            return_value=mock_registry,
        ),
        patch(
            "custom_components.solvis_control.entity.async_get_translations",
            return_value={},
        ),
    ):
        ent.async_write_ha_state = MagicMock()
        await ent.async_added_to_hass()

    mock_registry.async_update_entity.assert_not_called()
    ent.async_write_ha_state.assert_called_once()
