#!/usr/bin/env python3
"""纯 Python 的 FDT(.dtb) -> DTS 反编译，行为对齐 dtc -I dtb -O dts"""
import struct, sys

FDT_BEGIN_NODE, FDT_END_NODE, FDT_PROP, FDT_NOP, FDT_END = 1, 2, 3, 4, 9

def be32(b, o): return struct.unpack_from(">I", b, o)[0]

class FDT:
    def __init__(self, data):
        self.d = data
        self.magic = be32(data, 0)
        if self.magic != 0xD00DFEED:
            raise ValueError("不是有效 FDT（magic=%08x）" % self.magic)
        self.total = be32(data, 4)
        self.off_struct = be32(data, 8)
        self.off_strings = be32(data, 12)
        self.off_rsvmap = be32(data, 16)
        self.version = be32(data, 20)
        self.cpuid = be32(data, 28)
        self.size_strings = be32(data, 32)
        self.size_struct = be32(data, 36)

    def string(self, off):
        end = self.d.index(b"\0", self.off_strings + off)
        return self.d[self.off_strings + off:end].decode("utf-8", "replace")

    def rsvmap(self):
        out, o = [], self.off_rsvmap
        while True:
            addr, size = struct.unpack_from(">QQ", self.d, o)
            o += 16
            if addr == 0 and size == 0:
                break
            out.append((addr, size))
        return out

    def nodes(self):
        """返回 (root_name, tree)；tree = {'props':[(name,bytes)], 'children':[...], 'name':str}"""
        o = self.off_struct
        end = o + self.size_struct
        stack, root = [], None
        cur = None
        while o < end:
            tok = be32(self.d, o); o += 4
            if tok == FDT_BEGIN_NODE:
                e = self.d.index(b"\0", o)
                name = self.d[o:e].decode("utf-8", "replace")
                o = (e + 4) & ~3
                node = {"name": name, "props": [], "children": []}
                if cur is not None:
                    cur["children"].append(node)
                else:
                    root = node
                stack.append(node)
                cur = node
            elif tok == FDT_END_NODE:
                stack.pop()
                cur = stack[-1] if stack else None
            elif tok == FDT_PROP:
                ln, nameoff = struct.unpack_from(">II", self.d, o); o += 8
                val = self.d[o:o + ln]
                o = (o + ln + 3) & ~3
                cur["props"].append((self.string(nameoff), val))
            elif tok == FDT_NOP:
                continue
            elif tok == FDT_END:
                break
        return root

def is_printable(v):
    return all((0x20 <= c <= 0x7e) or c in (0x00, 0x09, 0x0a) for c in v)

def fmt_value(v):
    if len(v) == 0:
        return None
    # 字符串（dtc 规则：可打印且以 \0 结尾）
    if v[-1] == 0 and is_printable(v + b"\0"):
        parts = [p for p in v.split(b"\0") if p != b""]
        if parts and all(is_printable(p) for p in parts):
            return " ".join('"%s"' % p.decode("utf-8", "replace")
                            .replace("\\", "\\\\").replace('"', '\\"') for p in parts)
    if len(v) % 4 == 0:
        cells = struct.unpack(">%dI" % (len(v) // 4), v)
        out, line, cells_in_line = [], [], 0
        for c in cells:
            line.append("0x%02x" % c if c < 0x100 else "0x%x" % c)
            cells_in_line += 1
            if cells_in_line == 8:
                out.append(" ".join(line)); line = []; cells_in_line = 0
        if line:
            out.append(" ".join(line))
        return "<" + "\n\t\t".join(out) + ">"
    return "[" + " ".join("%02x" % c for c in v) + "]"

def labels_from(root):
    """从 __symbols__ 恢复 label：只处理同节点链"""
    m = {}
    for name, val in root["props"]:
        if name != "__symbols__":
            continue
        items = val.split(b"\0")
        it = iter(items)
        for l, p in zip(it, it):
            if not l:
                continue
            m[p.decode()] = l.decode()
    return m

def emit(node, depth, lab, path):
    ind = "\t" * depth
    name = node["name"] if node["name"] else "/"
    label = lab.get(path)
    out = []
    head = (label + ": ") if label else ""
    if depth == 0:
        out.append("/ {")
    else:
        out.append("%s%s%s {" % (ind, head, name))
    for pname, val in node["props"]:
        if pname == "__symbols__":
            continue
        s = fmt_value(val)
        if s is None:
            out.append("%s\t%s;" % (ind, pname))
        else:
            out.append("%s\t%s = %s;" % (ind, pname, s))
    for ch in node["children"]:
        child_path = (path.rstrip("/") + "/" + ch["name"]) if path != "/" else "/" + ch["name"]
        out.append(emit(ch, depth + 1, lab, child_path))
    out.append("%s};" % ind if depth else "};")
    return "\n".join(out)

def decompile(path, out_path=None, keep_symbols=False):
    data = open(path, "rb").read()
    f = FDT(data)
    root = f.nodes()
    lab = labels_from(root)
    body = emit(root, 0, lab, "/")
    hdr = ["/dts-v1/;", ""]
    for a, s in f.rsvmap():
        hdr.append("/memreserve/ 0x%x 0x%x;" % (a, s))
    if len(hdr) > 2:
        hdr.append("")
    txt = "\n".join(hdr) + "\n" + body + "\n"
    if out_path:
        open(out_path, "w", encoding="utf-8").write(txt)
    return txt, len(lab), f

if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + ".dts"
    txt, nlab, f = decompile(src, dst)
    print(f"{src} -> {dst}")
    print(f"  totalsize={f.total} version={f.version} struct={f.size_struct}B strings={f.size_strings}B label={nlab}")
    print(f"  输出 {len(txt)} 字符")
