"""Fan definition for Efire."""
from __future__ import annotations

import logging
import math
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

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

    if data.device.has_blower:
        async_add_entities([EfireFan(coordinator=data.coordinator)])
    else:
        _LOGGER.debug("[%s] Blower feature disabled on fireplace", data.device.name)


class EfireFan(NapoleonEfireEntity, FanEntity):
    """Fan entity for the fireplace."""

    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_translation_key = "blower"

    key = _attr_translation_key
    speed_range = (1, 6)

    @property
    def is_on(self) -> bool:
        """Return on or off."""
        return self.coordinator.data.blower_speed >= 1

    @property
    def percentage(self) -> int | None:
        """Return fan percentage."""
        return ranged_value_to_percentage(
            self.speed_range, self.coordinator.data.blower_speed
        )

    @property
    def speed_count(self) -> int:
        """Count of supported speeds. In our case the highest setting is equivalent to the number of speed settings."""
        return self.speed_range[1]

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        # Calculate percentage steps

        int_value = math.ceil(percentage_to_ranged_value(self.speed_range, percentage))

        _LOGGER.debug(
            "Setting Fan Speed %d%% (native value: %d)", percentage, int_value
        )
        await self.coordinator.device.set_blower_speed(blower_speed=int_value)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if percentage:
            int_value = math.ceil(
                percentage_to_ranged_value(self.speed_range, percentage)
            )
        else:
            # Turn on to highest setting if no setting is provided
            int_value = self.speed_range[1]
        await self.coordinator.device.set_blower_speed(blower_speed=int_value)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.device.set_blower_speed(blower_speed=0)
        await self.coordinator.async_request_refresh()
