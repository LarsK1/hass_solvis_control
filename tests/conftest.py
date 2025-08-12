"""
Fixtures for Testing

Version: v2.1.0
"""

import pytest
import logging

from tests.dummies import DummyConfigEntry, DummyEntity, DummyEntityRegistry, DummyRegister
from tests.dummies import DummyModbusClient, DummyModbusResponse, DummyResponseObj
from homeassistant.util import dt as dt_util
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from datetime import timedelta
from custom_components.solvis_control.select import SolvisSelect
from custom_components.solvis_control.sensor import SolvisSensor
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


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.WARNING)

    debug_modules = [
        "custom_components.solvis_control.config_flow",
        "custom_components.solvis_control.utils.helpers",
        "tests.conftest",
    ]

    for module in debug_modules:
        _LOGGER = logging.getLogger(module)
        _LOGGER.setLevel(logging.DEBUG)


@pytest.fixture
def mock_get_mac(mocker, request):

    param = getattr(request, "param", {})
    patch_target = param.get("_patch", "config_flow")
    mac_value = param.get("mac", "00:11:22:33:44:55")

    patch_paths = {
        "config_flow": "custom_components.solvis_control.config_flow.get_mac",
        "helpers": "custom_components.solvis_control.utils.helpers.get_mac",
    }

    return mocker.patch(patch_paths[patch_target], return_value=mac_value)


@pytest.fixture
def mock_modbus(mocker, request):

    _LOGGER = logging.getLogger("tests.conftest")

    def mock_modbus_factory(host="127.0.0.1", port=502):
        _LOGGER.debug(f"[mock_modbus_factory] Creating Mock-Modbus-Client for {host}:{port} with parameters: {locals()}")
        mock_modbus_client = AsyncMock(spec=AsyncModbusTcpClient)
        mock_modbus_client.__aenter__.return_value = mock_modbus_client
        mock_modbus_client.__aexit__.return_value = None
        mock_modbus_client.host = host
        mock_modbus_client.port = port
        mock_modbus_client.DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

        _LOGGER.debug(f"[mock_modbus_factory] Mock-Modbus-Instance created: {mock_modbus_client}")

        async def mock_connect():
            _LOGGER.debug("[mock_modbus_factory] mock.connect() called successfully")
            return True

        mock_modbus_client.convert_from_registers.side_effect = lambda registers, data_type, word_order: registers[0]

        def set_mock_behavior(fail_connect=False, fail_read=False, custom_registers=None):
            _LOGGER.debug(f"[mock_modbus_factory] Setting mock behavior: fail_connect={fail_connect}, fail_read={fail_read}, custom_registers={custom_registers if custom_registers else 'None/Empty'}")

            if fail_connect:

                async def failing_connect():
                    raise ConnectionException("Connection failed")

                mock_modbus_client.connect.side_effect = failing_connect
                type(mock_modbus_client).connected = PropertyMock(return_value=False)

            else:
                mock_modbus_client.connect.side_effect = mock_connect

            if fail_read:

                async def failing_read_registers(*args, **kwargs):
                    raise ModbusException("Read failed")

                mock_modbus_client.read_input_registers.side_effect = failing_read_registers
                mock_modbus_client.read_holding_registers.side_effect = failing_read_registers

            else:
                custom_registers = custom_registers or {}

                async def custom_read_registers(address, count):
                    response_mock = MagicMock()

                    response_mock.isError.return_value = False

                    if address in custom_registers:
                        response_mock.registers = custom_registers[address]
                    else:
                        response_mock.registers = [10001]
                    return response_mock

                mock_modbus_client.read_input_registers.side_effect = custom_read_registers
                mock_modbus_client.read_holding_registers.side_effect = custom_read_registers

        mock_modbus_client.set_mock_behavior = set_mock_behavior

        @property
        def connected(self):
            side_effect = self.connect.side_effect
            return side_effect is None or not isinstance(side_effect, ConnectionException)

        type(mock_modbus_client).connected = connected

        return mock_modbus_client

    param = getattr(request, "param", {})

    _LOGGER.debug(f"[mock_modbus] Parameters: {param}")

    register_values = {int(k): v for k, v in param.items() if str(k).isdigit()}

    mock_modbus_instance = mock_modbus_factory("127.0.0.1", 502)

    mock_modbus_instance.set_mock_behavior(
        fail_connect=param.get("fail_connect", False),
        fail_read=param.get("fail_read", False),
        custom_registers=register_values,
    )

    patch_targets = [
        "pymodbus.client.AsyncModbusTcpClient",
        "custom_components.solvis_control.utils.helpers.AsyncModbusTcpClient",
        "custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient",
    ]

    for target in patch_targets:
        mocker.patch(target, return_value=mock_modbus_instance)

    def mock_init(self, hass, entry):
        super(SolvisModbusCoordinator, self).__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data.get(POLL_RATE_HIGH)),
        )
        self.config_entry = entry
        self.hass = hass
        self.modbus = mock_modbus_instance
        self.host = entry.data.get(CONF_HOST, "127.0.0.1")
        self.port = entry.data.get(CONF_PORT, 502)
        self.option_hkr2 = entry.data.get(CONF_OPTION_1, False)
        self.option_hkr3 = entry.data.get(CONF_OPTION_2, False)
        self.option_solar = entry.data.get(CONF_OPTION_3, False)
        self.option_heatpump = entry.data.get(CONF_OPTION_4, False)
        self.option_heatmeter = entry.data.get(CONF_OPTION_5, False)
        self.option_room_temperature_sensor = entry.data.get(CONF_OPTION_6, False)
        self.option_write_temperature_sensor = entry.data.get(CONF_OPTION_7, False)
        self.option_pv2heat = entry.data.get(CONF_OPTION_8, False)
        self.supported_version = entry.data.get(DEVICE_VERSION, 1)
        self.poll_rate_default = entry.data.get(POLL_RATE_DEFAULT, 10)
        self.poll_rate_slow = entry.data.get(POLL_RATE_SLOW, 30)
        self.poll_rate_high = entry.data.get(POLL_RATE_HIGH, 5)
        _LOGGER.debug(f"[SolvisModbusCoordinator] Verwende Modbus-Instanz: {self.modbus} (ID: {id(self.modbus)}) für {self.host}:{self.port}")

    mocker.patch("custom_components.solvis_control.coordinator.SolvisModbusCoordinator.__init__", mock_init)

    return mock_modbus_instance


@pytest.fixture
def mock_coordinator():
    coordinator = AsyncMock()
    coordinator.data = {"TestEntity": 1}
    coordinator.poll_rate_slow = 30
    coordinator.poll_rate_default = 10
    coordinator.modbus = AsyncMock()
    coordinator.modbus.connect = AsyncMock()
    coordinator.modbus.write_register = AsyncMock()
    coordinator.modbus.close = MagicMock()
    coordinator.supported_version = None
    coordinator.async_add_listener = lambda _callback: None
    return coordinator


@pytest.fixture
def mock_config_entry():
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_HOST: "127.0.0.1",
        CONF_NAME: "TestDevice",
        DEVICE_VERSION: 1,
        POLL_RATE_DEFAULT: 10,
        POLL_RATE_SLOW: 30,
    }
    return entry


@pytest.fixture
def mock_entity_registry(hass):
    return er.async_get(hass)


@pytest.fixture
def mock_platform():
    platform = MagicMock()
    platform.platform_name = "solvis_control"
    platform.domain = "select"
    return platform


@pytest.fixture
def mock_device_info():
    return DeviceInfo(
        identifiers={("solvis", "test_address")},
        connections={("mac", "00:1A:2B:3C:4D:5E")},
        name="Test Device",
        manufacturer="Solvis",
        model="Test Model",
        model_id="SM-1000",
        sw_version="1.0.0",
        hw_version="1.0",
        via_device=("solvis", "hub_identifier"),
        configuration_url="http://192.168.1.100/config",
        suggested_area="Boiler Room",
    )


@pytest.fixture
def dummy_config_entry():
    data = {
        CONF_NAME: "TestDevice",
        CONF_HOST: "127.0.0.1",
        CONF_PORT: 502,
        DEVICE_VERSION: 1,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
        POLL_RATE_HIGH: 10,
        CONF_OPTION_1: False,
        CONF_OPTION_2: False,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_6: False,
        CONF_OPTION_7: False,
        CONF_OPTION_8: False,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
    }
    return DummyConfigEntry(data)


@pytest.fixture
def dummy_entity_registry():
    entities = {
        "entity.one": DummyEntity("unique_1", "entity.one"),
        "entity.two": DummyEntity("unique_2", "entity.two"),
    }
    return DummyEntityRegistry(entities)


@pytest.fixture
def dummy_coordinator(monkeypatch, dummy_config_entry, dummy_entity_registry):
    config_entry = dummy_config_entry
    dummy_modbus = DummyModbusClient()
    config_entry.runtime_data["modbus"] = dummy_modbus

    hass = MagicMock()
    monkeypatch.setattr(er, "async_get", lambda hass_instance: dummy_entity_registry)

    async def fake_executor_job(func, *args, **kwargs):
        return func(*args, **kwargs)

    hass.async_add_executor_job = fake_executor_job

    coordinator = SolvisModbusCoordinator(hass, config_entry)
    return coordinator


@pytest.fixture
def dummy_solvisselect_entity(hass, mock_coordinator, mock_device_info, mock_platform):
    def _factory(
        host="test_host",
        name="Test Entity",
        enabled_by_default=True,
        options=("Option 1", "Option 2"),
        modbus_address=1,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
        platform=None,
        entity_id=None,
    ):
        entity = SolvisSelect(
            coordinator=mock_coordinator,
            device_info=mock_device_info,
            host=host,
            name=name,
            enabled_by_default=enabled_by_default,
            options=options,
            modbus_address=modbus_address,
            data_processing=data_processing,
            poll_rate=poll_rate,
            supported_version=supported_version,
        )
        entity.hass = hass
        entity.platform = platform if platform is not None else mock_platform
        entity.entity_id = entity_id if entity_id is not None else f"select.{name.lower().replace(' ', '_')}"
        return entity

    return _factory


@pytest.fixture
def mock_solvis_sensor(mock_coordinator, mock_device_info):
    """Fixture returning a preconfigured SolvisSensor instance."""
    return SolvisSensor(
        coordinator=mock_coordinator,
        device_info=mock_device_info,
        host="test_host",
        name="Test Number Sensor",
        unit_of_measurement="°C",
        device_class="temperature",
        state_class="measurement",
        entity_category="",
        enabled_by_default=True,
        data_processing=0,
        poll_rate=False,
        supported_version=1,
        modbus_address=1,
        suggested_precision=2,
    )
