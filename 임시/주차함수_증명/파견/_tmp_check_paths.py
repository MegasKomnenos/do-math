# -*- coding: utf-8 -*-
"""부록D_장7B.md 자료 줄의 records/<r7>…/경로 실재 확인(읽기 전용)."""
import io, os, re, glob, sys
R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fn = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "장v2", "부록D_장7B.md")
txt = io.open(fn, encoding="utf-8").read()
dirs = os.listdir(R)
n = bad = 0
for ln in txt.split("\n"):
    if not ln.startswith("**자료.**"):
        continue
    for seg in re.findall(r"`([^`]+)`", ln):
        m = re.match(r"records/(r[0-9a-f]{7,32})[^/]*/(.+)$", seg)
        if not m:
            continue
        d = [x for x in dirs if x.startswith(m.group(1))]
        p = os.path.join(R, d[0], m.group(2)) if d else None
        n += 1
        if not p:
            print("NO DIR", seg); bad += 1; continue
        if "*" in p:
            g = [x for x in glob.glob(p) if os.path.isfile(x)]
            print("GLOB", len(g), seg)
            if not g: bad += 1
            continue
        if os.path.isdir(p):
            cnt = sum(len(f) for _, _, f in os.walk(p)); sz = sum(os.path.getsize(os.path.join(a, b)) for a, _, f in os.walk(p) for b in f)
            print("DIR", cnt, "files", sz // 1024, "KiB", seg)
        elif not os.path.exists(p):
            print("MISSING", seg); bad += 1
print("paths", n, "bad", bad)
