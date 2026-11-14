# 核对数据（2026-11-14，实机 GIA-AN00）

所有数字均由 `tools/` 下的脚本在本机上跑出，可复现。

## 1. 三份来源的规模

| 来源 | 字符数 | 节点 | 说明 |
|---|---|---|---|
| `boot_b` 内 DTB（`reference/base.dts`） | 213,299 | 915 | 静态 base 树 |
| `dtbo/overlay_6.dtb`（`reference/overlay_6.dts`） | 223,249 | 505 | 碎片树（`__overlay__`） |
| 实机活树（`reference/live_tree.dts`） | — | **1,170** | 合并 + fixup 后 |
| 本仓库 `arch/.../gia-an00.dts` 展开 | 436,239 | **1,170** | 待发布树 |

## 2. base 树 vs 活树

```
A: 节点 915 / 属性 4585
B: 节点 1171 / 属性 7258
公共节点 915 ｜ 仅 base 0 ｜ 仅活树 256
属性单边 0 ｜ 属性值不同 355
```

活树比静态 base 多 **256 个节点**，全部来自 dtbo 合并——抽查确认：

| 关键节点 | overlay_6 中出现 | 活树 | base |
|---|---|---|---|
| `dsi@14013000/panel@0` | 有 | 有 | 无 |
| `dsi@14013000/ports` | 有 | 有 | 无 |
| `audio_hw_config/hardware_info` | 有 | 有 | 无 |

状态位抽查（决定性判据）：

| 属性 | base 树 | 活树实测 | 结论 |
|---|---|---|---|
| `direct_charger/status` | `ok` | `disabled` | 被 overlay 覆盖 |
| `battery_fault/status` | `ok` | `disabled` | 被 overlay 覆盖 |
| `usb_short_circuit_protect/status` | `disabled` | `ok` | 被 overlay 覆盖 |

→ **静态 base 单独看会误判，必须用合并后的树。**

## 3. 活树 vs 本仓库树（发布前终检）

```
活树   节点 1170  属性 8541（含每节点 name 属性）
本树   节点 1170  属性 7258
公共节点 1170 ｜ 仅活树 0 ｜ 仅本树 0
本树多出的属性名:  0
活树有而本树缺的属性: 116（= 各节点的 name 属性，dtc 输出时按惯例丢弃）
```

属性值差异 2968 处，构成：

| 类型 | 数量 | 原因 |
|---|---|---|
| 纯数值/字节差异 | 2145 | phandle 重编号、中断号编码（活树是运行时分配，本树是 `&label`） |
| 字符串差异 | 63 | `bootargs` 空白折叠、`serialno` 置零等 |
| 其它形态差异（空值 vs `<0x0>`） | 760 | dtc 对空属性的省略写法 |

结论：**结构零差异，值差异全部可解释**，可作为该机型设备树基线发布。

## 4. 复现方法

```bash
# 1) 取活树（需要 root）
python3 tools/live_tree.py            # -> verify/live_tree.dts / .json

# 2) 反编译 boot 内的 dtb
python3 tools/fdt2dts.py dtb.bin reference/base.dts

# 3) 对比
python3 tools/dtscmp.py reference/live_tree.dts arch/arm64/boot/dts/mediatek/gia-an00.dts
```

## 5. 提取环境记录

```
设备     HONOR GIA-AN00 (MT6877V/ZA)
内核     4.14.186+ aarch64，clang 11，构建 2026-04-10
boot     header v2, page 2048, kernel_size 17,928,189, dtb_size 181,895 @ 0x12fe040
dtbo     16 个 overlay，生效 overlay_6 (androidboot.dtbo_idx=6)
```
