"""The Napoleon eFIRE integration models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonaparte import Fireplace

    from .coordinator import NapoleonEfireDataUpdateCoordinator


@dataclass
class FireplaceData:
    """Entity data for the Napoleon eFIRE integration."""

    title: str
    device: Fireplace
    coordinator: NapoleonEfireDataUpdateCoordinator
