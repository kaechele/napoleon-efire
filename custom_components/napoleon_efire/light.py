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

    efire_lights = [EfireFlame(coordinator=data.coordinator)]

    if data.device.has_night_light:
        efire_lights.append(EfireNightLight(coordinator=data.coordinator))
    else:
        _LOGGER.debug(
            "[%s] Night Light feature disabled on fireplace", data.device.name
        )
    async_add_entities(efire_lights)


class EfireFlame(NapoleonEfireEntity, LightEntity):
    """Flame (as light) entity."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_translation_key = "flame"

    key = _attr_translation_key

    @property
    def brightness(self) -> int:
        """Return the current flame height 0-255."""
        return int((self.fireplace.state.flame_height / 6) * 255)

    @property
    def icon(self) -> str:
        """Return appropriate icon for flame entity."""
        return "mdi:fireplace" if self.fireplace.state.power else "mdi:fireplace-off"

    @property
    def is_on(self) -> bool:
        """Return true if flame is on."""
        return self.fireplace.state.power

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the flame to turn on."""
        flame_height = 6
        if ATTR_BRIGHTNESS in kwargs:
            flame_height = round(kwargs[ATTR_BRIGHTNESS] / 255 * 6)
        # Setting the flame height to a non-zero value will also implicitly
        # call the power_on function in the bonaparte library.
        # Therefor, not calling it explicitly here.
        await self.fireplace.set_flame_height(flame_height)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the flame to turn off."""
        await self.fireplace.power_off()
        await self.coordinator.async_request_refresh()


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

        await self.fireplace.set_night_light_brightness(light_level)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.fireplace.set_night_light_brightness(0)
        await self.coordinator.async_request_refresh()
