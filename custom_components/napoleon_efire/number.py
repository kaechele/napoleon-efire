"""Napoleon eFIRE flame height number entity."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NapoleonEfireEntity
from .models import FireplaceData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fans."""
    data: FireplaceData = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([NapoleonEfireFlameControlEntity(coordinator=data.coordinator)])


class NapoleonEfireFlameControlEntity(NapoleonEfireEntity, NumberEntity):
    """Flame height control entity."""

    _attr_native_max_value: float = 6
    _attr_native_min_value: float = 0
    _attr_native_step: float = 1
    _attr_mode: NumberMode = NumberMode.SLIDER
    _attr_translation_key = "flame_height"
    _attr_icon = "mdi:arrow-expand-vertical"

    key = _attr_translation_key

    @property
    def native_value(self) -> float | None:
        """Return the current Flame Height setting."""
        return self.fireplace.state.flame_height

    async def async_set_native_value(self, value: float) -> None:
        """Slider change."""
        native_value: int = int(value)
        _LOGGER.debug(
            "[%s] Set flame height to %d with raw value %s",
            self.fireplace.name,
            value,
            native_value,
        )
        await self.fireplace.set_flame_height(native_value)
        if native_value == 0:
            await self.fireplace.power_off()
        await self.coordinator.async_refresh()
