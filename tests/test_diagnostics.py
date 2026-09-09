"""
Tests for Solvis Control diagnostics

Version: v2.1.0
"""

import pytest
import pymodbus.client as ModbusClient
import custom_components.solvis_control.diagnostics as diagnostics

from pymodbus.exceptions import ModbusException, ConnectionException
from custom_components.solvis_control.diagnostics import scan_modbus_registers, async_get_config_entry_diagnostics
from custom_components.solvis_control.const import REGISTERS
from contextlib import asynccontextmanager


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

    async def read_input_registers(self, address, count, slave=1):
        return DummyResponse(False, [address + 10 + offset for offset in range(count)])

    async def read_holding_registers(self, address, count, slave=1):
        return DummyResponse(False, [address + 20 + offset for offset in range(count)])

    def convert_from_registers(self, registers, data_type, word_order):
        return registers[0]

    def close(self):
        pass


class ErrorClient(DummyClient):
    async def read_input_registers(self, address, count, slave=1):
        return DummyResponse(True, [])


class ExceptionClient:
    DATATYPE = type("DummyDataType", (), {"INT16": "int16"})

    async def connect(self):
        raise ModbusException("Test Modbus failure")

    def close(self):
        pass


class ErrorReadClient(DummyClient):
    async def read_input_registers(self, address, count, slave=1):
        raise ConnectionException("Test Modbus failure")


class BatchFallbackClient(DummyClient):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.calls = []

    async def read_input_registers(self, address, count, slave=1):
        self.calls.append((address, count, slave))
        if count > 1:
            return DummyResponse(True, [])

        return DummyResponse(False, [address + 100])


@asynccontextmanager
async def error_read_client_cm(host, port, **kwargs):
    client = ErrorReadClient(host, port)
    await client.connect()
    try:
        yield client
    finally:
        client.close()


@asynccontextmanager
async def dummy_client_cm(host, port, **kwargs):
    client = DummyClient(host, port)
    await client.connect()
    try:
        yield client
    finally:
        client.close()


@asynccontextmanager
async def error_client_cm(host, port, **kwargs):
    client = ErrorClient(host, port)
    await client.connect()
    try:
        yield client
    finally:
        client.close()


@asynccontextmanager
async def exception_client_cm(host, port, **kwargs):
    client = ExceptionClient()
    try:
        await client.connect()
    except ModbusException:
        pass
    try:
        yield client
    finally:
        client.close()


@pytest.mark.asyncio
async def test_scan_modbus_registers_input(monkeypatch):
    TestField = type("TestField", (), {})()
    TestField.address = 100
    TestField.register = 1

    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestField])
    monkeypatch.setattr(
        diagnostics,
        "AsyncModbusTcpClient",
        dummy_client_cm,
    )

    result = await scan_modbus_registers("127.0.0.1", 502, 1)

    assert "register_100" in result
    assert result["register_100"] == 110.0


@pytest.mark.asyncio
async def test_scan_modbus_registers_holding(monkeypatch):
    TestField = type("TestField", (), {})()
    TestField.address = 200
    TestField.register = 2

    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestField])
    monkeypatch.setattr(
        diagnostics,
        "AsyncModbusTcpClient",
        dummy_client_cm,
    )

    result = await scan_modbus_registers("127.0.0.1", 502, 2)

    assert "register_200" in result
    assert result["register_200"] == 220.0


@pytest.mark.asyncio
async def test_scan_modbus_registers_error(monkeypatch):
    TestField = type("TestField", (), {})()
    TestField.address = 300
    TestField.register = 1
    monkeypatch.setattr("custom_components.solvis_control.diagnostics.REGISTERS", [TestField])
    monkeypatch.setattr(
        diagnostics,
        "AsyncModbusTcpClient",
        error_client_cm,
    )

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
    monkeypatch.setattr(
        diagnostics,
        "AsyncModbusTcpClient",
        dummy_client_cm,
    )

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
    monkeypatch.setattr(
        diagnostics,
        "AsyncModbusTcpClient",
        error_read_client_cm,
    )
    result = await scan_modbus_registers("127.0.0.1", 502, 1)

    assert "error" in result
    assert "Test Modbus failure" in result["error"]


@pytest.mark.asyncio
async def test_scan_modbus_range_input_batch(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "create_modbus_client",
        dummy_client_cm,
    )

    result = await diagnostics.scan_modbus_range(
        "127.0.0.1",
        502,
        100,
        102,
        register_type=diagnostics.REGISTER_TYPE_INPUT,
        batch_size=3,
        delay=0,
    )

    assert result["results"] == [
        {
            "register": 100,
            "type": "input",
            "raw_uint16": 110,
            "int16": 110,
            "factor10": 11.0,
            "hex": "0x006E",
            "binary": "0000000001101110",
        },
        {
            "register": 101,
            "type": "input",
            "raw_uint16": 111,
            "int16": 111,
            "factor10": 11.1,
            "hex": "0x006F",
            "binary": "0000000001101111",
        },
        {
            "register": 102,
            "type": "input",
            "raw_uint16": 112,
            "int16": 112,
            "factor10": 11.2,
            "hex": "0x0070",
            "binary": "0000000001110000",
        },
    ]
    assert result["errors"] == []


@asynccontextmanager
async def batch_fallback_client_cm(host, port, **kwargs):
    client = BatchFallbackClient(host, port)
    await client.connect()
    try:
        yield client
    finally:
        client.close()


@pytest.mark.asyncio
async def test_scan_modbus_range_falls_back_to_single_reads(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "create_modbus_client",
        batch_fallback_client_cm,
    )

    result = await diagnostics.scan_modbus_range(
        "127.0.0.1",
        502,
        5,
        7,
        register_type=diagnostics.REGISTER_TYPE_INPUT,
        batch_size=3,
        delay=0,
    )

    assert [item["register"] for item in result["results"]] == [5, 6, 7]
    assert [item["raw_uint16"] for item in result["results"]] == [105, 106, 107]
