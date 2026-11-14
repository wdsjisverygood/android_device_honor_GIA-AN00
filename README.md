# TWRP device tree — Honor 60 SE (GIA-AN00)

TWRP 12.1 device tree, extracted from the retail unit's `boot_b.img` and
recovery ramdisk.

## 数据来源

| 文件 | 来源 |
|---|---|
| `prebuilt/kernel` | `boot_b.img` kernel（18,718,206 B，gzip）|
| `prebuilt/dtb` | `boot_b.img` 头 `dtb_size=181895` 的 DTB |
| `recovery.fstab` | 原机 recovery ramdisk `system/etc/recovery.fstab` + `fstab.mt6877` |
| `recovery/root/init.recovery.mt6877.rc` | 原机 recovery init（USB 配置）|

## 内核参数

```
BOARD_KERNEL_BASE     = 0x40000000
BOARD_KERNEL_OFFSET   = 0x00080000
BOARD_RAMDISK_OFFSET  = 0x11100000
BOARD_TAGS_OFFSET     = 0x07C80000
BOARD_KERNEL_PAGESIZE = 2048
BOARD_KERNEL_CMDLINE  = bootopt=64S3,32N2,64N2 buildvariant=user
BOARD_MKBOOTIMG_ARGS  = --header_version 2 --dtb prebuilt/dtb ...
```

## 编译

配合 `Action-TWRP-Builder` 的 `build-gia.yml`：

```
MANIFEST_BRANCH: twrp-12.1
DEVICE_TREE_BRANCH: twrp-12.1
DEVICE_PATH: device/honor/gia
DEVICE_NAME: gia
MAKEFILE_NAME: twrp_gia
```

## 刷入

```bash
fastboot flash boot_b recovery.img
fastboot reboot recovery
```

> A/B 设备：TWRP 刷到 `boot_b` 后原系统无法启动，测试完刷回 `boot_b.img`。

## 分区注意

- A/B + 动态分区（super 9,227,468,800 B）
- 无独立 `/product`，用 `product_h`
- Honor 私有分区：`patch`、`preas`、`preavs`、`preload`、`cust`、`version`

## 待调项

| 项 | 说明 |
|---|---|
| 触摸 | Goodix，若无法触摸调 `TW_INPUT_BLACKLIST` |
| 解密 | FBE + metadata，首次可能失败 |
| 屏幕 | 1080×2400，`TW_THEME=portrait_hdpi` |
