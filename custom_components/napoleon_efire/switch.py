"""Define switch func."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from bonaparte import Fireplace, FireplaceState
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NapoleonEfireEntity
from .models import FireplaceData


@dataclass
class EfireSwitchRequiredKeysMixin:
    """Mixin for required keys."""

    on_fn: Callable[[Fireplace], Awaitable]
    off_fn: Callable[[Fireplace], Awaitable]
    value_fn: Callable[[FireplaceState], bool]


@dataclass
class EfireSwitchEntityDescription(
    SwitchEntityDescription, EfireSwitchRequiredKeysMixin
):
    """Describes a switch entity."""


EFIRE_SWITCHES: tuple[EfireSwitchEntityDescription, ...] = (
    EfireSwitchEntityDescription(
        key="on_off",
        translation_key="flame",
        icon="mdi:fire",
        on_fn=lambda device: device.power_on(),
        off_fn=lambda device: device.power_off(),
        value_fn=lambda data: data.power,
    ),
    EfireSwitchEntityDescription(
        key="continuous_pilot",
        translation_key="continuous_pilot",
        icon="mdi:candle",
        on_fn=lambda device: device.set_continuous_pilot(enabled=True),
        off_fn=lambda device: device.set_continuous_pilot(enabled=False),
        value_fn=lambda data: data.pilot,
    ),
    EfireSwitchEntityDescription(
        key="split_flow",
        translation_key="split_flow",
        icon="mdi:call-split",
        on_fn=lambda device: device.set_split_flow(enabled=True),
        off_fn=lambda device: device.set_split_flow(enabled=False),
        value_fn=lambda data: data.split_flow,
    ),
    EfireSwitchEntityDescription(
        key="aux",
        translation_key="aux",
        icon="mdi:electric-switch",
        on_fn=lambda device: device.set_aux(enabled=True),
        off_fn=lambda device: device.set_aux(enabled=False),
        value_fn=lambda data: data.aux,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure switch entities."""
    data: FireplaceData = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        EfireSwitch(coordinator=data.coordinator, description=description)
        for description in EFIRE_SWITCHES
        if description.key in ["on_off", "continuous_pilot"]
        or getattr(data.device.features, description.key, False)
    )


class EfireSwitch(NapoleonEfireEntity, SwitchEntity):
    """Define an Efire Switch."""

    entity_description: EfireSwitchEntityDescription

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self.entity_description.on_fn(self.coordinator.device)
        await self.async_update_ha_state(force_refresh=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self.entity_description.off_fn(self.coordinator.device)
        await self.async_update_ha_state(force_refresh=True)

    @property
    def is_on(self) -> bool | None:
        """Return the on state."""
        return self.entity_description.value_fn(self.coordinator.data)
