"""The Napoleon eFIRE integration."""

from __future__ import annotations

import asyncio
import logging

from bonaparte import Fireplace, FireplaceState

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL, UPDATE_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class NapoleonEfireDataUpdateCoordinator(DataUpdateCoordinator[FireplaceState]):
    """Class to manage the polling of the fireplace API."""

    def __init__(
        self,
        hass: HomeAssistant,
        fireplace: Fireplace,
    ) -> None:
        """Initialize the Coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.device = fireplace
        self.data: FireplaceState

    async def async_config_entry_first_refresh(self) -> None:
        """Get mostly static data on first refresh."""
        # Firmware version queries are two separate calls for BLE FW and MCU FW
        # Because it's pretty much static info we update it only upon initial load
        await self.device.update_firmware_version()
        return await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> FireplaceState:
        async with asyncio.timeout(UPDATE_TIMEOUT):
            try:
                await self.device.update_state()
                _LOGGER.debug("Old state: %s", self.data)
                self.data = self.device.state
                _LOGGER.debug("New state: %s", self.data)
            except ConnectionError as exception:
                raise UpdateFailed from exception

        return self.data
