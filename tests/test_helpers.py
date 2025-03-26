import asyncio
import pytest
from decimal import Decimal
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry

from custom_components.solvis_control.const import (
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    MANUFACTURER,
    DOMAIN,
)
from custom_components.solvis_control.utils import helpers
from pymodbus.exceptions import ConnectionException, ModbusException


class DummyConfigEntry:
    def __init__(self, data):
        self.data = data
        self.entry_id = "dummy_entry"


class DummyModbusResponse:
    def __init__(self, registers):
        self.registers = registers


class DummyModbusClient:
    def __init__(self, registers):
        self.registers = registers
        self.DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

    async def connect(self):
        return True

    async def read_input_registers(self, address, count):
        return DummyModbusResponse(self.registers)

    async def read_holding_registers(self, address, count):
        return DummyModbusResponse(self.registers)

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0]

    def close(self):
        pass


class DummyModbus:
    """Dummy modbus for write_modbus_value tests."""

    def __init__(self, response, connect_success=True):
        self.response = response
        self.connect_success = connect_success
        self.called_close = False

    async def connect(self):
        if not self.connect_success:
            raise ConnectionException("Connect failed")
        return True

    async def write_register(self, address, value, slave=1):
        return self.response

    def close(self):
        self.called_close = True


class DummyResponse:
    def __init__(self, error=False):
        self._error = error

    def isError(self):
        return self._error


class DummyRegister:
    """Simple dummy register object for should_skip_register tests."""

    def __init__(self, name, address, conf_option, supported_version):
        self.name = name
        self.address = address
        self.conf_option = conf_option
        self.supported_version = supported_version


class DummyEntities:
    def __init__(self, entities):
        self._entities = entities

    def __getitem__(self, key):
        return self._entities[key]

    def __iter__(self):
        return iter(self._entities)

    def values(self):
        return self._entities.values()

    def get(self, key):
        return self._entities.get(key)

    def get_entry(self, key):
        return self._entities.get(key)

    def pop(self, key, default=None):
        return self._entities.pop(key, default)


class DummyEntityRegistry:
    def __init__(self, entities):
        self.entities = DummyEntities(entities)

    def async_remove(self, entity_id):
        self.entities.pop(entity_id, None)


class DummyEntity:
    def __init__(self, unique_id, entity_id, config_entry_id="dummy_entry"):
        self.unique_id = unique_id
        self.entity_id = entity_id
        self.config_entry_id = config_entry_id


class DummyResponseObj:
    def __init__(self, hwsrc):
        self.hwsrc = hwsrc


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


@pytest.mark.asyncio
async def test_fetch_modbus_value_success(monkeypatch):
    dummy_client = DummyModbusClient([123])
    monkeypatch.setattr(
        helpers,
        "ModbusClient",
        type("DummyModbusModule", (), {"AsyncModbusTcpClient": lambda host, port: dummy_client}),
    )
    result = await helpers.fetch_modbus_value(register=10, register_type=1, host="127.0.0.1", port=502)
    assert result == 123


@pytest.mark.asyncio
async def test_fetch_modbus_value_invalid_response(monkeypatch):
    dummy_client = DummyModbusClient([])
    monkeypatch.setattr(
        helpers,
        "ModbusClient",
        type("DummyModbusModule", (), {"AsyncModbusTcpClient": lambda host, port: dummy_client}),
    )
    with pytest.raises(ModbusException):
        await helpers.fetch_modbus_value(register=10, register_type=1, host="127.0.0.1", port=502)


@pytest.mark.asyncio
async def test_fetch_modbus_value_connection_exception(monkeypatch):

    class FailingModbusClient(DummyModbusClient):
        async def connect(self):
            raise ConnectionException("Connection failed")

    dummy_client = FailingModbusClient([123])
    monkeypatch.setattr(
        helpers,
        "ModbusClient",
        type("DummyModbusModule", (), {"AsyncModbusTcpClient": lambda host, port: dummy_client}),
    )
    with pytest.raises(ConnectionException):
        await helpers.fetch_modbus_value(register=10, register_type=1, host="127.0.0.1", port=502)


def dummy_srp(packet, timeout, verbose):
    return [((None, DummyResponseObj("AA:BB:CC:DD:EE:FF")),)]


def dummy_srp_empty(packet, timeout, verbose):
    return []


def test_get_mac_success(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [((None, DummyResponseObj("AA:BB:CC:DD:EE:FF")),)])
    mac = helpers.get_mac("192.168.1.1")
    assert mac == "AA:BB:CC:DD:EE:FF"


def test_get_mac_no_response(monkeypatch):
    monkeypatch.setattr(helpers, "srp", lambda packet, timeout, verbose: [])
    mac = helpers.get_mac("192.168.1.1")
    assert mac is None


def test_remove_old_entities(monkeypatch):
    ent1 = DummyEntity("unique_1", "entity.one", "dummy_entry")
    ent2 = DummyEntity("unique_2", "entity.two", "dummy_entry")
    registry = DummyEntityRegistry({"entity.one": ent1, "entity.two": ent2})

    monkeypatch.setattr(helpers, "er", type("DummyER", (), {"async_get": lambda hass: registry}))

    monkeypatch.setattr(helpers, "async_resolve_entity_id", lambda reg, unique_id: next((entity.entity_id for entity in reg.entities.values() if entity.unique_id == unique_id), None))

    asyncio.run(helpers.remove_old_entities(hass=None, config_entry_id="dummy_entry", active_entity_ids={"unique_1"}))
    assert "entity.one" in registry.entities
    assert "entity.two" not in registry.entities


def test_generate_unique_id_normal():
    uid = helpers.generate_unique_id(modbus_address=100, supported_version=1, name="Test Sensor")
    assert uid == "100_1_Test_Sensor"


def test_generate_unique_id_special_chars():
    uid = helpers.generate_unique_id(modbus_address=100, supported_version=1, name="@@@")
    assert uid == "100_1"


@pytest.mark.asyncio
async def test_write_modbus_value_success():
    response = DummyResponse(error=False)
    dummy_modbus = DummyModbus(response, connect_success=True)
    result = await helpers.write_modbus_value(dummy_modbus, address=10, value=123)
    assert result is True
    assert dummy_modbus.called_close is True


@pytest.mark.asyncio
async def test_write_modbus_value_error_response():
    response = DummyResponse(error=True)
    dummy_modbus = DummyModbus(response, connect_success=True)
    result = await helpers.write_modbus_value(dummy_modbus, address=10, value=123)
    assert result is False
    assert dummy_modbus.called_close is True


@pytest.mark.asyncio
async def test_write_modbus_value_connection_exception():
    dummy_modbus = DummyModbus(DummyResponse(error=False), connect_success=False)
    result = await helpers.write_modbus_value(dummy_modbus, address=10, value=123)
    assert result is False
    assert dummy_modbus.called_close is True


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


def test_generate_device_info_invalid_version():
    data = {
        DEVICE_VERSION: "abc",
        "VERSIONSC": "1.0.1",
        "VERSIONNBG": "1.0",
    }
    entry = DummyConfigEntry(data)
    host = "192.168.1.100"
    name = "TestDevice"
    info = helpers.generate_device_info(entry, host, name)

    assert info["model"] == "Solvis Control (unbekannt)"


@pytest.mark.asyncio
async def test_fetch_modbus_value_no_modbus_client(monkeypatch):
    host, port = "127.0.0.1", 502

    monkeypatch.setattr(helpers, "ModbusClient", type("DummyModule", (), {"AsyncModbusTcpClient": lambda host, port: None}))
    with pytest.raises(ConnectionException) as excinfo:
        await helpers.fetch_modbus_value(register=10, register_type=1, host=host, port=port)
    assert f"Failed to initialize Modbus client for {host}:{port}" in str(excinfo.value)


class DummyModbusClientConnectFalse:
    DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

    async def connect(self):
        return False

    async def read_input_registers(self, address, count):
        pass

    async def read_holding_registers(self, address, count):
        pass

    def close(self):
        pass

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0]


@pytest.mark.asyncio
async def test_fetch_modbus_value_connect_fail(monkeypatch):
    host, port = "127.0.0.1", 502
    monkeypatch.setattr(helpers, "ModbusClient", type("DummyModule", (), {"AsyncModbusTcpClient": lambda host, port: DummyModbusClientConnectFalse()}))
    with pytest.raises(ConnectionException) as excinfo:
        await helpers.fetch_modbus_value(register=10, register_type=1, host=host, port=port)
    assert f"Failed to connect to Modbus device at {host}:{port}" in str(excinfo.value)


class DummyModbusClientInvalidResponse:
    DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

    async def connect(self):
        return True

    async def read_input_registers(self, address, count):
        class DummyResponse:
            registers = []

        return DummyResponse()

    async def read_holding_registers(self, address, count):
        class DummyResponse:
            registers = []

        return DummyResponse()

    def close(self):
        pass

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0] if registers else None


@pytest.mark.asyncio
async def test_fetch_modbus_value_invalid_response(monkeypatch):
    host, port = "127.0.0.1", 502
    monkeypatch.setattr(helpers, "ModbusClient", type("DummyModule", (), {"AsyncModbusTcpClient": lambda host, port: DummyModbusClientInvalidResponse()}))
    with pytest.raises(ModbusException) as excinfo:
        await helpers.fetch_modbus_value(register=10, register_type=1, host=host, port=port)
    assert f"Invalid response from Modbus for register 10" in str(excinfo.value)


class DummyModbusClientHolding:
    DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

    async def connect(self):
        return True

    async def read_input_registers(self, address, count):
        raise Exception("read_input_registers should not be called")

    async def read_holding_registers(self, address, count):
        class DummyResponse:
            registers = [456]

        return DummyResponse()

    def close(self):
        pass

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0]


@pytest.mark.asyncio
async def test_fetch_modbus_value_holding_registers(monkeypatch):
    host, port = "127.0.0.1", 502
    monkeypatch.setattr(helpers, "ModbusClient", type("DummyModule", (), {"AsyncModbusTcpClient": lambda host, port: DummyModbusClientHolding()}))
    result = await helpers.fetch_modbus_value(register=20, register_type=0, host=host, port=port)
    assert result == 456


class DummyModbusClientCloseException:
    DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

    async def connect(self):
        return True

    async def read_input_registers(self, address, count):
        class DummyResponse:
            registers = [789]

        return DummyResponse()

    async def read_holding_registers(self, address, count):
        class DummyResponse:
            registers = [789]

        return DummyResponse()

    def close(self):
        raise Exception("Close failed")

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0]


@pytest.mark.asyncio
async def test_fetch_modbus_value_close_exception(monkeypatch, caplog):
    host, port = "127.0.0.1", 502
    monkeypatch.setattr(helpers, "ModbusClient", type("DummyModule", (), {"AsyncModbusTcpClient": lambda host, port: DummyModbusClientCloseException()}))
    result = await helpers.fetch_modbus_value(register=10, register_type=1, host=host, port=port)

    assert result == 789

    assert "Error while closing Modbus connection: Close failed" in caplog.text


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


@pytest.mark.asyncio
async def test_write_modbus_value_modbus_exception():

    class DummyModbus:
        async def connect(self):
            return True

        async def write_register(self, address, value, slave=1):
            raise ModbusException("Test modbus error")

        def close(self):
            pass

    dummy = DummyModbus()
    result = await helpers.write_modbus_value(dummy, address=10, value=123)
    assert result is False


@pytest.mark.asyncio
async def test_write_modbus_value_generic_exception():
    class DummyModbus:
        async def connect(self):
            return True

        async def write_register(self, address, value, slave=1):
            raise Exception("Generic error")

        def close(self):
            pass

    dummy = DummyModbus()
    result = await helpers.write_modbus_value(dummy, address=10, value=123)
    assert result is False


@pytest.mark.asyncio
async def test_write_modbus_value_close_exception(monkeypatch, caplog):
    class DummyResponse:
        def isError(self):
            return False

    class DummyModbus:
        async def connect(self):
            return True

        async def write_register(self, address, value, slave=1):
            return DummyResponse()

        def close(self):
            raise Exception("Close error")

    dummy = DummyModbus()
    result = await helpers.write_modbus_value(dummy, address=10, value=123)

    assert result is True
    assert "Error while closing Modbus connection: Close error" in caplog.text


def test_should_not_skip_register_tuple_all_true():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: True, CONF_OPTION_2: True}
    reg = DummyRegister(name="sensor", address=10, conf_option=(1, 2), supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is False


def test_should_skip_register_tuple_missing_option():
    entry_data = {DEVICE_VERSION: "1", CONF_OPTION_1: True, CONF_OPTION_2: False}
    reg = DummyRegister(name="sensor", address=10, conf_option=(1, 2), supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is True


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


def test_should_skip_register_sc3_for_sc2():
    entry_data = {DEVICE_VERSION: "2", CONF_OPTION_1: True}
    reg = DummyRegister(name="sensor", address=10, conf_option=1, supported_version=1)

    assert helpers.should_skip_register(entry_data, reg) is True


def test_should_skip_register_invalid_device_version():
    entry_data = {DEVICE_VERSION: "invalid", CONF_OPTION_1: True}
    reg = DummyRegister("sensor", 10, 0, 2)  # supported_version=2

    assert helpers.should_skip_register(entry_data, reg) is False
