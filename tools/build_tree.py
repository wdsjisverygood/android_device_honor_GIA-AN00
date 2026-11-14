import os, re, collections, struct, shutil

HOME = "/data/user/0/dev.dsh.android/files/home"
SRC  = HOME + "/dts_work/device.dts"
ROOT = HOME + "/dts_work/out"
OUT  = ROOT + "/arch/arm64/boot/dts/mediatek"
text = open(SRC, encoding="utf-8", errors="replace").read()
clean = re.sub(r"/\*.*?\*/", lambda m: " "*len(m.group(0)), text, flags=re.S)
clean = re.sub(r"//[^\n]*", lambda m: " "*len(m.group(0)), clean)

m = re.search(r"^\s*/\s*\{", clean, re.M)
root_open = clean.index("{", m.start())

def carve(s, open_idx):
    """返回 (根属性列表, [(节点名, 文本)])"""
    props, nodes = [], []
    depth, i, prev, in_str, cur = 1, open_idx + 1, open_idx + 1, False, None
    while i < len(s):
        c = s[i]
        if in_str:
            i += 2 if c == "\\" else 1
            if c == '"': in_str = False
            continue
        if c == '"':
            in_str = True; i += 1; continue
        if c == "{":
            if depth == 1:
                mm = re.search(r"([A-Za-z0-9_,@.#+-]+)\s*$", s[prev:i])
                cur = mm.group(1) if mm else "unnamed"
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 1:
                j = i + 1
                while j < len(s) and s[j] in " \t\r\n": j += 1
                if j < len(s) and s[j] == ";": j += 1
                nodes.append((cur, s[prev:j].strip()))
                prev, i = j, j
                continue
            elif depth == 0:
                break
        elif c == ";" and depth == 1:
            props.append(s[prev:i+1].strip()); prev = i + 1
        i += 1
    return props, nodes

root_props, nodes = carve(clean, root_open)
print(f"根属性 {len(root_props)} 条，一级子节点 {len(nodes)} 个")

RULES = [
    ("display",    ("lcd_panel","lcm","panel","backlight","leds","dsi","dpi","disp","pwm","ovl","rdma","wdma","dispsys","mutex","dsc","smi_common","mtk_leds")),
    ("touch",      ("touch","goodix","focaltech","novatek","himax","gt9","ft8","tp@","tp_")),
    ("camera",     ("camera","imgsensor","seninf","camsv","mipi_tx","mipi_rx","isp","kd_","sensor_network","cpe_")),
    ("audio",      ("sound","audio","accdet","afe","snd","speaker","smartpa","ptp3","mt_soc","dmic")),
    ("power",      ("honor_","vbus_","charger","battery","fuelgauge","fuelguage","gauge","pd_","typec","typec_","sc85","fan5","rt-pd","rt_","soh","ptst","power","batt","project","lk_","lk@")),
    ("connectivity",("wifi","bt","btif","conninfra","consys","gps","gnss","nfc","fm","stp","btb","irq_nfc","singleap")),
    ("storage",    ("msdc","ufs","mmc","nand","sdcard","flash","sd@","emmc","rpmb")),
    ("usb",        ("usb","xhci","ssusb","musb","extcon","usb0phy")),
    ("multimedia", ("vdec","venc","vcodec","jpeg","mm@","mm_","cam1","cam2","vpu","dp_tx","hdmi")),
    ("thermal",    ("thermal","tzc","cooling","power_thermalzone","lvt")),
    ("core",       ("cpus","cpu@","idle-states","psci","firmware","memory","reserved-memory","chosen","aliases","pmu","mtk_lpm","bootprof","md_attr","debug-kinfo","mrdump","ramoops","utos","secmem","trusty","atf","bl31","rootparam","hw_pmucurr")),
    ("soc",        ("soc","dramc","devapc","infra","pericfg","topmisc","sleep","srclken","apxgpt","hacc","apmixed","fhctl","apcldma","mdcldma","mobicore","tee","trusted","amms","aee","m4u","iommu","emi","bus","qos","dbg","mbist","aes","security","modem","md@","md_","dram","sramrom","dpmaif","ccci","mux","gce","cmdq","gic","intc","timer","watchdog","mali","gpu","mfg","mmsys","larb","smi","scpsys","pwrap","spmi","auxadc","efuse","topckgen","infracfg","mcucfg","dvfsrc","hwrng","nvmem","scp","mcupm","sspm","tinysys","apu","mt6","pmic","regulator","rt5","spm","crypto","camsys","syscon")),
]

def cat(name):
    n = name.lower()
    for g, keys in RULES:
        if any(k in n for k in keys):
            return g
    return "misc"

groups = collections.OrderedDict()
for name, body in nodes:
    groups.setdefault(cat(name), []).append(body)

os.makedirs(OUT, exist_ok=True)
for old in os.listdir(OUT):
    os.remove(os.path.join(OUT, old))

HDR = ("// SPDX-License-Identifier: GPL-2.0\n"
       "/*\n * HONOR GIA-AN00 / MT6877V/ZA 设备树分片\n"
       " * 由实机反编译 device.dts 自动还原，节点内容保持原样\n */\n\n")

order = ["core","soc","display","touch","camera","audio","power","connectivity","storage","usb","multimedia","thermal","misc"]
incs = []
for g in order:
    if g not in groups: continue
    fn = f"gia-an00-{g}.dtsi"
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(HDR + f"/* {len(groups[g])} 个顶层节点 */\n\n")
        for body in sorted(groups[g], key=lambda b: b.split("{")[0].strip().lower()):
            indented = "\n".join("\t" + ln for ln in body.split("\n"))
            f.write(indented.rstrip() + "\n\n")
    incs.append(f'#include "{fn}"')
    print(f"  {fn:34s} {len(groups[g]):3d} 节点  {os.path.getsize(os.path.join(OUT, fn)):>7d} B")

with open(os.path.join(OUT, "gia-an00.dts"), "w", encoding="utf-8") as f:
    f.write("// SPDX-License-Identifier: GPL-2.0\n")
    f.write("/*\n * 荣耀 60 SE / HONOR GIA-AN00 (MT6877V/ZA — 天玑 900)\n"
            " * 标准内核设备树入口。反编译文本的 phandle 为数字，内部引用自洽；\n"
            " * 若要接回 MTK 官方源码树，需把数字 phandle 换回 &label 形式。\n */\n\n")
    f.write("/dts-v1/;\n\n")
    f.write("#include <dt-bindings/gpio/gpio.h>\n")
    f.write("#include <dt-bindings/interrupt-controller/arm-gic.h>\n")
    f.write("#include <dt-bindings/interrupt-controller/irq.h>\n")
    f.write("#include <dt-bindings/clock/mt6877-clk.h>\n\n")
    for l in incs: f.write(l + "\n")
    f.write("\n/ {\n")
    for p in root_props:
        f.write("\t" + p.replace("\n", "\n\t") + "\n")
    f.write("};\n")

with open(os.path.join(OUT, "Makefile"), "w") as f:
    f.write("# SPDX-License-Identifier: GPL-2.0\ndtb-$(CONFIG_ARCH_MEDIATEK) += gia-an00.dtb\n")

with open(os.path.join(OUT, "Kconfig"), "w") as f:
    f.write('''# SPDX-License-Identifier: GPL-2.0
if ARCH_MEDIATEK

config ARCH_GIA_AN00
\tbool "HONOR GIA-AN00 (MT6877V/ZA)"
\tdepends on ARCH_MEDIATEK
\thelp
\t  荣耀 60 SE / HONOR GIA-AN00，MTK MT6877V/ZA 天玑 900。

endif
''')

# dtbo overlay 抽取
dtbo_src = HOME + "/dts_work/dtbo_a.img"
if os.path.exists(dtbo_src):
    data = open(dtbo_src, "rb").read()
    ddir = ROOT + "/dtbo"
    os.makedirs(ddir, exist_ok=True)
    off, n = 0, 0
    while True:
        idx = data.find(b"\xd0\x0d\xfe\xed", off)
        if idx < 0: break
        total = struct.unpack_from(">I", data, idx + 4)[0]
        if 0 < total < 4 * 1024 * 1024 and idx + total <= len(data):
            open(f"{ddir}/overlay_{n}.dtb", "wb").write(data[idx:idx + total])
            n += 1
        off = idx + 4
    print(f"  dtbo overlay 抽取: {n} 个 -> out/dtbo/")

print("总大小:", sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(ROOT) for f in fs) // 1024, "KB")
