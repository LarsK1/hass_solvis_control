"""
Tests for Solvis Control Helpers

Version: v2.1.0
"""

import asyncio
import pytest
from decimal import Decimal
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from custom_components.solvis_control.utils import helpers
from pymodbus.exceptions import ConnectionException, ModbusException
from tests.dummies import DummyConfigEntry, DummyEntity, DummyEntityRegistry, DummyRegister, dummy_srp, dummy_srp_empty
from tests.dummies import DummyModbusClient, DummyModbusResponse, DummyResponseObj
from custom_components.solvis_control.sensor import SolvisSensor
from homeassistant.const import EntityCategory
from custom_components.solvis_control.const import (
    CONF_NAME,
    PORT,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    MANUFACTURER,
    DATA_COORDINATOR,
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    POLL_RATE_SLOW,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
)


class DummyModbusCM:
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        try:
            self._client.close()
        except:
            pass


# # # Tests for generate_device_info # # #


def test_generate_device_info():
    data = {
        DEVICE_VERSION: 1,
        "VERSIONSC": "1.0.1",
        "VERSIONNBG": "1.0",
    }
    entry = DummyConfigEntry(data)
    host = "192.168.1.100"
    name = "TestDevice"
    info = helpers.generate_device_info(entry, host, name)

    assert isinstance(info, dict)
    assert (DOMAIN, host) in info["identifiers"]
    assert info["name"] == name
    assert info["manufacturer"] == MANUFACTURER
    assert info["model"] == "Solvis Control 3"
    assert info["sw_version"] == "1.0.1"
    assert info["hw_version"] == "1.0"


def test_generate_device_info_invalid_version():
    data = {
        DEVICE_VERSION: "invalid",
        "VERSIONSC": "1.0.1",
        "VERSIONNBG": "1.0",
    }
    entry = DummyConfigEntry(data)
    host = "192.168.1.100"
    name = "TestDevice"
    info = helpers.generate_device_info(entry, host, name)

    assert info["model"] == "Solvis Control (unbekannt)"


# # # Tests for fetch_modbus_value # # #


@pytest.mark.asyncio
async def test_fetch_modbus_value_success(monkeypatch):
    dummy_client = DummyModbusClient([123])
    monkeypatch.setattr(
        helpers,
        "create_modbus_client",
        lambda host, port, device_version=None: DummyModbusCM(dummy_client),
    )
    result = await helpers.fetch_modbus_value(register=10, register_type=1, host="127.0.0.1", port=502)

    assert result == 123


@pytest.mark.asyncio
async def test_fetch_modbus_value_invalid_response(monkeypatch):
    host, port = "127.0.0.1", 502
    dummy_client = DummyModbusClient([])
    monkeypatch.setattr(
        helpers,
        "create_modbus_client",
        lambda host, port, device_version=None: (_ for _ in ()).throw(ModbusException("Invalid response from Modbus for register 10")),
    )
    with pytest.raises(ModbusException):
        await helpers.fetch_modbus_value(register=10, register_type=1, host="127.0.0.1", port=502)


@pytest.mark.asyncio  #
async def test_fetch_modbus_value_connection_exception(monkeypatch):
    host, port = "127.0.0.1", 502
    dummy_client = DummyModbusClient(registers=[123], raise_on_connect=True)
    monkeypatch.setattr(
        helpers,
        "create_modbus_client",
        lambda host, port, device_version=None: (_ for _ in ()).throw(ConnectionException(f"Failed to connect to Modbus device at {host}:{port}")),
    )
    with pytest.raises(ConnectionException):
        await helpers.fetch_modbus_value(register=10, register_type=1, host="127.0.0.1", port=502)


@pytest.mark.asyncio
async def test_fetch_modbus_value_connect_fail(monkeypatch):
    host, port = "127.0.0.1", 502
    dummy_client = DummyModbusClient(connect_success=False)
    monkeypatch.setattr(
        helpers,
        "create_modbus_client",
        lambda host, port, device_version=None: (_ for _ in ()).throw(ConnectionException(f"Failed to connect to Modbus device at {host}:{port}")),
    )
    with pytest.raises(ConnectionException) as excinfo:
        await helpers.fetch_modbus_value(register=10, register_type=1, host=host, port=port)

    assert f"Failed to connect to Modbus device at {host}:{port}" in str(excinfo.value)


@pytest.mark.asyncio
async def test_fetch_modbus_value_holding_registers(monkeypatch):
    dummy = DummyModbusClient([456])
    monkeypatch.setattr(
        helpers,
        "create_modbus_client",
        lambda host, port, device_version=None: DummyModbusCM(dummy),
    )
    result = await helpers.fetch_modbus_value(register=20, register_type=0, host="127.0.0.1", port=502)
    assert result == 456


@pytest.mark.asyncio
async def test_fetch_modbus_value_error_response_is_error(monkeypatch):
    # simuliert data.isError() == True
    dummy_client = DummyModbusClient([1])

    async def fake_read_input(address, count):
        return DummyModbusResponse([1], error=True)

    dummy_client.read_input_registers = fake_read_input
    monkeypatch.setattr(
        helpers,
        "create_modbus_client",
        lambda host, port, device_version=None: DummyModbusCM(dummy_client),
    )
    with pytest.raises(ModbusException) as excinfo:
        await helpers.fetch_modbus_value(register=5, register_type=1, host="127.0.0.1", port=502)
    assert "Invalid response from Modbus for register 5" in str(excinfo.value)


# # # Tests for get_mac # # #


def test_get_mac_success(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [((None, DummyResponseObj("AA:BB:CC:DD:EE:FF")),)])
    mac = helpers.get_mac("192.168.1.1")

    assert mac == "AA:BB:CC:DD:EE:FF"


def test_get_mac_no_response(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [])
    mac = helpers.get_mac("192.168.1.1")

    assert mac is None


def test_get_mac_empty_responses(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [])
    mac = helpers.get_mac("192.168.1.1")

    assert mac is None


def test_get_mac_empty_result(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [[]])
    mac = helpers.get_mac("192.168.1.1")

    assert mac is None


def test_get_mac_insufficient_length(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [[("dummy",)]])
    mac = helpers.get_mac("192.168.1.1")

    assert mac is None


def test_get_mac_second_none(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [[("dummy", None)]])
    mac = helpers.get_mac("192.168.1.1")

    assert mac is None


# # # Tests for remove_old_entities # # #


def test_remove_old_entities(monkeypatch):
    ent1 = DummyEntity("unique_1", "entity.one", "dummy_entry")
    ent2 = DummyEntity("unique_2", "entity.two", "dummy_entry")
    registry = DummyEntityRegistry({"entity.one": ent1, "entity.two": ent2})

    monkeypatch.setattr(helpers, "er", type("DummyER", (), {"async_get": lambda hass: registry}))

    monkeypatch.setattr(helpers, "async_resolve_entity_id", lambda reg, unique_id: next((entity.entity_id for entity in reg.entities.values() if entity.unique_id == unique_id), None))

    asyncio.run(helpers.remove_old_entities(hass=None, config_entry_id="dummy_entry", active_entity_ids={"unique_1"}))

    assert "entity.one" in registry.entities
    assert "entity.two" not in registry.entities


# # # Tests for generate_unique_id # # #


def test_generate_unique_id_normal():
    uid = helpers.generate_unique_id(modbus_address=100, supported_version=1, name="Test Sensor")

    assert uid == "100_1_Test_Sensor"


def test_generate_unique_id_special_chars():
    uid = helpers.generate_unique_id(modbus_address=100, supported_version=1, name="@@@")

    assert uid == "100_1"


# # # Tests for write_modbus_value # # #


@pytest.mark.asyncio
async def test_write_modbus_value_success():
    dummy_modbus = DummyModbusClient(write_response=DummyModbusResponse([123], error=False))
    result = await helpers.write_modbus_value(dummy_modbus, address=10, value=123)

    assert result is True


@pytest.mark.asyncio
async def test_write_modbus_value_error_response():
    dummy_modbus = DummyModbusClient(write_response=DummyModbusResponse([123], error=True))
    result = await helpers.write_modbus_value(dummy_modbus, address=10, value=123)

    assert result is False


@pytest.mark.asyncio
async def test_write_modbus_value_connection_exception():
    dummy_modbus = DummyModbusClient(
        write_response=DummyModbusResponse([123], error=False),
        raise_on_connect=True,
    )
    result = await helpers.write_modbus_value(dummy_modbus, address=10, value=123)

    assert result is False


@pytest.mark.asyncio
async def test_write_modbus_value_modbus_exception(monkeypatch):
    host, port = "127.0.0.1", 502
    dummy = DummyModbusClient(raise_on_write=True, host=host, port=port)
    result = await helpers.write_modbus_value(dummy, address=10, value=123)

    assert result is False


@pytest.mark.asyncio
async def test_write_modbus_value_generic_exception(monkeypatch):
    host, port = "127.0.0.1", 502
    dummy = DummyModbusClient(raise_generic_on_write=True)
    result = await helpers.write_modbus_value(dummy, address=10, value=123)

    assert result is False


# # # Tests for process_coordinator_data # # #


def test_process_coordinator_data_none():
    available, value, attrs = helpers.process_coordinator_data(None, "test")

    assert available is False
    assert value is None
    assert attrs == {}


def test_process_coordinator_data_not_dict():
    available, value, attrs = helpers.process_coordinator_data("invalid", "test")

    assert available is False
    assert value is None


def test_process_coordinator_data_key_missing():
    data = {"other": 42}
    available, value, attrs = helpers.process_coordinator_data(data, "test")

    assert available is None
    assert value is None
    assert attrs == {}


def test_process_coordinator_data_value_none():
    data = {"test": None}
    available, value, attrs = helpers.process_coordinator_data(data, "test")

    assert available is False
    assert value is None


def test_process_coordinator_data_invalid_type():
    data = {"test": "string"}
    available, value, attrs = helpers.process_coordinator_data(data, "test")

    assert available is False
    assert value is None


def test_process_coordinator_data_error_value():
    data = {"test": -300}
    available, value, attrs = helpers.process_coordinator_data(data, "test")

    assert available is False
    assert value is None


def test_process_coordinator_data_valid():
    data = {"test": 42}
    available, value, attrs = helpers.process_coordinator_data(data, "test")

    assert available is True
    assert value == 42
    assert attrs == {"raw_value": 42}


# # # Tests for should_skip_register # # #


def test_should_skip_register_no_conf_option():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: False}
    reg = DummyRegister(name="sensor", address=10, conf_option=0, supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is False


def test_should_skip_register_conf_option_disabled():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: False}
    reg = DummyRegister(name="sensor", address=10, conf_option=1, supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is True


def test_should_skip_register_tuple_missing_option():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: True, CONF_OPTION_2: False}
    reg = DummyRegister(name="sensor", address=10, conf_option=(1, 2), supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is True


def test_should_skip_register_version_mismatch():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: True}
    reg = DummyRegister(name="sensor", address=10, conf_option=1, supported_version=2)

    assert helpers.should_skip_register(entry_data, reg) is True


def test_should_skip_register_ok():
    entry_data = {DEVICE_VERSION: "2", CONF_OPTION_1: True}
    reg = DummyRegister(name="sensor", address=10, conf_option=1, supported_version=2)

    assert helpers.should_skip_register(entry_data, reg) is False


def test_should_skip_register_tuple_all_true():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: True, CONF_OPTION_2: True}
    reg = DummyRegister(name="sensor", address=10, conf_option=(1, 2), supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is False


def test_should_skip_register_tuple_missing_option():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: True, CONF_OPTION_2: False}
    reg = DummyRegister(name="sensor", address=10, conf_option=(1, 2), supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is True


def test_should_skip_register_sc3_for_sc2():
    entry_data = {DEVICE_VERSION: "2", CONF_OPTION_1: True}
    reg = DummyRegister(name="sensor", address=10, conf_option=1, supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is True


def test_should_skip_register_invalid_device_version():
    entry_data = {DEVICE_VERSION: "invalid", CONF_OPTION_1: True}
    reg = DummyRegister("sensor", 10, 0, 2)  # supported_version=2

    assert helpers.should_skip_register(entry_data, reg) is False


# # # Tests for async_setup_solvis_entities # # #


@pytest.mark.asyncio
async def test_async_setup_solvis_entities_sensor(monkeypatch):
    dummy_register = DummyRegister("Test Sensor", 101, 1, 1)
    dummy_register.unit = "°C"
    dummy_register.device_class = "temperature"
    dummy_register.state_class = "measurement"
    dummy_register.entity_category = "diagnostic"
    dummy_register.suggested_precision = 1
    dummy_register.options = None
    dummy_register.input_type = 0
    dummy_register.enabled_by_default = True
    dummy_register.data_processing = 0

    monkeypatch.setattr(helpers, "REGISTERS", [dummy_register])

    dummy_entry = DummyConfigEntry()
    dummy_entry.entry_id = "test_entry"

    class DummyHass:
        def __init__(self):
            self.data = {DOMAIN: {dummy_entry.entry_id: {DATA_COORDINATOR: object()}}}
            self.config = type("DummyConfig", (), {"config_dir": "."})()
            self.bus = object()

    async def dummy_remove_old_entities(hass, entry_id, active_entity_ids):
        return

    monkeypatch.setattr(helpers, "remove_old_entities", dummy_remove_old_entities)
    dummy_hass = DummyHass()
    created_entities = []

    def dummy_add_entities(entities):
        created_entities.extend(entities)

    await helpers.async_setup_solvis_entities(
        dummy_hass,
        dummy_entry,
        dummy_add_entities,
        entity_cls=SolvisSensor,
        input_type=0,
    )

    assert len(created_entities) == 1
    sensor = created_entities[0]
    assert sensor.native_unit_of_measurement == "°C"
    assert sensor.device_class == "temperature"
    assert sensor.state_class == "measurement"
    assert sensor.entity_category == EntityCategory.DIAGNOSTIC
    assert sensor.suggested_display_precision == 1


# # # Tests for create_modbus_client # # #


def test_create_modbus_client_device_version_2(monkeypatch):
    captured = {}

    class DummyClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(helpers, "AsyncModbusTcpClient", DummyClient)
    client = helpers.create_modbus_client("127.0.0.1", 502, device_version=2)

    assert isinstance(client, DummyClient)
    assert captured == {
        "host": "127.0.0.1",
        "port": 502,
        "timeout": 6.0,
        "retries": 3,
        "reconnect_delay": 1.0,
        "reconnect_delay_max": 5.0,
    }
