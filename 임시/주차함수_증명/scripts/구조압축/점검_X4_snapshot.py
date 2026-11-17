# -*- coding: utf-8 -*-
"""X4: 읽은 트리의 시각 — 장v2/*.md의 mtime·크기·sha256을 적는다(읽기 전용)."""
import glob, hashlib, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "구조표_v2.md")]
print("snapshot at", time.strftime("%Y-%m-%d %H:%M:%S"))
for p in files:
    b = open(p, "rb").read()
    print(f"{os.path.relpath(p, ROOT)}\t{time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(p)))}\t{len(b)}\t{b.count(b'\n')}\t{hashlib.sha256(b).hexdigest()[:12]}")
