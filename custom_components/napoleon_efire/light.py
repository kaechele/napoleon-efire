"""Napoleon eFIRE lights."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
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
    """Set up the light entity."""
    data: FireplaceData = hass.data[DOMAIN][entry.entry_id]

    if data.device.has_night_light:
        async_add_entities([EfireNightLight(coordinator=data.coordinator)])
    else:
        _LOGGER.debug(
            "[%s] Night Light feature disabled on fireplace", data.device.name
        )


class EfireNightLight(NapoleonEfireEntity, LightEntity):
    """Night Light entity."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_icon = "mdi:lightbulb-night"
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_translation_key = "night_light"

    key = _attr_translation_key

    @property
    def brightness(self) -> int:
        """Return the current brightness 0-255."""
        return int((self.coordinator.data.night_light_brightness / 6) * 255)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.data.night_light_brightness >= 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            light_level = round(kwargs[ATTR_BRIGHTNESS] / 255 * 6)
        else:
            light_level = 6

        result = await self.fireplace.set_night_light_brightness(light_level)
        if result:
            self.coordinator.data.night_light_brightness = light_level
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        result = await self.fireplace.set_night_light_brightness(0)
        if result:
            self.coordinator.data.night_light_brightness = 0
        await self.coordinator.async_request_refresh()
