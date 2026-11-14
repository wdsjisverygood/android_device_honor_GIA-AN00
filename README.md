# android_device_honor_GIA-AN00
# Honor 60 SE (GIA-AN00) Device Tree Dump

This repository contains the extracted Device Tree Source (DTS) and hardware configuration for the **Honor 60 SE (Model: GIA-AN00)**, powered by the MediaTek MT6877 (Dimensity 900) SoC.

This dump is extracted from the stock Magic UI 6.1 (based on Android 12). It is intended for research, GSI porting, and kernel development purposes.

## 🛠 Hardware Specifications
Based on the extracted DTS analysis, here are the key hardware details:

*   **SoC**: MediaTek MT6877V/ZA (Dimensity 900)
*   **CPU**: Octa-core (2x Cortex-A76 + 6x Cortex-A55)
*   **GPU**: ARM Mali-G68 MC4
*   **Display**: 6.67-inch, 1080 x 2400 (FHD+), supports up to 120Hz refresh rate.
*   **Battery**: 4300mAh (Rated Capacity)
*   **Charging IC**: MT6360 PMIC (Supports fast charging protocols)
*   **Partition Scheme**: Virtual A/B (Dynamic Partitions)
*   **Fingerprint**: Side-mounted fingerprint sensor (Goodix/Synaptics variants)

## ⚠️ Privacy & Disclaimer
*   **Sanitized Data**: To protect the owner's privacy, all sensitive information including the **Device Serial Number (SN)**, **Battery SN/Certificate**, and **Mainboard ID (boardid)** have been completely sanitized and replaced with zeros (`0x00` / `00000000`).
*   **Disclaimer**: I am not responsible for bricked devices, dead SD cards, or thermonuclear war. Flash and modify your device at your own risk.

## 📂 Contents
*   `device.dts`: The sanitized Device Tree Source file.

---
*Extracted and open-sourced for the geek community.*
