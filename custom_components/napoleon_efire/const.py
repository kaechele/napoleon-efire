"""Constants for the Napoleon eFIRE integration."""

from datetime import timedelta

DOMAIN = "napoleon_efire"

# Config Flow constants
CONF_FEATURES = "features"
LOCAL_NAME_PREFIX = "NAP_FPC_"

# List of features supported by the bonaparte library but not by this component
# - The controller's timer feature is not supported and probably should not be implemented
#   This feature can be achieved using automations from within Home Assistant instead
UNSUPPORTED_FEATURES = ["timer"]

# Coordinator constants
UPDATE_INTERVAL = timedelta(seconds=30)
UPDATE_TIMEOUT = 15  # seconds

# Entity keys that were part of the legacy `<ble_name>_<key>` unique ID scheme.
# This list is deliberately frozen: it exists only to recognise IDs written before
# the switch to `<address>_<key>`, so keys added later never belong in it.
LEGACY_UNIQUE_ID_KEYS = (
    "aux",
    "blower",
    "continuous_pilot",
    "flame",
    "led_lights",
    "night_light",
    "split_flow",
)

# Flame height, as the IFC reports and accepts it
FLAME_HEIGHT_OFF = 0
FLAME_HEIGHT_MIN = 1
FLAME_HEIGHT_MAX = 6

# Entity key of the burner, shared by the climate entity and the migration that
# clears out the light entity it used to be.
FLAME_KEY = "flame"
