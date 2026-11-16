# -*- coding: utf-8 -*-
"""검토 C: D.30 (7)(ㄱ)의 인수 범위(ς≤12, st≤0.3)와 (ㄷ)의 ς_U+1을 입력 jsonl의 sL·sU로 확인."""
import io, os, glob, json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
base = os.path.join(ROOT, "원고_자료", "세션_재계산")
files = glob.glob(os.path.join(base, "r89eb039_polar", "inputs", "*.jsonl")) + glob.glob(os.path.join(base, "**", "NEW_recert_Q*.jsonl"), recursive=True)
print("파일 수", len(files))
for f in files[:3]: print(" ", os.path.relpath(f, ROOT))
mx = (-1, None); mn = (1e9, None); n = 0; keys = set()
for f in files:
    for ln in io.open(f, encoding="utf-8"):
        ln = ln.strip()
        if not ln: continue
        d = json.loads(ln); n += 1; keys |= set(d.keys())
        for kk in ("sU", "sigma_hi", "sig_hi"):
            if kk in d and d[kk] > mx[0]: mx = (d[kk], (os.path.basename(f), d.get("k1"), d.get("k2")))
        for kk in ("sL", "sigma_lo", "sig_lo"):
            if kk in d and d[kk] < mn[0]: mn = (d[kk], os.path.basename(f))
print("행 수", n, "키", sorted(keys)[:20])
print("max sU", mx, " -> (sU+1)/40 =", (mx[0]+1)/40, " sU/40 =", mx[0]/40)
print("min sL", mn)
