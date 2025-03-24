import pytest
import pymodbus.client as ModbusClient

from pymodbus.exceptions import ModbusException
from custom_components.solvis_control.diagnostics import scan_modbus_registers, async_get_config_entry_diagnostics
from custom_components.solvis_control.const import REGISTERS


class DummyResponse:
    def __init__(self, error: bool, registers):
        self._error = error
        self.registers = registers

    def isError(self):
        return self._error


class DummyClient:
    DATATYPE = type("DummyDataType", (), {"INT16": "int16"})

    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def connect(self):
        return True

    async def read_input_registers(self, address, count):
        return DummyResponse(False, [address + 10])

    async def read_holding_registers(self, address, count):
        return DummyResponse(False, [address + 20])

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0]

    def close(self):
        pass


class ExceptionClient:
    DATATYPE = type("DummyDataType", (), {"INT16": "int16"})

    async def connect(self):
        raise ModbusException("Test Modbus failure")

    def close(self):
        pass


@pytest.mark.asyncio
async def test_scan_modbus_registers_input(monkeypatch):
    TestField = type("TestField", (), {})()
    TestField.address = 100
    TestField.register = 1

    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestField])
    monkeypatch.setattr(ModbusClient, "AsyncModbusTcpClient", lambda host, port: DummyClient(host, port))

    result = await scan_modbus_registers("127.0.0.1", 502, 1)

    assert "register_100" in result
    assert result["register_100"] == 110.0


@pytest.mark.asyncio
async def test_scan_modbus_registers_holding(monkeypatch):
    TestField = type("TestField", (), {})()
    TestField.address = 200
    TestField.register = 2

    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestField])
    monkeypatch.setattr(ModbusClient, "AsyncModbusTcpClient", lambda host, port: DummyClient(host, port))

    result = await scan_modbus_registers("127.0.0.1", 502, 2)

    assert "register_200" in result
    assert result["register_200"] == 220.0


@pytest.mark.asyncio
async def test_scan_modbus_registers_error(monkeypatch):
    TestField = type("TestField", (), {})()
    TestField.address = 300
    TestField.register = 1
    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestField])

    class ErrorClient(DummyClient):
        async def read_input_registers(self, address, count):
            return DummyResponse(True, [])

    monkeypatch.setattr(ModbusClient, "AsyncModbusTcpClient", lambda host, port: ErrorClient(host, port))

    result = await scan_modbus_registers("127.0.0.1", 502, 1)

    assert result.get("register_300") == "Error"


@pytest.mark.asyncio
async def test_async_get_config_entry_diagnostics(monkeypatch):
    TestFieldInput = type("TestFieldInput", (), {})()
    TestFieldInput.address = 400
    TestFieldInput.register = 1
    TestFieldHolding = type("TestFieldHolding", (), {})()
    TestFieldHolding.address = 500
    TestFieldHolding.register = 2

    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestFieldInput, TestFieldHolding])
    monkeypatch.setattr(ModbusClient, "AsyncModbusTcpClient", lambda host, port: DummyClient(host, port))

    class DummyEntry:
        data = {
            "host": "127.0.0.1",
            "port": 502,
            "name": "TestEntry",
        }

    entry = DummyEntry()
    diag = await async_get_config_entry_diagnostics(None, entry)

    assert "entry_data" in diag
    assert "modbus_data_input" in diag
    assert "modbus_data_holding" in diag
    assert diag["modbus_data_input"].get("register_400") == 410.0
    assert diag["modbus_data_holding"].get("register_500") == 520.0


async def test_scan_modbus_registers_modbus_exception(monkeypatch):
    """Test that scan_modbus_registers captures a ModbusException and returns an error."""
    monkeypatch.setattr(ModbusClient, "AsyncModbusTcpClient", lambda host, port: ExceptionClient())

    result = await scan_modbus_registers("127.0.0.1", 502, 1)

    assert "error" in result
    assert "Test Modbus failure" in result["error"]
