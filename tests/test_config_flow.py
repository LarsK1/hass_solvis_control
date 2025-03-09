import unittest

import pytest
from unittest.mock import Mock, AsyncMock
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from scapy.all import ARP, Ether

from custom_components.solvis_control.config_flow import SolvisConfigFlow

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

from voluptuous.error import Invalid


@pytest.mark.asyncio
async def test_full_flow(hass, mock_modbus, mock_helpers) -> None:
    """Testet den vollständigen Konfigurations-Flow"""

    # start flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # user input
    user_input = {
        CONF_NAME: "Solvis Heizung Test",
        CONF_HOST: "10.0.0.131",
        CONF_PORT: 502,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"

    # user input
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

    # user input
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


@pytest.mark.asyncio  # OK
async def test_step_user_no_mac_address(hass, mock_modbus, mock_helpers, mocker):
    """Testet den Fall, dass die MAC-Adresse nicht gefunden wird."""
    mocker.patch("custom_components.solvis_control.config_flow.get_mac", return_value=None)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    user_input = {CONF_NAME: "Solvis Fehlerfall", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)
    assert result["type"] == FlowResultType.FORM
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio  # OK
async def test_step_device_invalid_poll_rates(hass, mock_modbus, mock_helpers):
    """Testet die Validierung der Poll-Raten."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 15, POLL_RATE_DEFAULT: 10, POLL_RATE_SLOW: 30}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)
    assert result["type"] == FlowResultType.FORM
    assert "base" in result.get("errors", {})
    assert "poll_rate_invalid_high" in result.get("errors", {}).get("base", "")


@pytest.mark.asyncio  # OK
async def test_step_features_invalid_combination(hass, mock_modbus, mock_helpers):
    """Testet die Validierung von inkonsistenten Feature-Kombinationen."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)
    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 30, POLL_RATE_SLOW: 300}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)
    feature_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], feature_input)
    assert result["type"] == FlowResultType.FORM
    assert "base" in result["errors"]
    assert result["errors"]["base"] == "only_one_temperature_sensor"


@pytest.mark.asyncio
async def test_async_get_options_flow(hass, mock_modbus, mock_helpers):
    """Testet die Initialisierung des Options-Flows analog zum Full-Flow-Test."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 30, POLL_RATE_SLOW: 300}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    features_input = {CONF_OPTION_1: True, CONF_OPTION_2: False}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], features_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    entry = result["result"]

    options_flow = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(options_flow["flow_id"], {})

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"


@pytest.mark.asyncio  # OK
async def test_async_step_options_invalid_connection(hass, mock_modbus, mock_helpers):
    """Testet den Fall, dass die Verbindung im OptionsFlow fehlschlägt analog zum Full-Flow-Test."""
    mock_modbus.set_mock_behavior(fail_connect=True)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    user_input = {CONF_NAME: "Solvis", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    device_input = {DEVICE_VERSION: str(SolvisDeviceVersion.SC3), POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 30, POLL_RATE_SLOW: 300}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    features_input = {CONF_OPTION_1: True, CONF_OPTION_2: False}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], features_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    entry = result["result"]

    options_flow = await hass.config_entries.options.async_init(entry.entry_id)
    user_input = {CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.options.async_configure(options_flow["flow_id"], {})

    assert result["type"] == FlowResultType.FORM
    assert "base" in result.get("errors", {})
    assert result.get("errors", {}).get("base") == "cannot_connect"
