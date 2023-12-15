# Napoleon eFIRE Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs] ![Project Maintenance][maintenance-shield]

Integrate your Napoleon eFIRE Bluetooth controlled fireplace into Home
Assisstant. Works best with an
[ESPHome Bluetooth Proxy](https://esphome.github.io/bluetooth-proxies/).

**This integration will set up the following platforms:**

| Platform | Description                                                                                   |
| -------- | --------------------------------------------------------------------------------------------- |
| `fan`    | Controls the optional 6-speed blower fan.                                                     |
| `light`  | Controls the optional light kit. The optional LED controller is not yet implemented.          |
| `number` | Allows setting the flame height on a scale of 1 to 6.                                         |
| `switch` | Controls the main power as well as auxillary power, continuous pilot and split flow settings. |

## Implemented features and controls

1. AUX relay (Switch entity, _optional_)

   A high voltage relay on the IFC, fed from the IFCs line voltage, that can be
   used to switch on and off small electric loads. Consult the IFC manual for
   specifics.

1. Blower (Fan entity, _optional_)

   Blower fan that distributes the hot air from the fireplace in the room. The
   IFC supports 6 speeds for this fan.

1. Continuous Pilot (Switch entity)

   When switched to the on position the fireplace operates the pilot light in
   continuous pilot mode (CPI). By default the pilot light operates in
   intermittent pilot mode (IPI) and is electrically ignited shortly before the
   main burner is to be ignited.

   Generally, the fireplace should remain in IPI mode unless the benefits of CPI
   mode (e.g. quicker ignition especially in extreme cold conditions, less
   condensation on glass, operation during power outages when backup batteries
   are depleted) outweigh the additional cost and negative air quality effects
   from constantly burning a small amount of fuel.

1. Flame (Switch entity)

   Turns on or off the flame on the fireplace.

1. Flame height (Number entity)

   Allows setting the flame height on a scale from 1 to 6.

1. Night light (Light entity, _optional_)

   Some fireplaces come with a lamp installed at the top of the firebox. The IFC
   supports 6 dimming levels for this light.

1. Split Flow (Switch entity, _optional_)

   Control for an optional valve that can direct the flow of fuel towards
   additional burner positions. For example, some fireplaces have a front and a
   back burner. Enabling this control will enable both burners.

## Limitations

This integration has the following limitations. Many of them are a limitation of
the Napoleon Bluetooth controller or the ProFlame 2 IFC (Integrated Fireplace
Controller) which this integration cannot influence.

1. The RF remote overrides Bluetooth control (IFC limitation)

   The RF remote will always override the Bluetooth controller. If the remote is
   used then the controller will no longer be able to send commands to the IFC
   nor read the current state of the fireplace from the IFC. This also means you
   cannot turn off a fireplace that was turned on via the RF remote. While the
   Napoleon eFIRE app has a lock screen implemented that is supposed to engage
   when the remote is controlling the fireplace this does not work on my own
   controller (the command hangs indefinitely). Therefor this is currently not
   implemented here either.

   **Ideally, Home Assistant is the only thing controlling the fireplace.**

1. The Bluetooth controller is disabled when the switch on the RF
   receiver/battery backup inside the fireplace is in the "Off" position. (IFC
   limitation)

   To disable your RF remote the best thing is to just remove the batteries.

1. Turning on the fireplace via a direct flame height setting will always cause
   the fireplace to turn on at the highest flame height first and then reducing
   the flame height. The same is true for the blower and its speed settings.
   (Bluetooth controller limitation)

1. Using this integration will block the eFIRE app from connecting to the
   fireplace.

   Right now this integration maintains a permanent connection to the Bluetooth
   controller. And as long as a device is connected to the Bluetooth controller
   it is not discoverable by the eFIRE app.

   This is a limitation that can technically be worked around by only connecting
   when fetching the current state of the fireplace (currently every 30s). But
   it would still lead to situations where Home Assistant and the eFIRE app will
   conflict with each other.

   Unfortunately the controller does not send updates as BLE advertisements.

## Installation

### Installation through HACS

1. Go to HACS in your Home Assistant instance.
1. Click on **Integrations**.
1. Search for the **Napoleon eFIRE** integration.
1. Install the integration from the HACS interface.

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA
   configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need
   to create it.
1. In the `custom_components` directory (folder) create a new folder called
   `napoleon_efire`.
1. Download _all_ the files from the `custom_components/napoleon_efire/`
   directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI see if your fireplace was automatically detected or go to
   "Configuration" -> "Integrations" click "+" and search for "Napoleon eFIRE"

## Configuration is done in the UI

When setting up a fireplace for the first time you can select the features of
your fireplace you want to control as not all fireplaces come equipped with all
features.

## Contributions are welcome!

If you want to contribute to this please read the
[Contribution guidelines](CONTRIBUTING.md)

---

[Napoleon eFIRE enabled Fireplaces]: https://github.com/kaechele/napoleon-efire
[commits-shield]:
  https://img.shields.io/github/commit-activity/y/kaechele/napoleon-efire.svg?style=for-the-badge
[commits]: https://github.com/kaechele/napoleon-efire/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]:
  https://img.shields.io/badge/HACS-Default-green.svg?style=for-the-badge
[license-shield]:
  https://img.shields.io/github/license/kaechele/napoleon-efire.svg?style=for-the-badge
[maintenance-shield]:
  https://img.shields.io/badge/maintainer-Felix%20Kaechele%20%40kaechele-blue.svg?style=for-the-badge
[releases-shield]:
  https://img.shields.io/github/release/kaechele/napoleon-efire.svg?style=for-the-badge
[releases]: https://github.com/kaechele/napoleon-efire/releases
