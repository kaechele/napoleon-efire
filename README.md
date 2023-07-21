# Napoleon eFIRE Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs] ![Project Maintenance][maintenance-shield]

Integrate your Napoleon eFIRE Bluetooth controlled fireplace into Home
Assisstant. Works best with an
[ESPHome Bluetooth Proxy](https://esphome.github.io/bluetooth-proxies/).

**This integration will set up the following platforms.**

| Platform | Description                                                                                   |
| -------- | --------------------------------------------------------------------------------------------- |
| `fan`    | Controls the optional blower fan.                                                             |
| `light`  | Controls the optional light kit. The optional LED controller is not yet implemented.          |
| `number` | Allows setting the flame height on a scale of 1 to 6.                                         |
| `switch` | Controls the main power as well as auxillary power, continuous pilot and split flow settings. |

## Installation

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
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for
   "Napoleon eFIRE"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the
[Contribution guidelines](CONTRIBUTING.md)

---

[Napoleon eFIRE enabled Fireplaces]: https://github.com/kaechele/napoleon-efire
[commits-shield]: https://img.shields.io/github/commit-activity/y/kaechele/napoleon-efire.svg?style=for-the-badge
[commits]: https://github.com/kaechele/napoleon-efire/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/kaechele/napoleon-efire.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Felix%20Kaechele%20%40kaechele-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/kaechele/napoleon-efire.svg?style=for-the-badge
[releases]: https://github.com/kaechele/napoleon-efire/releases
