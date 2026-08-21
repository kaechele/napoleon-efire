"""Napoleon eFIRE flame.

The burner is modelled as a heater, not as a light. A light is a legitimate target
for area-wide commands — `light.turn_on` against an area, "turn on the lights" via
a voice assistant, a blanket script — and for this device that ignites gas. Nothing
in the light domain distinguishes a burner from the LED strip beside it.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature

from .const import (
    DOMAIN,
    FLAME_HEIGHT_MAX,
    FLAME_HEIGHT_MIN,
    FLAME_HEIGHT_OFF,
    FLAME_KEY,
)
from .entity import NapoleonEfireEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .models import FireplaceData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the flame entity."""
    data: FireplaceData = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([EfireFlame(coordinator=data.coordinator)])


class EfireFlame(NapoleonEfireEntity, ClimateEntity):
    """Flame (as heater) entity."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_preset_modes = [
        str(height) for height in range(FLAME_HEIGHT_MIN, FLAME_HEIGHT_MAX + 1)
    ]
    _attr_supported_features = (
        ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    # ClimateEntity requires a unit even when it reports no temperature. The IFC
    # exposes neither a current temperature nor a setpoint, so nothing reads this.
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_translation_key = FLAME_KEY

    key = _attr_translation_key

    @property
    def icon(self) -> str:
        """Return appropriate icon for flame entity."""
        return "mdi:fireplace" if self.fireplace.state.power else "mdi:fireplace-off"

    @property
    def hvac_mode(self) -> HVACMode:
        """Return whether the burner is lit."""
        if self.fireplace.state.flame_height >= FLAME_HEIGHT_MIN:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def preset_mode(self) -> str | None:
        """Return the current flame height, or None when the burner is out."""
        height = self.fireplace.state.flame_height
        return str(height) if height >= FLAME_HEIGHT_MIN else None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Light or extinguish the burner."""
        if hvac_mode == HVACMode.OFF:
            await self._async_set_flame_height(FLAME_HEIGHT_OFF)
            return
        # Ignite at the LOWEST height, not the highest. A caller that wants a
        # specific height asks for it via the preset; a bare turn-on carries no
        # such intent, and defaulting a gas burner to maximum is not a safe
        # reading of "on".
        await self._async_set_flame_height(FLAME_HEIGHT_MIN)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the flame height."""
        await self._async_set_flame_height(int(preset_mode))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light the burner."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Extinguish the burner."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def _async_set_flame_height(self, height: int) -> None:
        """Set flame height, which implicitly powers the fireplace on or off.

        Setting a non-zero height also calls power_on inside the bonaparte library,
        so there is no separate power command to issue here.
        """
        await self.fireplace.set_flame_height(height)
        await self.coordinator.async_request_refresh()
