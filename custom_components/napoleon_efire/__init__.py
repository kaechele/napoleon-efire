"""The Napoleon eFIRE integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from bonaparte import Fireplace
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_PASSWORD,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er

from .const import CONF_FEATURES, DOMAIN, LEGACY_UNIQUE_ID_KEYS
from .coordinator import NapoleonEfireDataUpdateCoordinator
from .models import FireplaceData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.SWITCH,
]

_LOGGER = logging.getLogger(__name__)


async def _async_migrate_unique_ids(
    hass: HomeAssistant, entry: ConfigEntry, address: str
) -> None:
    """Re-key entities from the BLE advertised name onto the device address.

    Entities used to be keyed as `<ble_name>_<key>`, but the advertised name is not
    stable, so a name change orphaned every entity and created a fresh set. Rewrite
    any surviving legacy ID onto `<address>_<key>` so history and automations follow.
    """
    registry = er.async_get(hass)

    @callback
    def _migrator(entity_entry: er.RegistryEntry) -> dict[str, str] | None:
        for key in LEGACY_UNIQUE_ID_KEYS:
            suffix = f"_{key}"
            if not entity_entry.unique_id.endswith(suffix):
                continue
            new_unique_id = f"{address}{suffix}"
            if new_unique_id == entity_entry.unique_id:
                return None
            if (
                existing := registry.async_get_entity_id(
                    entity_entry.domain, DOMAIN, new_unique_id
                )
            ) is not None:
                # A previous name change already produced an entity under the stable
                # ID. Renaming onto it would collide, so leave the stale one for the
                # user to delete rather than failing setup.
                _LOGGER.debug(
                    "Not migrating %s to %s: already held by %s",
                    entity_entry.entity_id,
                    new_unique_id,
                    existing,
                )
                return None
            _LOGGER.debug(
                "Migrating unique ID of %s to %s", entity_entry.entity_id, new_unique_id
            )
            return {"new_unique_id": new_unique_id}
        return None

    await er.async_migrate_entries(hass, entry.entry_id, _migrator)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Napoleon eFIRE from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    password: str = entry.data[CONF_PASSWORD]
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address.upper(), connectable=True
    )
    if not ble_device:
        msg = f"Could not find eFIRE fireplace controller with address {address}"
        raise ConfigEntryNotReady(msg)

    fireplace = Fireplace(ble_device, compatibility_mode=False)
    fireplace.set_features(set(entry.data[CONF_FEATURES]))
    _LOGGER.debug(
        "Fireplace %s initialized. Feature set: %s",
        fireplace.name,
        set(entry.data[CONF_FEATURES]),
    )

    # Keyed off fireplace.address rather than entry.data[CONF_ADDRESS] so the value
    # is byte-identical to the one the entities build their unique IDs from.
    await _async_migrate_unique_ids(hass, entry, fireplace.address)

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
