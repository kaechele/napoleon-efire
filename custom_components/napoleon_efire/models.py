"""The Napoleon eFIRE integration models."""

from __future__ import annotations

from dataclasses import dataclass

from bonaparte import Fireplace

from .coordinator import NapoleonEfireDataUpdateCoordinator


@dataclass
class FireplaceData:
    """Entity data for the Napoleon eFIRE integration."""

    title: str
    device: Fireplace
    coordinator: NapoleonEfireDataUpdateCoordinator
