# dtbo 分区：16 个 overlay = 2 个机型 × 8 个硬件版本

`dtbo` 分区里 16 个 overlay 全部反编译成 dts（`dtbo/overlay_0.dts` … `overlay_15.dts`），
并逐个抽出变体标识。**它们的内容除了一处变体声明以外完全相同**——也就是说这不
是 16 套不同的屏幕参数，而是 16 个**硬件版本选择器**。

## 变体对照表

| idx | `mtk,boardid` | `mtk,board_name` | `hardware_version` |
|---:|---|---|---|
| 0 | `0x04 0x00 0x09 0x07` | `GIA_AN00_VA` | HN1GIAM |
| 1 | `0x04 0x01 0x00 0x00` | `GIA_AN00_VB` | HN1GIAM |
| 2 | `0x04 0x01 0x00 0x02` | `GIA_AN00_VC` | HN1GIAM |
| 3 | `0x04 0x01 0x00 0x04` | `GIA_AN00_VD` | HN1GIAM |
| 4 | `0x04 0x01 0x01 0x02` | `GIA_AN00_VE` | HN1GIAM |
| 5 | `0x04 0x01 0x01 0x03` | `GIA_AN00_VF` | HN1GIAM |
| **6** | `0x04 0x00 0x06 0x07` | **`GIA_AN00_VG`** | HN1GIAM |
| 7 | `0x04 0x00 0x07 0x01` | `GIA_AN00_VH` | HN1GIAM |
| 8 | `0x04 0x00 0x09 0x06` | `GIA_TN00_VA` | HN1GIATM |
| 9 | `0x04 0x00 0x09 0x08` | `GIA_TN00_VB` | HN1GIAM |
| 10 | `0x04 0x00 0x09 0x09` | `GIA_TN00_VC` | HN1GIAM |
| 11 | `0x04 0x01 0x00 0x01` | `GIA_TN00_VD` | HN1GIAM |
| 12 | `0x04 0x01 0x00 0x03` | `GIA_TN00_VE` | HN1GIAM |
| 13 | `0x04 0x01 0x01 0x04` | `GIA_TN00_VF` | HN1GIAM |
| 14 | `0x04 0x00 0x06 0x09` | `GIA_TN00_VG` | HN1GIAM |
| 15 | `0x04 0x00 0x07 0x02` | `GIA_TN00_VH` | HN1GIAM |

本机（荣耀 60 SE / `GIA-AN00`，`ro.board.platform` = `GIA_AN00_VG`）跑的是 **idx 6**，
与命令行 `androidboot.dtbo_idx=6` 一致 ✅ —— 这是本仓库数据自洽的又一处证据。

`GIA_TN00_*` 是共用 MT6877 平台的姊妹机型（同一个 dtbo 镜像里同时提供两套变体），
本仓库同时收录，做 TN00 移植时可以直接用对应的 overlay。

## 唯一的差异在哪里

16 个 dts 里，除下面这个 `fragment` 之外**逐字节相同**（含 7 组 `lcd_kit` 面板表）：

```dts
fragment@85 {
    target = <0xffffffff>;          /* 指向 &hw_config 一类节点 */
    __overlay__ {
        mtk,boardid    = <0x04 0x00 0x06 0x07>;   /* idx 6 = VG */
        mtk,board_name = "GIA_AN00_VG";
        mtk,product_name = "GIA-AN00";
        hardware_version = "HN1GIAM";
    };
};
```

所以「换屏黑屏」不是挑 overlay 出来的——7 组面板表（`lcd_kit_gia_110_150_6p67`、
`110_410`、`130_410`、`130_420`、`130_530`、`160_150`、`auo_otm1901a_5p2_1080p_video_default`）
在每个 overlay 里都在，由 **LK / lk2** 按实际屏 ID 选择，跟 `dtbo_idx` 无关。

## 面板表清单（每个 overlay 都有，取自 `overlay_6.dts`）

| 节点 | 起始行（overlay_6.dts） |
|---|---:|
| `lcd_kit_gia_110_150_6p67` | 7 |
| `lcd_kit_gia_110_410_6p67` | 436 |
| `lcd_kit_gia_130_410_6p67` | 839 |
| `lcd_kit_gia_130_420_6p67` | 1203 |
| `lcd_kit_gia_130_530_6p67` | 1558 |
| `lcd_kit_gia_160_150_6p67` | 1921 |
| `lcd_kit_gia_auo_otm1901a_5p2_1080p_video_default` | 2242 |

`__symbols__` 里同时给出 `dsi_gia_110_150_6p67 = "/fragment@0/__overlay__/lcd_kit_gia_110_150_6p67"`
这类路径别名，可以在自己的 dts 里直接用 `&dsi_gia_130_410_6p67` 引用。

## 重新生成

```bash
python3 tools/fdt2dts.py dtbo/overlay_6.dtb dtbo/overlay_6.dts
```

## 注意

- overlay 里的 `target = <0xffffffff>` 是**未解析的 phandle 占位**（fragment 的 target
  在 dtbo 编译期由 `mkdtboimg` 保留，运行时由 U-Boot/LK 填），不要把 `0xffffffff`
  当真实值使用。
- 想在自编 dtb 里复现这片屏，正确做法是直接从 `overlay_6.dts` 拷 `fragment@0..6`
  的 `__overlay__` 内容进你的 `dsi@14013000` 节点，而不是叠加整个 overlay。
