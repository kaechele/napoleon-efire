"""Config flow for Napoleon eFIRE integration."""
from __future__ import annotations

import logging
from typing import Any

from bleak_retry_connector import BLEDevice
from bluetooth_data_tools import human_readable_name
from bonaparte import Fireplace
from bonaparte.const import Feature
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_FEATURES, DOMAIN, LOCAL_NAME_PREFIX, UNSUPPORTED_FEATURES

AVAILABLE_FEATURES = {f.value for f in Feature if f.value not in UNSUPPORTED_FEATURES}

FEATURES_SCHEMA = {
    # replace selector.BooleanSelector() with bool once
    # https://github.com/home-assistant/frontend/issues/15536 is fixed
    vol.Required(feature, default=False): selector.BooleanSelector()
    for feature in AVAILABLE_FEATURES
}

_LOGGER = logging.getLogger(__name__)


async def async_validate_fireplace_or_error(
    ble_device: BLEDevice, password: str
) -> dict[str, str]:
    """Validate authentication with the fireplace."""
    fp = Fireplace(ble_device)
    auth = await fp.authenticate(password)
    await fp.disconnect()
    if not auth:
        return {CONF_PASSWORD: "invalid_auth"}
    return {}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Napoleon eFIRE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        super().__init__()
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}
        self._init_info: dict[str, Any] | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": human_readable_name(
                None, discovery_info.name, discovery_info.address
            )
        }
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step to pick discovered device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            discovery_info = self._discovered_devices[address]
            password = user_input[CONF_PASSWORD]
            await self.async_set_unique_id(
                discovery_info.address, raise_on_progress=False
            )
            self._abort_if_unique_id_configured()

            if not (
                errors := await async_validate_fireplace_or_error(
                    discovery_info.device, password
                )
            ):
                self._init_info = {
                    "name": discovery_info.name,
                    CONF_ADDRESS: discovery_info.address,
                    CONF_PASSWORD: password,
                }
                return await self.async_step_select_features()

        if discovery := self._discovery_info:
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            for discovery in async_discovered_service_info(self.hass):
                if (
                    discovery.address in current_addresses
                    or discovery.address in self._discovered_devices
                    or not discovery.name.startswith(LOCAL_NAME_PREFIX)
                ):
                    continue
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="no_unconfigured_devices")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        service_info.address: (
                            f"{service_info.name} ({service_info.address})"
                        )
                        for service_info in self._discovered_devices.values()
                    }
                ),
                vol.Optional(CONF_PASSWORD, default="0000"): str,
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_select_features(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Allow the user to select the features available on the fireplace."""
        if user_input is not None and self._init_info is not None:
            supported_features = [
                key
                for (key, value) in user_input.items()
                if key in AVAILABLE_FEATURES and value
            ]
            return self.async_create_entry(
                title=self._init_info["name"],
                data={
                    CONF_ADDRESS: self._init_info[CONF_ADDRESS],
                    CONF_PASSWORD: self._init_info[CONF_PASSWORD],
                    CONF_FEATURES: supported_features,
                },
            )

        errors: dict[str, str] = {}
        data_schema = vol.Schema(FEATURES_SCHEMA)
        return self.async_show_form(
            step_id="select_features", data_schema=data_schema, errors=errors
        )
