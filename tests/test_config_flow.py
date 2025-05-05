"""
Tests for Solvis Control Config Flow

Version: v2.0.0
"""

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
from custom_components.solvis_control.config_flow import SolvisConfigFlow, SolvisOptionsFlow, SolvisRoomTempSelect
from custom_components.solvis_control.config_flow import get_solvis_devices_options, get_solvis_roomtempsensors
from custom_components.solvis_control.const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    MAC,
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
    DEVICE_VERSION,
    SolvisDeviceVersion,
)

_LOGGER = logging.getLogger("tests.test_config_flow")


async def create_test_config_entry(hass) -> ConfigEntry:
    """Create and add a test ConfigEntry"""
    config_data = {
        CONF_NAME: "Solvis",
        CONF_HOST: "10.0.0.131",
        CONF_PORT: 502,
        MAC: "40:33:be:13:b5:98",
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
        CONF_OPTION_9: False,
        CONF_OPTION_10: False,
        CONF_OPTION_11: False,
        CONF_OPTION_12: False,
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
        CONF_OPTION_1: True,
        CONF_OPTION_2: True,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_8: False,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], feature_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "roomtempsensors"

    roomtemp_input = {
        "hkr1_room_temp_sensor": "1",
        "hkr2_room_temp_sensor": "1",
        "hkr3_room_temp_sensor": "1",
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], roomtemp_input)

    # check
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis Heizung Test"

    # check
    expected_data = {
        **user_input,
        **device_input,
        **feature_input,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
        CONF_OPTION_6: True,
        CONF_OPTION_7: False,
        CONF_OPTION_9: True,
        CONF_OPTION_10: False,
        CONF_OPTION_11: True,
        CONF_OPTION_12: False,
    }
    assert result["data"] == expected_data


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
    assert result["errors"]["base"] == "mac_error"
    assert "device" in result["errors"]
    assert result["errors"]["device"] == "Could not find mac-address of device. Please enter the mac-address below manually."


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
    assert "Connection failed" in result["errors"]["device"]


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
async def test_config_flow_step_user_modbus_exception(hass, mock_modbus, mock_get_mac):

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # user input step user
    user_input = {CONF_NAME: "Solvis Fehlerfall", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "modbus_error"
    assert "device" in result["errors"]
    assert "Read failed" in result["errors"]["device"]


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
async def test_get_solvis_devices_options_defaults():

    schema = get_solvis_devices_options({})
    validated_data = schema({})

    assert validated_data[DEVICE_VERSION] == str(SolvisDeviceVersion.SC3)
    assert validated_data[POLL_RATE_HIGH] == 10
    assert validated_data[POLL_RATE_DEFAULT] == 30
    assert validated_data[POLL_RATE_SLOW] == 300


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ({}, {"hkr1_room_temp_sensor": "1"}),
        ({CONF_OPTION_1: True}, {"hkr1_room_temp_sensor": "1", "hkr2_room_temp_sensor": "1"}),
        ({CONF_OPTION_2: True}, {"hkr1_room_temp_sensor": "1", "hkr3_room_temp_sensor": "1"}),
        ({CONF_OPTION_1: True, CONF_OPTION_2: True}, {"hkr1_room_temp_sensor": "1", "hkr2_room_temp_sensor": "1", "hkr3_room_temp_sensor": "1"}),
    ],
)
def test_get_solvis_roomtempsensors(input_data, expected_output):
    schema = get_solvis_roomtempsensors(input_data)
    validated = schema({})
    assert validated == expected_output


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
@pytest.mark.parametrize(
    "conf_option_1, conf_option_2, roomtemp_input, expected_roomtemp_options",
    [
        # Case 1: Only hkr1 is available (CONF_OPTION_1=False, CONF_OPTION_2=False)
        (
            False,
            False,
            {"hkr1_room_temp_sensor": "1"},
            {
                CONF_OPTION_6: True,  # hkr1 == "1"
                CONF_OPTION_7: False,  # hkr1 != "2"
                CONF_OPTION_9: False,  # hkr2 not provided -> False
                CONF_OPTION_10: False,  # hkr2 not provided -> False
                CONF_OPTION_11: False,  # hkr3 not provided -> False
                CONF_OPTION_12: False,  # hkr3 not provided -> False
            },
        ),
        # Case 2: hkr1 and hkr2 available (CONF_OPTION_1=True, CONF_OPTION_2=False)
        (
            True,
            False,
            {"hkr1_room_temp_sensor": "1", "hkr2_room_temp_sensor": "2"},
            {
                CONF_OPTION_6: True,  # hkr1 == "1"
                CONF_OPTION_7: False,  # hkr1 != "2"
                CONF_OPTION_9: False,  # hkr2 != "1"
                CONF_OPTION_10: True,  # hkr2 == "2"
                CONF_OPTION_11: False,  # hkr3 not provided -> False
                CONF_OPTION_12: False,  # hkr3 not provided -> False
            },
        ),
        # Case 3: hkr1, hkr2 und hkr3 verfügbar (CONF_OPTION_1=True, CONF_OPTION_2=True)
        (
            True,
            True,
            {"hkr1_room_temp_sensor": "2", "hkr2_room_temp_sensor": "1", "hkr3_room_temp_sensor": "2"},
            {
                CONF_OPTION_6: False,  # hkr1 != "1"
                CONF_OPTION_7: True,  # hkr1 == "2"
                CONF_OPTION_9: True,  # hkr2 == "1"
                CONF_OPTION_10: False,  # hkr2 != "2"
                CONF_OPTION_11: False,  # hkr3 != "1"
                CONF_OPTION_12: True,  # hkr3 == "2"
            },
        ),
    ],
)
async def test_options_flow_full(hass, mock_get_mac, mock_modbus, conf_option_1, conf_option_2, roomtemp_input, expected_roomtemp_options) -> None:
    # Create test config entry
    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    flow_id = result.get("flow_id")
    assert flow_id is not None

    # Step "init"
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"
    flow_id = result.get("flow_id")

    # Step "device"
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }
    result = await hass.config_entries.options.async_configure(flow_id, device_input)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "features"
    flow_id = result.get("flow_id")

    # Step "features"
    feature_input = {
        CONF_OPTION_1: conf_option_1,
        CONF_OPTION_2: conf_option_2,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_8: False,
    }
    result = await hass.config_entries.options.async_configure(flow_id, feature_input)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "roomtempsensors"
    flow_id = result.get("flow_id")

    # Step "roomtempsensors"
    result = await hass.config_entries.options.async_configure(flow_id, roomtemp_input)
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis"

    # Build expected data merging all inputs and expected room temperature options
    expected_data = {
        **user_input,
        **device_input,
        **feature_input,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
        CONF_NAME: "Solvis",
        **expected_roomtemp_options,
    }
    assert result["data"] == expected_data


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
    assert "Connection failed" in result["errors"]["device"]


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"fail_read": True}], indirect=True)
async def test_options_flow_step_init_modbus_exception(hass, mock_get_mac, mock_modbus) -> None:

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
    assert result["errors"]["base"] == "modbus_error"
    assert "device" in result["errors"]
    assert "Read failed" in result["errors"]["device"]


@pytest.mark.asyncio
async def test_options_flow_step_init_generic_exception(hass, mock_get_mac, mock_modbus):

    async def failing_read_registers(*args, **kwargs):
        raise ValueError("Test generic error")

    mock_modbus.read_input_registers.side_effect = failing_read_registers
    mock_modbus.read_holding_registers.side_effect = failing_read_registers

    config_entry = await create_test_config_entry(hass)

    # >>> start options flow <<<
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    flow_id = result["flow_id"]

    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(flow_id, user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "unknown"
    assert "device" in result["errors"]
    assert "Test generic error" in result["errors"]["device"]


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
    result = await hass.config_entries.options.async_configure(flow_id, device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert "base" in result.get("errors", {})
    assert "poll_rate_invalid_high" in result.get("errors", {}).get("base", "")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_input, expected_options",
    [
        (
            {"hkr1_room_temp_sensor": "1"},
            {CONF_OPTION_9: False, CONF_OPTION_10: False, CONF_OPTION_11: False, CONF_OPTION_12: False},
        ),
        (
            {"hkr1_room_temp_sensor": "1", "hkr2_room_temp_sensor": "2"},
            {CONF_OPTION_9: False, CONF_OPTION_10: True, CONF_OPTION_11: False, CONF_OPTION_12: False},
        ),
        (
            {"hkr1_room_temp_sensor": "1", "hkr3_room_temp_sensor": "1"},
            {CONF_OPTION_9: False, CONF_OPTION_10: False, CONF_OPTION_11: True, CONF_OPTION_12: False},
        ),
    ],
)
async def test_config_flow_step_roomtempsensors(user_input, expected_options):
    flow = SolvisConfigFlow()
    flow.data = {CONF_NAME: "TestDevice"}
    result = await flow.async_step_roomtempsensors(user_input)
    for option, expected in expected_options.items():
        assert flow.data.get(option) == expected
