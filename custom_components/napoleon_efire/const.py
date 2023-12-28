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
