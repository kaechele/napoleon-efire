"""The Napoleon eFIRE integration."""

from __future__ import annotations

import logging

from bonaparte import Fireplace

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_PASSWORD,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .const import CONF_FEATURES, DOMAIN
from .coordinator import NapoleonEfireDataUpdateCoordinator
from .models import FireplaceData

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.SWITCH,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Napoleon eFIRE from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    password: str = entry.data[CONF_PASSWORD]
    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper(), True)
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find eFIRE fireplace controller with address {address}"
        )

    fireplace = Fireplace(ble_device, compatibility_mode=False)
    fireplace.set_features(set(entry.data[CONF_FEATURES]))
    _LOGGER.debug(
        "Fireplace %s initialized. Feature set: %s",
        fireplace.name,
        set(entry.data[CONF_FEATURES]),
    )

    @callback
    def _async_update_ble(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        _change: bluetooth.BluetoothChange,
    ) -> None:
        """Update from a BLE callback."""
        fireplace.set_ble_device_and_advertisement_data(
            service_info.device, service_info.advertisement
        )

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_update_ble,
            BluetoothCallbackMatcher({ADDRESS: address}),
            bluetooth.BluetoothScanningMode.ACTIVE,
        )
    )

    if not await fireplace.authenticate(password):
        raise ConfigEntryAuthFailed
    coordinator = NapoleonEfireDataUpdateCoordinator(hass, fireplace)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = FireplaceData(
        entry.title, fireplace, coordinator
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_stop(_event: Event) -> None:
        """Close the connection."""
        await fireplace.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data: FireplaceData = hass.data[DOMAIN].pop(entry.entry_id)
        await data.device.disconnect()

    return unload_ok
