import asyncio
import struct
import pytest
from unittest.mock import MagicMock
from homeassistant.helpers import entity_registry as er
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.pdu import ExceptionResponse
from tests.dummies import DummyConfigEntry, DummyEntity, DummyEntityRegistry, DummyRegister
from tests.dummies import DummyModbusClient, DummyModbusResponse, DummyResponseObj
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
    DEVICE_VERSION,
    SolvisDeviceVersion,
)


@pytest.fixture
def patch_registers(monkeypatch):
    dummy_register = DummyRegister(
        name="dummy_sensor",
        address=100,
        conf_option=0,  # 0: always process
        supported_version=1,  # fits to device version
        poll_rate=0,  # DEFAULT_POLL_GROUP
        poll_time=0,  # it's polling time!
        reg=1,  # read input register
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    return dummy_register


@pytest.mark.asyncio
async def test_async_update_data_success(dummy_coordinator, patch_registers):
    data = await dummy_coordinator._async_update_data()

    assert "dummy_sensor" in data
    assert data["dummy_sensor"] == 123


@pytest.mark.asyncio
async def test_async_update_data_skip_poll_rate(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="slow_sensor",
        address=200,
        conf_option=0,
        supported_version=1,
        poll_rate=0,  # DEFAULT_POLL_GROUP
        poll_time=5,  # no polling time
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    dummy_coordinator.poll_rate_high = 2
    data = await dummy_coordinator._async_update_data()

    assert "slow_sensor" not in data
    assert dummy_register.poll_time == 3


@pytest.mark.asyncio
async def test_async_update_data_invalid_response(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="invalid_sensor",
        address=300,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])

    async def invalid_read(address, count):
        class DummyResponse:
            registers = []

        return DummyResponse()

    dummy_modbus = dummy_coordinator.modbus
    dummy_modbus.read_input_registers = invalid_read
    data = await dummy_coordinator._async_update_data()

    assert "invalid_sensor" not in data


@pytest.mark.asyncio
async def test_async_update_data_modbus_exception(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="error_sensor",
        address=400,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])

    async def raise_exception(address, count):
        raise ModbusException("Test modbus error")

    dummy_modbus = dummy_coordinator.modbus
    dummy_modbus.read_input_registers = raise_exception
    data = await dummy_coordinator._async_update_data()

    assert "error_sensor" not in data


@pytest.mark.asyncio
async def test_poll_rate_slow_reset(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="slow_sensor_reset",
        address=250,
        conf_option=0,
        supported_version=1,
        poll_rate=1,  # SLOW_POLL_GROUP
        poll_time=0,  # reset: <= 0
        reg=1,  # Input
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    data = await dummy_coordinator._async_update_data()
    assert "slow_sensor_reset" in data
    assert dummy_register.poll_time == dummy_coordinator.poll_rate_slow


@pytest.mark.asyncio
async def test_poll_rate_default_reset(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="default_sensor_reset",
        address=350,
        conf_option=0,
        supported_version=1,
        poll_rate=0,  # DEFAULT_POLL_GROUP
        poll_time=0,  # reset: <= 0
        reg=1,  # Input
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    data = await dummy_coordinator._async_update_data()
    assert "default_sensor_reset" in data
    assert dummy_register.poll_time == dummy_coordinator.poll_rate_default


@pytest.mark.asyncio
async def test_skip_disabled_entity(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="disabled_sensor",
        address=500,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    dummy_registry = DummyEntityRegistry({"entity.one": DummyEntity("unique_1", "entity.one", disabled=True)})
    entity_id = f"{DOMAIN}.{dummy_register.name}"
    dummy_registry.entities = {entity_id: MagicMock(disabled=True)}
    monkeypatch.setattr(er, "async_get", lambda hass: dummy_registry)
    data = await dummy_coordinator._async_update_data()

    assert entity_id not in data


@pytest.mark.asyncio
async def test_exception_response(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="exception_sensor",
        address=600,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )

    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])

    class DummyExceptionResponse:
        pass

    dummy_modbus = dummy_coordinator.modbus

    async def exception_response(address, count):
        return DummyExceptionResponse()

    dummy_modbus.read_input_registers = exception_response
    entity_id = f"{dummy_register.name}"
    data = await dummy_coordinator._async_update_data()
    assert entity_id not in data


@pytest.mark.asyncio
async def test_data_conversion_error(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="conversion_error_sensor",
        address=700,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    dummy_modbus = dummy_coordinator.modbus

    def raise_value_error(registers, data_type, word_order):
        raise ValueError("Conversion error")

    dummy_modbus.convert_from_registers = raise_value_error
    entity_id = f"{dummy_register.name}"
    data = await dummy_coordinator._async_update_data()
    assert entity_id in data
    assert data[entity_id] == -300


@pytest.mark.asyncio
async def test_connection_exception(dummy_coordinator, monkeypatch):
    dummy_modbus = dummy_coordinator.modbus

    async def raise_connection_exception():
        raise ConnectionException("Connection failed")

    dummy_modbus.connect = raise_connection_exception
    data = await dummy_coordinator._async_update_data()
    assert data == {}


@pytest.mark.asyncio
async def test_close_exception(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="normal_sensor",
        address=800,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])
    dummy_modbus = dummy_coordinator.modbus

    def raise_exception():
        raise Exception("Close error")

    dummy_modbus.close = raise_exception
    entity_id = f"{dummy_register.name}"

    data = await dummy_coordinator._async_update_data()
    assert entity_id in data
    assert data[entity_id] == 123


@pytest.mark.asyncio
async def test_exception_response_instance(dummy_coordinator, monkeypatch):
    dummy_register = DummyRegister(
        name="exception_sensor_real",
        address=600,
        conf_option=0,
        supported_version=1,
        poll_rate=0,
        poll_time=0,
        reg=1,
        multiplier=1.0,
        absolute_value=False,
        byte_swap=0,
    )
    monkeypatch.setattr("custom_components.solvis_control.coordinator.REGISTERS", [dummy_register])

    async def exception_response(address, count):
        return ExceptionResponse(1)

    dummy_modbus = dummy_coordinator.modbus
    dummy_modbus.read_input_registers = exception_response

    data = await dummy_coordinator._async_update_data()
    assert dummy_register.name not in data
