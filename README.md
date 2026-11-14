# Honor 60 SE (GIA-AN00) 设备树 / Device Tree Source

荣耀 60 SE（HONOR 60 SE，型号 `GIA-AN00`）的完整设备树源码，从实机提取、反编译、切分，
并与内核运行时活树逐节点核对过。原厂 Magic UI 6.1.0.175（Android 12）提取，
适用于内核移植、GSI 适配、TWRP 移植与硬件研究。

Complete device tree for the **Honor 60 SE (GIA-AN00, MediaTek MT6877V/ZA)**,
extracted from a retail unit, split by subsystem, and verified node-by-node
against the live kernel tree at runtime.

---

## 机型识别（别搞错型号）

| 项 | 值 | 怎么验 |
|---|---|---|
| 商品名 | **荣耀 60 SE（HONOR 60 SE）** | 机身 / 包装 |
| 型号 | `GIA-AN00` | `getprop ro.product.model` |
| 内部代号 | `HNGIA-M` | `getprop ro.product.device` |
| board | `GIA_AN00_VG` | `getprop ro.board.platform` |
| SoC | `MT6877V/ZA` = **天玑 900 / Dimensity 900** | 设备树 `model` 字段实测 |
| dtbo 变体 | idx 6 = `GIA_AN00_VG` | `androidboot.dtbo_idx=6` |

⚠️ **不是**荣耀 X40。两者同属 MT6877 家族但 SoC 版本（`MT6877V/ZA` vs `MT6877V/TZA`）
与 board 不同，dtbo 变体也不同，混用会直接不开机。判断依据以设备树 `model`
与 `ro.board.platform` 为准，不要凭外观或商品页。

## 硬件与软件规格

| 项 | 值 |
|---|---|
| SoC | MediaTek MT6877V/ZA（Dimensity 900 5G） |
| CPU | 8 核，2× Cortex-A76 + 6× Cortex-A55 |
| RAM | 8.0 GB + 2.0 GB（虚拟内存） |
| 存储 | 256 GB，UFS |
| 屏幕 | 6.67" 1080×2400 (FHD+)，AMOLED |
| 电池 | 4300 mAh（额定） |
| OS | Magic UI 6.1 / Android 12 / SDK 31 / VNDK 31 |
| 构建号 | `6.1.0.175 (C00E173R8P8)` |
| 安全补丁 | 2026-10-05 |
| 内核 | `4.14.186+` aarch64，clang 11，构建于 2026-04-10 |
| 基带 | `MOLY.NR15.R3.TC36.PR4.SP.V1.0.2.P108` |
| 分区布局 | A/B + 动态分区；当前 slot `_b`；super 9,227,468,800 B |

## 数据来源与可信度

| 来源 | 说明 | 校验 |
|---|---|---|
| `boot_b` 分区内的 DTB | `boot.img` 头部 `dtb_size=181895 @ 0x12fe040`（FDT magic 通过），反编译 → `reference/base.dts` | 与 dtbo 合并后与活树比对 |
| `/sys/firmware/devicetree/base` | 内核运行时**活树**（base + overlay + bootloader fixup 后的最终态），逐节点逐属性 dump | 权威判据 |
| `dtbo` 分区 16 个 overlay | 2 机型 × 8 硬件版本选择器，含 7 组 `lcd_kit` 面板表 | 与 `ro.board.platform` 交叉核对 |
| `reference/device.dts` | 原始扁平化 dts（436,239 B，md5 `251d40c071f954288984283eef8b5557`），本仓库切分的源头 | 与仓库首版逐字节一致 |

`arch/.../gia-an00.dts` 与活树的核对结果（详见 [docs/VERIFY.md](docs/VERIFY.md)）：

- 节点集合：活树 1170 个，本树 1170 个，**无单边节点**
- 属性名集合：本树**没有多出任何属性**
- 属性值差异 ≈2968 处，**集中在 phandle 重编号与中断号编码**——`&label` 引用被解析成数字
  与运行时重新分配 phandle 的必然结果，不是内容错误

## 目录结构

```
arch/arm64/boot/dts/mediatek/
├── gia-an00.dts              入口：#include 13 个分片 + 根属性
├── gia-an00-core.dtsi        20 节点  cpus / psci / memory / reserved-memory / ramoops
├── gia-an00-soc.dtsi        255 节点  GIC / topckgen / infracfg / dramc / devapc / iommu / gce / mali
├── gia-an00-display.dtsi     34 节点  dsi / dispsys / mutex / ovl / rdma / lcd_panel
├── gia-an00-power.dtsi       40 节点  honor_* 电源域 / charger / battery / fuelgauge / typec / pd
├── gia-an00-misc.dtsi        41 节点  ap_ccif / bpi / cqdma / dvfs 等
├── gia-an00-multimedia.dtsi  27 节点  vdec / venc / jpeg / dp_tx / cam3
├── gia-an00-camera.dtsi      24 节点  imgsensor / seninf / camsv / mipi
├── gia-an00-audio.dtsi       14 节点  afe / sound / accdet / smartpa
├── gia-an00-connectivity.dtsi 12 节点 wifi / bt / btif / consys / nfc / gnss
├── gia-an00-storage.dtsi      9 节点  msdc0-1 / ufshci / ufsphy / rpmb
├── gia-an00-usb.dtsi          8 节点  xhci / usb-phy / extcon
├── gia-an00-thermal.dtsi      5 节点  thermal zone
├── gia-an00-touch.dtsi        1 节点  goodix 触摸
├── Makefile / Kconfig        dtb-$(CONFIG_ARCH_GIA_AN00) += gia-an00.dtb
dtbo/          16 个 overlay：overlay_N.dtb（原样）+ overlay_N.dts（反编译，已逐个核对）
reference/     device.dts / base.dts / overlay_6.dts / live_tree.dts / live_tree.json
tools/         fdt2dts.py / dtscmp.py / live_tree.py / build_tree.py
docs/          VERIFY.md 核对数据 · DTBO.md 变体对照表
```

共 **471 个 label**，无重复，可直接用 `&label` 引用，能无缝接回 MTK 源码树。

## 编译

```bash
# A. 只验证语法（不需要内核树）
dtc -I dts -O dtb -o gia-an00.dtb arch/arm64/boot/dts/mediatek/gia-an00.dts

# B. 放进内核源码树
cp -r arch/arm64/boot/dts/mediatek/* <kernel>/arch/arm64/boot/dts/mediatek/
<kernel>/scripts/config --enable ARCH_GIA_AN00
make ARCH=arm64 dtbs
```

建议配 **MTK 4.14 官方 BSP** 内核树，`Makefile` 里的 `dtb-$(CONFIG_ARCH_MEDIATEK)`
约定与 MTK BSP 一致。

## 复现验证

```bash
python3 tools/live_tree.py    # 需要 root：dump 活树
python3 tools/fdt2dts.py dtb.bin reference/base.dts
python3 tools/dtscmp.py reference/live_tree.dts arch/arm64/boot/dts/mediatek/gia-an00.dts
```

## 已知差异 / 注意

1. **`serialno` 已置零**。原始 DTB 里 `firmware/android/serialno = "0000000000000000"`，
   真实序列号由 bootloader 运行时写入。同时按隐私要求，电池 SN/证书、boardid 等
   也已置零（`0x00` / `00000000`）。
2. 本树来自 **base + dtbo(overlay 6)** 的静态合并结果；活树额外含 bootloader fixup
   （`serialno`、部分 phandle 编号、`bootargs` 空白折叠）。差异已量化在 `docs/VERIFY.md`。
3. **`dtbo` 的 16 个 overlay 是「2 机型 × 8 硬件版本」选择器，不是 16 套屏幕参数**。
   它们除 `mtk,boardid` / `mtk,board_name` 一行外逐字节相同；本机 `dtbo_idx=6` →
   `GIA_AN00_VG`。7 组 `lcd_kit` 面板表在每个 overlay 里都有，由 LK 按实际屏 ID 选择，
   与 overlay 序号无关。详见 [docs/DTBO.md](docs/DTBO.md)。
4. 这台机器的分区布局**不是标准 AOSP**：没有独立 `/product`，只有 `product_h` / `patch_hn` /
   `preas_a` / `preavs_a` / `preload` / `cust` / `version` 等 Honor 私有分区。
   写 GSI 或自编 ROM 时这部分必须自己处理。

## 隐私与免责

- 所有敏感信息（设备 SN、电池 SN/证书、主板 boardid）已置零替换为 `0x00` / `00000000`。
- 不含任何私有密钥、证书、账号或他人数据。
- 仅供同型号设备的系统开发、内核移植、TWRP 移植等用途。
- 刷机有风险，作者不对变砖、数据丢失、SD 卡损坏或「核战争」负责。刷机自负。
- `dtbo/` 与 `reference/` 中的二进制/反编译产物版权归原厂（Honor / MediaTek）所有，
  按 GPL-2.0 内核衍生作品惯例提供，仅作互操作性研究与兼容性参考。

## 协议

GPL-2.0（内核设备树为其衍生作品）。见 [LICENSE](LICENSE)。

## 致谢

- MediaTek 4.14 BSP 与 MT6877 平台资料
- `dtc` / `libfdt` / `mkdtboimg`
- 提供 4.14 BPF 回归 NOP 补丁的社区工作

---
*Extracted and open-sourced for the geek community.*
