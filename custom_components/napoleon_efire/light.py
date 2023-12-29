"""Napoleon eFIRE lights."""

from __future__ import annotations

import logging
from math import ceil
from typing import Any

from bonaparte.const import LedMode

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.color as color_util

from .const import DOMAIN
from .entity import NapoleonEfireEntity
from .models import FireplaceData

_LOGGER = logging.getLogger(__name__)

EFFECT_HOLD = "Hold"
EFFECT_CYCLE = "Cycle"
EFFECT_EMBER_BED = "Ember Bed"

EFFECT_MAP = {
    EFFECT_HOLD: LedMode.HOLD,
    EFFECT_CYCLE: LedMode.CYCLE,
    EFFECT_EMBER_BED: LedMode.EMBER_BED,
}


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
        _LOGGER.debug("[%s] LED Lights feature enabled on fireplace", data.device.name)
    else:
        _LOGGER.debug("[%s] LED Lights feature disabled on fireplace", data.device.name)

    if data.device.has_night_light:
        efire_lights.append(EfireNightLight(coordinator=data.coordinator))
        _LOGGER.debug("[%s] Night Light feature enabled on fireplace", data.device.name)
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

    _attr_color_mode = ColorMode.HS
    _attr_effect_list = [EFFECT_HOLD, EFFECT_CYCLE, EFFECT_EMBER_BED]
    _attr_icon = "mdi:led-strip"
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_translation_key = "led_lights"

    key = _attr_translation_key

    @property
    def _hsv_color(self) -> tuple[float, float, float]:
        rgb = self.coordinator.data.led_color
        return color_util.color_RGB_to_hsv(*rgb)

    @property
    def brightness(self) -> int:
        """Return the LED brightness."""
        return int((self._hsv_color[2] / 100) * 255)

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        if self.coordinator.data.led_mode == LedMode.CYCLE:
            return EFFECT_CYCLE
        if self.coordinator.data.led_mode == LedMode.EMBER_BED:
            return EFFECT_EMBER_BED
        return EFFECT_HOLD

    @property
    def hs_color(self) -> [float, float]:
        """Return the LED HS color."""
        return self._hsv_color[:2]

    @property
    def is_on(self) -> bool:
        """Return true when LEDs are on."""
        return self.coordinator.data.led

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn LED lights on."""

        brightness = self.brightness
        hs_color = self.hs_color

        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]

        if ATTR_HS_COLOR in kwargs:
            hs_color = kwargs[ATTR_HS_COLOR]

        rgb = color_util.color_hsv_to_RGB(
            hs_color[0], hs_color[1], brightness / 255 * 100
        )

        await self.fireplace.set_led_color(rgb)

        if ATTR_EFFECT in kwargs:
            if kwargs[ATTR_EFFECT] in EFFECT_MAP:
                effect_selected = kwargs[ATTR_EFFECT] != EFFECT_HOLD
                effect = EFFECT_MAP[
                    kwargs[ATTR_EFFECT] if effect_selected else self.effect
                ]
                await self.fireplace.set_led_mode(
                    effect,
                    on=effect_selected,
                )

        await self.fireplace.set_led_state(on=True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn LED lights off."""
        await self.fireplace.set_led_state(on=False)
        await self.coordinator.async_request_refresh()
