# WMS WebControl (Basic) – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: LPGL3.0](https://img.shields.io/github/license/moltke69/ha-wms-webcontrol)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintenance-Active-green.svg)](https://github.com/moltke69/ha-wms-webcontrol)

---

> [!IMPORTANT]
> This integration talks to the old Warema WMS WebControl via XML protocol. It does not work with the Warema WMS WebControl Pro.

---

This custom component enables local control of Warema awnings (and other WMS devices) via the classic **Warema WMS WebControl** (without "Pro") in Home Assistant. Since the WMS WebControl does not offer an official API, this integration uses the internal XML protocols, which are also used by the device's web interface, to send commands and query the status.

## Features

* **No YAML required**: The entire setup is performed conveniently and efficiently via the Home Assistant user interface (Config Flow).
* **Auto-Discovery**: You only need to enter the IP address. The integration automatically scans the web control for all rooms and channels and adopts the original device names!
* **Full Control**: Supports opening, closing, and stopping while moving, as well as moving to a precise percentage position.
* **100% Local**: All commands are sent directly to the web control within your local network. No cloud required!
* **Real-time Feedback**: Retrieves fresh data (wake-up command) before each status update, ensuring the position in Home Assistant is always accurate.

## Requirements

* A working **Warema WMS Webcontrol** (the older version, often implemented as a small black box).
* The IP address of the WMS Webcontrol must be known and ideally assigned statically in the router.

## Installation

The easiest method is installation via [HACS](https://hacs.xyz/) (Home Assistant Community Store).

1. Open **HACS** in Home Assistant.
2. Click on **Integrations**.
3. Click the three dots (`...`) in the upper right corner and select **Custom Repositories**.
4. Paste the URL of this repository: `https://github.com/moltke69/ha-wms-webcontrol`
5. Select **Integration** as the category and click *Add*.
6. Now search for *Warema WMS Webcontrol* in HACS, click on it, and select **Download**.
7. **Restart Home Assistant.**

*(Alternatively: Download the repository as a ZIP file and manually copy the `custom_components/warema_webcontrol` folder to your Home Assistant directory.)*

## Configuration

After the integration is installed and Home Assistant has been restarted, setup is a breeze:

1. In Home Assistant, go to **Settings** -> **Integration**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **Warema WMS Webcontrol** and select it.
4. Enter the **IP address** of your web control (e.g., `192.168.1.50`).
5. Click *Submit*.

Sit back! The integration will now scan all rooms and automatically add your awnings as "covers" to your Home Assistant.

## Troubleshooting

* **The awning only responds intermittently:** The system uses sequential numbers to authenticate commands. The integration handles this automatically. If commands are still being dropped, check if the web control has a stable Wi-Fi/LAN connection.
* **The position is incorrect:** Warema uses an internal logic of 0-200, while Home Assistant uses 0-100% (0% = closed/extended, 100% = open/retracted). The integration automatically converts this.

## Note on Code Development

The reverse engineering of the WMS protocol (intercepting the hex and XML strings) was performed manually. AI assistance (LLM) was used for the subsequent translation into a functional Home Assistant integration (Python, Config Flow, async logic).
The code was then thoroughly tested locally.

---
*Disclaimer: This is an unofficial community project. It is not affiliated with WAREMA Renkhoff SE.*


