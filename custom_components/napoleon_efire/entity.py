"""Platform for shared base classes for sensors."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.napoleon_efire.const import DOMAIN
from custom_components.napoleon_efire.coordinator import (
    NapoleonEfireDataUpdateCoordinator,
)


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
            connections={(CONNECTION_BLUETOOTH, self.fireplace.address)},
            identifiers={(DOMAIN, self.fireplace.address)},
            sw_version=f"v{self.fireplace.state.ble_version}",
            hw_version=f"v{self.fireplace.state.mcu_version}",
        )

        # The BLE advertised name is not a stable identifier: the same controller
        # may advertise as NAP_FPC_* or as its bare MAC depending on adapter and
        # timing, which orphans every entity whenever it changes. The address is
        # already the stable identifier for the config entry, so use it here too.
        if description:
            self.entity_description = description
            self._attr_unique_id = f"{self.fireplace.address}_{description.key}"
        elif self.key:
            self._attr_unique_id = f"{self.fireplace.address}_{self.key}"
