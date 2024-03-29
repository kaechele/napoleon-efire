"""Platform for shared base classes for sensors."""

from __future__ import annotations

import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NapoleonEfireDataUpdateCoordinator


class NapoleonEfireEntity(CoordinatorEntity[NapoleonEfireDataUpdateCoordinator]):
    """Define a generic class for Napoleon eFIRE entities."""

    _attr_has_entity_name = True
    key: str | None = None

    def __init__(
        self,
        coordinator: NapoleonEfireDataUpdateCoordinator,
        description: EntityDescription | None = None,
    ) -> None:
        """Class initializer."""
        super().__init__(coordinator=coordinator)

        self.fireplace = coordinator.device
        self._attr_device_info = DeviceInfo(
            name=self.fireplace.name,
            manufacturer="Napoleon",
            model="W190-0090",
            connections={(dr.CONNECTION_BLUETOOTH, self.fireplace.address)},
            identifiers={(DOMAIN, self.fireplace.address)},
            sw_version=f"v{self.fireplace.state.ble_version}",
            hw_version=f"v{self.fireplace.state.mcu_version}",
        )

        if description:
            self.entity_description = description
            self._attr_unique_id = f"{self.fireplace.name}_{description.key}"
        elif self.key:
            self._attr_unique_id = f"{self.fireplace.name}_{self.key}"
