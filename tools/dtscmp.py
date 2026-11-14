#!/usr/bin/env python3
"""结构+属性对比（忽略空白/注释/label 前缀）"""
import re, sys

TOK = re.compile(r'"[^"]*"|<[^>]*>|\[[^\]]*\]|[^\s{}=;:\[\]<>"]+|[{};=:]')

def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", lambda m: " "*len(m.group(0)), s, flags=re.S)
    s = re.sub(r"//[^\n]*", lambda m: " "*len(m.group(0)), s)
    s = re.sub(r"/dts-v1/;", lambda m: " "*len(m.group(0)), s)
    s = re.sub(r"/plugin/;", lambda m: " "*len(m.group(0)), s)
    s = re.sub(r"#[^\n]*", lambda m: " "*len(m.group(0)), s)
    return s

def norm(v):
    v = v.replace(" ,", ",")
    v = re.sub(r"\s+", " ", v).strip()
    return v

def parse(text):
    toks = [m.group(0) for m in TOK.finditer(strip_comments(text))]
    tree = {}
    def walk(i, path):
        tree.setdefault(path, {})
        while i < len(toks):
            t = toks[i]
            if t == "}":
                return i + 1
            if t == "/memreserve/":
                while i < len(toks) and toks[i] != ";": i += 1
                i += 1; continue
            if i + 1 < len(toks) and toks[i+1] == ":":   # label: 跳过
                i += 2; continue
            if i + 1 < len(toks) and toks[i+1] == "{":   # name {
                name = t
                newp = (path.rstrip("/") + "/" + name) if path != "/" else "/" + name
                i = walk(i + 2, newp)
                if i < len(toks) and toks[i] == ";": i += 1
                continue
            if t == "{":                                  # 根
                i = walk(i + 1, path)
                if i < len(toks) and toks[i] == ";": i += 1
                continue
            # 属性
            name = t; i += 1
            if i < len(toks) and toks[i] == "=":
                i += 1; buf = []
                while i < len(toks) and toks[i] != ";":
                    buf.append(toks[i]); i += 1
                i += 1
                tree[path][name] = norm(" ".join(buf))
            else:
                if i < len(toks) and toks[i] == ";": i += 1
                tree[path][name] = ""
        return i
    walk(0, "/")
    return tree

def report(pa, pb, na, nb, show=12):
    a, b = parse(open(pa, encoding="utf-8", errors="replace").read()), parse(open(pb, encoding="utf-8", errors="replace").read())
    onlya = sorted(set(a) - set(b)); onlyb = sorted(set(b) - set(a))
    common = set(a) & set(b)
    pdiff, pmiss = [], []
    for p in common:
        for k in set(a[p]) - set(b[p]): pmiss.append((p, k, "只 A 有"))
        for k in set(b[p]) - set(a[p]): pmiss.append((p, k, "只 B 有"))
        for k in set(a[p]) & set(b[p]):
            if a[p][k] != b[p][k]:
                pdiff.append((p, k, a[p][k], b[p][k]))
    print(f"A = {na}: 节点 {len(a)}  属性 {sum(len(v) for v in a.values())}")
    print(f"B = {nb}: 节点 {len(b)}  属性 {sum(len(v) for v in b.values())}")
    print(f"公共节点 {len(common)} ｜ 仅A {len(onlya)} ｜ 仅B {len(onlyb)}")
    print(f"属性单边 {len(pmiss)} ｜ 属性值不同 {len(pdiff)}")
    if onlya: print("\n仅 A 有（前 %d）:" % show); [print("  " + p) for p in onlya[:show]]
    if onlyb: print("\n仅 B 有（前 %d）:" % show); [print("  " + p) for p in onlyb[:show]]
    if pmiss: print("\n属性单边（前 %d）:" % show)
    for p, k, w in pmiss[:show]: print(f"  {p} :: {k} ({w})")
    if pdiff:
        print("\n属性值不同（前 %d）:" % show)
        for p, k, va, vb in pdiff[:show]:
            print(f"  {p} :: {k}\n     A={va[:80]}\n     B={vb[:80]}")
    return len(onlya) + len(onlyb) + len(pmiss) + len(pdiff)

if __name__ == "__main__":
    report(sys.argv[1], sys.argv[2], "A", "B")
