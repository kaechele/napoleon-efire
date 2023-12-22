"""Napoleon eFIRE lights."""

from __future__ import annotations

import logging
from math import ceil
from typing import Any

from bonaparte.const import LedMode

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NapoleonEfireEntity
from .models import FireplaceData

_LOGGER = logging.getLogger(__name__)

EFFECT_CYCLE = "Cycle"
EFFECT_EMBER_BED = "Ember Bed"

EFFECT_MAP = {EFFECT_CYCLE: LedMode.CYCLE, EFFECT_EMBER_BED: LedMode.EMBER_BED}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light entity."""
    data: FireplaceData = hass.data[DOMAIN][entry.entry_id]

    efire_lights = [EfireFlame(coordinator=data.coordinator)]

    if data.device.has_led_lights:
        efire_lights.append(EfireLed(coordinator=data.coordinator))
    else:
        _LOGGER.debug("[%s] LED Lights feature disabled on fireplace", data.device.name)

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
        return self.fireplace.state.flame_height >= 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the flame to turn on."""
        flame_height = 6
        if ATTR_BRIGHTNESS in kwargs:
            flame_height = min(ceil(kwargs[ATTR_BRIGHTNESS] / 255 * 6), 6)
        # Setting the flame height to a non-zero value will also implicitly
        # call the power_on function in the bonaparte library.
        # Therefor, not calling it explicitly here.
        await self.fireplace.set_flame_height(flame_height)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the flame to turn off."""
        await self.fireplace.set_flame_height(0)
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


class EfireLed(NapoleonEfireEntity, LightEntity):
    """LED light entity."""

    _attr_color_mode = ColorMode.RGB
    _attr_icon = "mdi:led-strip"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_translation_key = "led_lights"
    _attr_effect_list = [EFFECT_CYCLE, EFFECT_EMBER_BED]

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        if self.coordinator.data.led_mode == LedMode.CYCLE:
            return EFFECT_CYCLE
        if self.coordinator.data.led_mode == LedMode.EMBER_BED:
            return EFFECT_EMBER_BED
        return None

    @property
    def is_on(self) -> bool:
        """Return true when LEDs are on."""
        return self.coordinator.data.led

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the current LED color."""
        return self.coordinator.data.led_color

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn LED lights on."""

        if ATTR_RGB_COLOR in kwargs:
            await self.fireplace.set_led_color(kwargs[ATTR_RGB_COLOR])

        if ATTR_EFFECT in kwargs:
            effect = LedMode.HOLD

            if kwargs[ATTR_EFFECT] in EFFECT_MAP:
                effect = EFFECT_MAP[kwargs[ATTR_EFFECT]]

            await self.fireplace.set_led_mode(effect, on=True)

        await self.fireplace.set_led_state(on=True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn LED lights off."""
        await self.fireplace.set_led_state(on=False)
        await self.coordinator.async_request_refresh()
