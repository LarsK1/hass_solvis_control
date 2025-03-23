import pytest
import asyncio
import logging
import voluptuous as vol

from voluptuous.error import Invalid
from unittest.mock import Mock, AsyncMock, patch
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.config_entries import ConfigEntry
from custom_components.solvis_control.config_flow import SolvisConfigFlow, SolvisOptionsFlow
from custom_components.solvis_control.config_flow import get_solvis_modules_options, get_solvis_devices_options
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

_LOGGER = logging.getLogger("tests.test_config_flow")


class FaultyData(dict):
    def get(self, key, default=None):
        raise KeyError(key)


async def create_test_config_entry(hass) -> ConfigEntry:
    """Create and add a test ConfigEntry"""
    config_data = {
        CONF_NAME: "Solvis",
        CONF_HOST: "10.0.0.131",
        CONF_PORT: 502,
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
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

    config_entry = ConfigEntry(
        version=2,
        minor_version=3,
        domain=DOMAIN,
        title="Solvis",
        data=config_data,
        source="user",
        entry_id="test_entry_id",
        unique_id="00:11:22:33:44:55",
        options={},
        discovery_keys={},
        subentries_data=None,
    )

    await hass.config_entries.async_add(config_entry)
    await hass.async_block_till_done()

    return config_entry


@pytest.mark.asyncio
async def test_debug_modbus_patch(mock_modbus):
    assert mock_modbus is not None
    assert hasattr(mock_modbus, "read_input_registers")


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_config_flow_full(hass, mock_get_mac, mock_modbus) -> None:

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # user input step user
    user_input = {
        CONF_NAME: "Solvis Heizung Test",
        CONF_HOST: "10.0.0.131",
        CONF_PORT: 502,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"

    # user input step device
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "features"

    # user input step features
    feature_input = {
        CONF_OPTION_1: False,
        CONF_OPTION_2: False,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_6: False,
        CONF_OPTION_7: False,
        CONF_OPTION_8: False,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], feature_input)

    # check
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis Heizung Test"

    # check
    assert result["data"] == {
        **user_input,
        **device_input,
        **feature_input,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": None}], indirect=True)
async def test_config_flow_step_user_no_mac_address(hass, mock_get_mac, mock_modbus):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis Fehlerfall", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "cannot_connect"
    assert "device" in result["errors"]
    assert result["errors"]["device"] == "Could not find mac-address of device"


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"fail_connect": True}], indirect=True)
async def test_config_flow_step_user_connection_exception(hass, mock_get_mac, mock_modbus):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis Fehlerfall", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "cannot_connect"
    assert "device" in result["errors"]
    assert "Modbus communication failed" in result["errors"]["device"]


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_async_step_user_unexpected_exception(hass, mock_get_mac, mock_modbus, caplog):

    mock_get_mac.side_effect = RuntimeError("Unbekannter Fehler")

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "errors" in result
    assert result["errors"]["base"] == "unknown"
    assert "Unexpected error in config flow" in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"fail_read": True}], indirect=True)
async def test_config_flow_step_user_fetch_modbus_none(hass, mock_modbus, mock_get_mac):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis Fehlerfall", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "cannot_connect"
    assert "device" in result["errors"]
    assert "Modbus communication failed" in result["errors"]["device"]


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_config_flow_step_device_invalid_poll_rate_high(hass, mock_modbus, mock_get_mac):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # user input step device - invalid poll rate high / default
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 15, POLL_RATE_DEFAULT: 10, POLL_RATE_SLOW: 30}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result.get("errors", {})
    assert "poll_rate_invalid_high" in result.get("errors", {}).get("base", "")


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_config_flow_step_device_invalid_poll_rate_slow(hass, mock_modbus, mock_get_mac):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # user input step device - invalid poll rate slow / default
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 5, POLL_RATE_DEFAULT: 10, POLL_RATE_SLOW: 12}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result.get("errors", {})
    assert "poll_rate_invalid_slow" in result.get("errors", {}).get("base", "")


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_config_flow_step_features_connection_exception(hass, mock_modbus, mock_get_mac, caplog):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert "flow_id" in result
    flow_id = result["flow_id"]

    # user input step user
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(flow_id, user_input)

    # check
    assert result["type"] == FlowResultType.FORM

    # mock modbus connectionException directly after device-step
    mock_modbus.set_mock_behavior(fail_connect=True)

    # user input step device
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 30, POLL_RATE_SLOW: 300}
    result = await hass.config_entries.flow.async_configure(flow_id, device_input)

    # check
    assert "type" in result
    assert result["type"] == FlowResultType.FORM
    assert "[config_flow > async_step_features] Got no value for register 2: setting default 1." in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_config_flow_step_features_invalid_combination(hass, mock_modbus, mock_get_mac):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # user input step device
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 30, POLL_RATE_SLOW: 300}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # user input step features - invalid selection of options 6 AND 7
    feature_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], feature_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "only_one_temperature_sensor"


@pytest.mark.asyncio
async def test_async_step_features_invalid_combination_keyerror_direct(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)

    flow = SolvisConfigFlow()
    flow.data = {
        CONF_NAME: "Solvis",
        CONF_HOST: "10.0.0.131",
        CONF_PORT: 502,
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }

    flow.data = FaultyData(dict(flow.data))

    user_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}
    result = await flow.async_step_features(user_input=user_input)

    assert "KeyError in SolvisConfigFlow" in caplog.text
    assert result["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize(
    "mock_modbus, expected_options",
    [
        ({"32770": [12345], "32771": [56789], 2: [1]}, {CONF_OPTION_1: False, CONF_OPTION_2: False}),
        ({"32770": [12345], "32771": [56789], 2: [2]}, {CONF_OPTION_1: True, CONF_OPTION_2: False}),
        ({"32770": [12345], "32771": [56789], 2: [3]}, {CONF_OPTION_1: True, CONF_OPTION_2: True}),
    ],
    indirect=["mock_modbus"],
)
async def test_config_flow_step_features_hkr_presets(hass, mock_modbus, mock_get_mac, expected_options):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    assert "flow_id" in result
    flow_id = result["flow_id"]

    # user input step user
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(flow_id, user_input)

    # user input step device
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 30, POLL_RATE_SLOW: 300}
    result = await hass.config_entries.flow.async_configure(flow_id, device_input)

    assert "type" in result
    assert result["type"] == FlowResultType.FORM

    # check
    validated_data = result["data_schema"]({})
    for key, expected_value in expected_options.items():
        actual_value = validated_data.get(key, None)
        assert actual_value == expected_value


@pytest.mark.asyncio
async def test_get_solvis_modules_options():

    # set empty data dict
    data = {}

    # get schema
    schema = get_solvis_modules_options(data)

    # check
    assert isinstance(schema, vol.Schema)

    expected_fields = {
        CONF_OPTION_1,
        CONF_OPTION_2,
        CONF_OPTION_3,
        CONF_OPTION_4,
        CONF_OPTION_5,
        CONF_OPTION_6,
        CONF_OPTION_7,
        CONF_OPTION_8,
    }
    assert all(field in schema.schema for field in expected_fields)

    defaults = schema({})
    for field in expected_fields:
        assert defaults[field] is False


@pytest.mark.asyncio
async def test_get_solvis_devices_options_defaults():

    schema = get_solvis_devices_options({})
    validated_data = schema({})

    assert validated_data[DEVICE_VERSION] == str(SolvisDeviceVersion.SC3)
    assert validated_data[POLL_RATE_HIGH] == 10
    assert validated_data[POLL_RATE_DEFAULT] == 30
    assert validated_data[POLL_RATE_SLOW] == 300


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_options_flow_full(hass, mock_get_mac, mock_modbus) -> None:

    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    assert "flow_id" in result

    flow_id = result.get("flow_id")
    assert flow_id is not None

    print(f"DEBUG: Flow ID nach async_init: {flow_id}")
    print(f"DEBUG: Aktuelle Flows nach async_init: {hass.config_entries.options.async_progress()}")

    # user input step init
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"
    flow_id = result.get("flow_id")

    # user input step device
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }
    result = await hass.config_entries.options.async_configure(flow_id, device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "features"

    # user input step features
    feature_input = {
        CONF_OPTION_1: False,
        CONF_OPTION_2: False,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_6: False,
        CONF_OPTION_7: False,
        CONF_OPTION_8: False,
    }
    result = await hass.config_entries.options.async_configure(flow_id, feature_input)

    # check
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis"

    # check
    assert result["data"] == {
        **user_input,
        **device_input,
        **feature_input,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
        "name": "Solvis",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"fail_connect": True}], indirect=True)
async def test_options_flow_step_init_connection_exception(hass, mock_get_mac, mock_modbus) -> None:

    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    flow_id = result.get("flow_id")

    # user input step init
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "cannot_connect"
    assert "device" in result["errors"]
    assert "Modbus communication failed" in result["errors"]["device"]


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"fail_read": True}], indirect=True)
async def test_options_flow_step_init_fetch_modbus_none(hass, mock_get_mac, mock_modbus) -> None:

    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    flow_id = result.get("flow_id")

    # user input step init
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "cannot_connect"
    assert "device" in result["errors"]
    assert "Modbus communication failed" in result["errors"]["device"]


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_options_flow_step_device_invalid_poll_rate(hass, mock_get_mac, mock_modbus) -> None:

    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    flow_id = result.get("flow_id")

    # user input step init
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)

    # user input step device - invalid poll rate high / default
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 15,
        POLL_RATE_DEFAULT: 10,
        POLL_RATE_SLOW: 30,
    }
    expected_schema = get_solvis_devices_options(config_entry.data)
    print(f"DEBUG: Erwartetes Schema für device step: {expected_schema.schema}")
    print(f"DEBUG: Device Input: {device_input}")
    result = await hass.config_entries.options.async_configure(flow_id, device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result.get("errors", {})
    assert "poll_rate_invalid_high" in result.get("errors", {}).get("base", "")


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_options_flow_step_features_invalid_combination(hass, mock_get_mac, mock_modbus) -> None:

    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    flow_id = result.get("flow_id")

    # user input step init
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)

    # user input step device
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }
    result = await hass.config_entries.options.async_configure(flow_id, device_input)

    # user input step features - invalid selection of options 6 AND 7
    feature_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}
    result = await hass.config_entries.options.async_configure(flow_id, feature_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "only_one_temperature_sensor"


@pytest.mark.asyncio
async def test_options_flow_invalid_combination_keyerror_direct(hass, monkeypatch, caplog, mock_config_entry):
    caplog.set_level(logging.DEBUG)

    if not hasattr(mock_config_entry, "options"):
        mock_config_entry.options = {}

    flow = SolvisOptionsFlow(mock_config_entry)
    flow.hass = hass
    flow.handler = "dummy"
    monkeypatch.setattr(hass.config_entries, "async_update_entry", lambda entry, options: None)
    monkeypatch.setattr(hass.config_entries, "async_get_known_entry", lambda entry_id: mock_config_entry)

    flow.data = FaultyData(dict(flow.data))

    user_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}
    result = await flow.async_step_features(user_input=user_input)

    assert "KeyError in SolvisConfigFlow" in caplog.text
    assert result["type"] == FlowResultType.CREATE_ENTRY
