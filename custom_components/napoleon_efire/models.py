"""The Napoleon eFIRE integration models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .const import CONF_FEATURES

if TYPE_CHECKING:
    from bonaparte import Fireplace
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import NapoleonEfireDataUpdateCoordinator


@dataclass
class FireplaceData:
    """Entity data for the Napoleon eFIRE integration."""

    title: str
    device: Fireplace
    coordinator: NapoleonEfireDataUpdateCoordinator


def configured_features(entry: ConfigEntry) -> set[str]:
    """Return the feature set the user has declared for this fireplace.

    Options win over data: the feature list was originally captured only at setup, so
    entries created before the options flow existed carry it in `data` and have no
    `options` at all. Reading options first makes a later correction take effect while
    leaving those entries working untouched.
    """
    if CONF_FEATURES in entry.options:
        return set(entry.options[CONF_FEATURES])
    return set(entry.data[CONF_FEATURES])
