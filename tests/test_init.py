"""
Tests for Solvis Control Init

Version: v2.1.0
"""

import pytest
import asyncio

import homeassistant.helpers.event as event

from unittest.mock import AsyncMock
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
from custom_components.solvis_control.const import DATA_COORDINATOR
from homeassistant.config_entries import ConfigEntry, ConfigEntryState, ConfigEntryNotReady
from custom_components.solvis_control import (
    async_setup_entry,
    async_unload_entry,
    async_migrate_entry,
    options_update_listener,
)
from custom_components.solvis_control.const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    POLL_RATE_SLOW,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    CONF_OPTION_9,
    CONF_OPTION_10,
    CONF_OPTION_11,
    CONF_OPTION_12,
    CONF_OPTION_13,
    DEVICE_VERSION,
    SolvisDeviceVersion,
    STORAGE_TYPE_CONFIG,
)


def dummy_update_entry(entry, **kwargs):
    if "data" in kwargs:
        entry.data = kwargs["data"]
    for key, value in kwargs.items():
        setattr(entry, key, value)
    return True


async def fake_migrate(hass, entry):
    return True


async def fake_migrate_fail(hass, entry):
    return False


@pytest.fixture
def extended_config_entry(mock_config_entry) -> ConfigEntry:
    mock_config_entry.entry_id = "test_entry"
    mock_config_entry.data.update(
        {
            CONF_HOST: "127.0.0.1",
            CONF_PORT: 502,
            DEVICE_VERSION: 1,  # SC3
            POLL_RATE_DEFAULT: 30,
            POLL_RATE_SLOW: 300,
            POLL_RATE_HIGH: 10,
        }
    )

    mock_config_entry.data[CONF_OPTION_13] = "SolvisBen Solo"
    mock_config_entry.version = 1
    mock_config_entry.minor_version = 2
    mock_config_entry.options = {}

    mock_config_entry.add_update_listener = lambda listener: lambda: None
    return mock_config_entry


# # # Tests for async_setup_entry # # #


@pytest.mark.asyncio
async def test_async_setup_entry(hass, extended_config_entry, monkeypatch):
    """Test async_setup_entry sets up the integration data correctly."""

    async def dummy_forward(*args, **kwargs):
        return True

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", dummy_forward)
    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)

    fake_client = AsyncMock()
    fake_client.connect.return_value = True
    monkeypatch.setattr("custom_components.solvis_control.create_modbus_client", lambda host, port, device_version: fake_client)

    async def dummy_first_refresh(self):
        return

    monkeypatch.setattr(SolvisModbusCoordinator, "async_config_entry_first_refresh", dummy_first_refresh)

    result = await async_setup_entry(hass, extended_config_entry)
    assert result is True
    assert DOMAIN in hass.data
    assert extended_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_setup_entry_missing_host(hass, extended_config_entry, monkeypatch):
    """Test async_setup_entry returns False if CONF_HOST is missing."""
    extended_config_entry.data.pop(CONF_HOST, None)

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", lambda *args, **kwargs: True)
    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    monkeypatch.setattr("custom_components.solvis_control.async_migrate_entry", fake_migrate)

    result = await async_setup_entry(hass, extended_config_entry)

    assert result is False


@pytest.mark.asyncio
async def test_setup_entry_missing_port(hass, extended_config_entry, monkeypatch):
    """Test async_setup_entry returns False if CONF_PORT is missing."""
    extended_config_entry.data.pop(CONF_PORT, None)

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", lambda *args, **kwargs: True)
    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    monkeypatch.setattr("custom_components.solvis_control.async_migrate_entry", fake_migrate)

    result = await async_setup_entry(hass, extended_config_entry)

    assert result is False


@pytest.mark.asyncio
async def test_setup_entry_migration_failure(hass, extended_config_entry, monkeypatch):
    """Test async_setup_entry returns False if async_migrate_entry fails."""
    monkeypatch.setattr("custom_components.solvis_control.async_migrate_entry", fake_migrate_fail)
    result = await async_setup_entry(hass, extended_config_entry)

    assert result is False


@pytest.mark.asyncio
async def test_setup_entry_connect_returns_false_raises_not_ready(hass, extended_config_entry, monkeypatch):
    """Test Modbus connect returns False triggers ConfigEntryNotReady."""
    monkeypatch.setattr(
        "custom_components.solvis_control.async_migrate_entry",
        lambda hass, entry: asyncio.sleep(0, result=True),
    )
    fake_client = AsyncMock()
    fake_client.connect.return_value = False
    monkeypatch.setattr(
        "custom_components.solvis_control.create_modbus_client",
        lambda host, port, device_version: fake_client,
    )
    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, extended_config_entry)


@pytest.mark.asyncio
async def test_setup_entry_connect_exception_raises_not_ready(hass, extended_config_entry, monkeypatch):
    """Test Modbus connect exception triggers ConfigEntryNotReady."""
    monkeypatch.setattr(
        "custom_components.solvis_control.async_migrate_entry",
        lambda hass, entry: asyncio.sleep(0, result=True),
    )
    fake_client = AsyncMock()
    fake_client.connect.side_effect = Exception("Connection error")
    monkeypatch.setattr(
        "custom_components.solvis_control.create_modbus_client",
        lambda host, port, device_version: fake_client,
    )
    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, extended_config_entry)


# # # Tests for async_unload_entry # # #


@pytest.mark.asyncio
async def test_async_unload_entry(hass, extended_config_entry, monkeypatch):
    """Test async_unload_entry."""

    hass.data.setdefault(DOMAIN, {})[extended_config_entry.entry_id] = {}

    client = AsyncMock()
    client.close = lambda: None
    extended_config_entry.runtime_data = {"modbus": client}

    async def dummy_unload(*args, **kwargs):
        return True

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", dummy_unload)
    result = await async_unload_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_failure(hass, extended_config_entry, monkeypatch):
    """Test async_unload_entry does not remove the entry from hass.data if unload fails."""

    hass.data.setdefault(DOMAIN, {})[extended_config_entry.entry_id] = {}

    client = AsyncMock()
    client.close = lambda: None
    extended_config_entry.runtime_data = {"modbus": client}

    async def dummy_unload_fail(*args, **kwargs):
        return False

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", dummy_unload_fail)
    result = await async_unload_entry(hass, extended_config_entry)

    assert result is False
    assert extended_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_unload_entry_close_exception_removes_entry(hass, extended_config_entry, monkeypatch):
    """Test exception in close() triggers removal of entry from hass.data."""
    hass.data.setdefault(DOMAIN, {})[extended_config_entry.entry_id] = {}
    client = AsyncMock()

    def close_raise():
        raise Exception("Close failed")

    client.close = close_raise
    extended_config_entry.runtime_data = {"modbus": client}

    async def dummy_unload_platforms(entry, platforms):
        return False

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", dummy_unload_platforms)

    result = await async_unload_entry(hass, extended_config_entry)

    assert result is False
    assert extended_config_entry.entry_id not in hass.data[DOMAIN]


# # # Tests for async_migrate_entry # # #


@pytest.mark.asyncio
async def test_async_migrate_entry(hass, extended_config_entry, monkeypatch):
    """Test async_migrate_entry aktualisiert den ConfigEntry korrekt."""

    update_kwargs = {}

    def dummy_update_entry(entry, **kwargs):
        update_kwargs.update(kwargs)
        return True

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)

    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert "version" in update_kwargs
    assert update_kwargs["version"] >= 2

    data = extended_config_entry.data

    assert POLL_RATE_DEFAULT in data
    assert POLL_RATE_SLOW in data
    assert POLL_RATE_HIGH in data


@pytest.mark.asyncio
async def test_migrate_branch_1(hass, extended_config_entry, monkeypatch):
    """Test migration for version 1 with minor_version < 3."""
    extended_config_entry.version = 1
    extended_config_entry.minor_version = 1  # < 3

    for key in [CONF_OPTION_1, CONF_OPTION_2, CONF_OPTION_3, CONF_OPTION_4, DEVICE_VERSION]:
        extended_config_entry.data.pop(key, None)

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.version == 2
    assert extended_config_entry.minor_version == 5
    assert extended_config_entry.data.get(DEVICE_VERSION) == "SC3"
    for key in [CONF_OPTION_1, CONF_OPTION_2, CONF_OPTION_3, CONF_OPTION_4]:
        assert key in extended_config_entry.data


@pytest.mark.asyncio
async def test_migrate_branch_2(hass, extended_config_entry, monkeypatch):
    """Test migration for version 1 with minor_version between 3 and 4."""
    extended_config_entry.version = 1
    extended_config_entry.minor_version = 3  # < 4

    for key in [POLL_RATE_DEFAULT, POLL_RATE_SLOW]:
        extended_config_entry.data.pop(key, None)

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.version == 2
    assert extended_config_entry.minor_version == 5
    assert extended_config_entry.data.get(POLL_RATE_DEFAULT) == 30
    assert extended_config_entry.data.get(POLL_RATE_SLOW) == 300


@pytest.mark.asyncio
async def test_migrate_branch_3(hass, extended_config_entry, monkeypatch):
    """Test migration for version 1 with minor_version == 4 (migrate to version 2, minor 0)."""
    extended_config_entry.version = 1
    extended_config_entry.minor_version = 4

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.version == 2
    assert extended_config_entry.minor_version == 5


@pytest.mark.asyncio
async def test_migrate_branch_4(hass, extended_config_entry, monkeypatch):
    """Test migration for version 2 with minor_version == 0 (set to 1 and add CONF_OPTION_5)."""
    extended_config_entry.version = 2
    extended_config_entry.minor_version = 0
    extended_config_entry.data.pop(CONF_OPTION_5, None)

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.minor_version == 5
    assert CONF_OPTION_5 in extended_config_entry.data


@pytest.mark.asyncio
async def test_migrate_branch_5(hass, extended_config_entry, monkeypatch):
    """Test migration for version 2 with minor_version == 1 (set to 2 and add CONF_OPTION_6, CONF_OPTION_7, POLL_RATE_HIGH)."""
    extended_config_entry.version = 2
    extended_config_entry.minor_version = 1

    for key in [CONF_OPTION_6, CONF_OPTION_7, POLL_RATE_HIGH]:
        extended_config_entry.data.pop(key, None)

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.minor_version == 5
    for key in [CONF_OPTION_6, CONF_OPTION_7]:
        assert key in extended_config_entry.data
    assert extended_config_entry.data.get(POLL_RATE_HIGH) == 10


@pytest.mark.asyncio
async def test_migrate_branch_6(hass, extended_config_entry, monkeypatch):
    """Test migration for version 2 with minor_version == 2 (set to 3 and add CONF_OPTION_8)."""
    extended_config_entry.version = 2
    extended_config_entry.minor_version = 2
    extended_config_entry.data.pop(CONF_OPTION_8, None)

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.minor_version == 5
    assert CONF_OPTION_8 in extended_config_entry.data


@pytest.mark.asyncio
async def test_migrate_all_missing_to_defaults(hass, extended_config_entry, monkeypatch):
    """Test that missing option keys are set to defaults in migration."""

    extended_config_entry.data.clear()

    extended_config_entry.version = 1
    extended_config_entry.minor_version = 1

    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)
    result = await async_migrate_entry(hass, extended_config_entry)

    assert result is True
    assert extended_config_entry.version == 2
    assert extended_config_entry.minor_version == 5

    assert extended_config_entry.data.get(CONF_OPTION_1) is False
    assert extended_config_entry.data.get(CONF_OPTION_2) is False
    assert extended_config_entry.data.get(CONF_OPTION_3) is False
    assert extended_config_entry.data.get(CONF_OPTION_4) is False
    assert extended_config_entry.data.get(CONF_OPTION_5) is False
    assert extended_config_entry.data.get(CONF_OPTION_6) is False
    assert extended_config_entry.data.get(CONF_OPTION_7) is False
    assert extended_config_entry.data.get(CONF_OPTION_8) is False
    assert extended_config_entry.data.get(CONF_OPTION_9) is False
    assert extended_config_entry.data.get(CONF_OPTION_10) is False
    assert extended_config_entry.data.get(CONF_OPTION_11) is False
    assert extended_config_entry.data.get(CONF_OPTION_12) is False
    assert extended_config_entry.data.get(CONF_OPTION_13) is None
    assert extended_config_entry.data.get(DEVICE_VERSION) == "SC3"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "option,expected",
    [
        (CONF_OPTION_1, False),
        (CONF_OPTION_2, False),
        (CONF_OPTION_3, False),
        (CONF_OPTION_4, False),
        (CONF_OPTION_5, False),
        (CONF_OPTION_6, False),
        (CONF_OPTION_7, False),
        (CONF_OPTION_8, False),
        (CONF_OPTION_9, False),
        (CONF_OPTION_10, False),
        (CONF_OPTION_11, False),
        (CONF_OPTION_12, False),
        (CONF_OPTION_13, None),
    ],
)
async def test_migrate_one_missing(hass, extended_config_entry, monkeypatch, option, expected):
    """Test that if a given option is missing in new_data, the migration sets it to its default value."""
    extended_config_entry.data = dict(extended_config_entry.data)
    extended_config_entry.data.pop(option, None)

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", lambda entry, platforms: True)
    monkeypatch.setattr(hass.config_entries, "async_update_entry", dummy_update_entry)

    await async_migrate_entry(hass, extended_config_entry)
    assert extended_config_entry.data.get(option) == expected


DEFAULTS = {
    CONF_OPTION_1: False,
    CONF_OPTION_2: False,
    CONF_OPTION_3: False,
    CONF_OPTION_4: False,
    CONF_OPTION_5: False,
    CONF_OPTION_6: False,
    CONF_OPTION_7: False,
    CONF_OPTION_8: False,
    CONF_OPTION_9: False,
    CONF_OPTION_10: False,
    CONF_OPTION_11: False,
    CONF_OPTION_12: False,
    CONF_OPTION_13: None,
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "present_option",
    [
        CONF_OPTION_1,
        CONF_OPTION_2,
        CONF_OPTION_3,
        CONF_OPTION_4,
        CONF_OPTION_5,
        CONF_OPTION_6,
        CONF_OPTION_7,
        CONF_OPTION_8,
        CONF_OPTION_9,
        CONF_OPTION_10,
        CONF_OPTION_11,
        CONF_OPTION_12,
        CONF_OPTION_13,
    ],
)
async def test_migrate_only_one_present(hass, extended_config_entry, monkeypatch, present_option):
    new_data = {
        CONF_HOST: "127.0.0.1",
        CONF_NAME: "TestDevice",
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
        POLL_RATE_HIGH: 10,
        DEVICE_VERSION: "SC3",
    }

    custom_value = not DEFAULTS[present_option]
    new_data[present_option] = custom_value
    extended_config_entry.data = new_data

    captured_data = {}

    def capture_update_entry(entry, **kwargs):
        nonlocal captured_data
        if "data" in kwargs:
            captured_data = kwargs["data"]
            entry.data = kwargs["data"]
        return True

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", lambda entry, platforms: True)
    monkeypatch.setattr(hass.config_entries, "async_update_entry", capture_update_entry)

    await async_migrate_entry(hass, extended_config_entry)

    for option, default in DEFAULTS.items():
        if present_option in {CONF_OPTION_9, CONF_OPTION_10, CONF_OPTION_11, CONF_OPTION_12}:
            expected = default
        else:
            if present_option == CONF_OPTION_6 and option in {CONF_OPTION_9, CONF_OPTION_11}:
                expected = custom_value
            elif present_option == CONF_OPTION_7 and option in {CONF_OPTION_10, CONF_OPTION_12}:
                expected = custom_value
            elif option == present_option:
                expected = custom_value
            else:
                expected = default
        assert captured_data.get(option) == expected, f"For option {option}: expected {expected}, got {captured_data.get(option)}"


# # # Tests for options_update_listener # # #


class FakeEntries:
    def __init__(self, entries):
        self.data = entries

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, key):
        return key in self.data

    def values(self):
        return self.data.values()

    def get(self, key, default=None):
        return self.data.get(key, default)


@pytest.mark.asyncio
async def test_options_update_listener(hass, extended_config_entry, monkeypatch):
    """Test options_update_listener: unloads platforms, forwards entry setups and refreshes the coordinator."""
    fake_coordinator = AsyncMock()
    fake_coordinator.async_refresh = AsyncMock()
    hass.data.setdefault(DOMAIN, {})[extended_config_entry.entry_id] = {
        DATA_COORDINATOR: fake_coordinator,
        "unsub_options_update_listener": lambda: None,
    }

    extended_config_entry.state = ConfigEntryState.LOADED
    extended_config_entry.setup_lock = asyncio.Lock()

    hass.config_entries._entries = FakeEntries({extended_config_entry.entry_id: extended_config_entry})

    monkeypatch.setattr(event, "async_track_time_interval", lambda hass, action, interval: lambda: None)

    unloaded = False

    async def dummy_unload(*args, **kwargs):
        nonlocal unloaded
        unloaded = True
        return True

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", dummy_unload)

    forward_called = False

    async def dummy_forward(*args, **kwargs):
        nonlocal forward_called
        forward_called = True
        return True

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", dummy_forward)

    async def dummy_reload(entry_id):
        await fake_coordinator.async_refresh()
        await hass.config_entries.async_unload_platforms(extended_config_entry, [])
        await hass.config_entries.async_forward_entry_setups(extended_config_entry, [])
        return True

    monkeypatch.setattr(hass.config_entries, "async_reload", dummy_reload)

    await options_update_listener(hass, extended_config_entry)
    assert unloaded is True
    assert forward_called is True
    fake_coordinator.async_refresh.assert_called_once()
