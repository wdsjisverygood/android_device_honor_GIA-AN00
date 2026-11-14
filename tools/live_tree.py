import os, sys, json, struct

ROOT = "/sys/firmware/devicetree/base"
OUT_DTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify/live_tree.dts")
OUT_JSON = OUT_DTS.replace(".dts", ".json")

def is_strings(b):
    if not b or b[-1] != 0: return False
    return all(0x20 <= c <= 0x7e or c in (0x09, 0x0a, 0x00) for c in b)

def fmt_prop(b):
    """-> ('strs'|'cells'|'bytes', rendered)"""
    if is_strings(b):
        parts = [p.decode('latin1') for p in b.split(b'\0') if p]
        return 'strs', ' , '.join('"%s"' % p for p in parts)
    if len(b) % 4 == 0 and b:
        cells = struct.unpack(">%dI" % (len(b)//4), b)
        out = []
        for c in cells:
            out.append("0x%x" % c)
        return 'cells', '<' + ' '.join(out) + '>'
    return 'bytes', '[' + ' '.join('%02x' % c for c in b) + ']'

def read_prop(p):
    try:
        with open(p, 'rb') as f: return f.read()
    except (IsADirectoryError, IsADirectoryError if False else PermissionError):
        return None

def walk(path, rel, lines, tree, depth):
    try: names = sorted(os.listdir(path))
    except OSError: return
    props, kids = [], []
    for n in names:
        fp = os.path.join(path, n)
        if os.path.isdir(fp): kids.append(n)
        else:
            try:
                with open(fp, 'rb') as f: b = f.read()
            except OSError: continue
            kind, txt = fmt_prop(b)
            props.append((n, kind, txt, b.hex()))
    node_path = rel if rel else "/"
    tree[node_path] = {n: {'kind': k, 'text': t, 'hex': h} for n, k, t, h in props}
    pad = "\t" * depth
    hdr = ("%s {" % (node_path.strip('/').split('/')[-1] if rel else "/"))
    lines.append(pad + hdr)
    for n, k, t, h in props:
        if n == 'name': continue
        lines.append("\t" * (depth+1) + (("%s = %s;" % (n, t)) if t else ("%s;" % n)))
    for kid in kids:
        walk(os.path.join(path, kid), (rel + "/" + kid) if rel else "/" + kid, lines, tree, depth+1)
    lines.append(pad + "};")

lines = ["/dts-v1/;", ""]
tree = {}
walk(ROOT, "", lines, tree, 0)
os.makedirs(os.path.dirname(OUT_DTS), exist_ok=True)
open(OUT_DTS, 'w').write("\n".join(lines) + "\n")
json.dump(tree, open(OUT_JSON, 'w'), ensure_ascii=False)
print("nodes=%d props=%d" % (len(tree), sum(len(v) for v in tree.values())))
print(OUT_DTS)
