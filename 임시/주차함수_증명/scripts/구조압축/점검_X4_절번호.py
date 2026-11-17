# -*- coding: utf-8 -*-
"""X4 (ㄹ) 절 번호 참조: 「n.m절」「n.m.k절」과 장 번호 「n장」, 괄호 절 참조 (7.1) 꼴을 현행 머리와 맞춘다. 읽기 전용."""
import glob, io, os, re
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
def rel(p): return os.path.relpath(p, ROOT)
BS = chr(92)
secs = {}
chaps = set()
for p in files:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        m = re.match(r"^## (\d+)\. (.*)", ln)
        if m: chaps.add(int(m.group(1))); secs[m.group(1)] = (rel(p), no, m.group(2))
        m = re.match(r"^###+ (\d+\.\d+(?:\.\d+)?) (.*)", ln)
        if m: secs[m.group(1)] = (rel(p), no, m.group(2))
print("## 현행 장:", sorted(chaps))
print("## 현행 절 수:", len([s for s in secs if '.' in s]))
for s in sorted(secs, key=lambda x: [int(t) for t in x.split('.')]):
    print(f"   {s}  {secs[s][2]}")
print()
REF = re.compile(r"(\d{1,2}\.\d{1,2}(?:\.\d)?)\s*절")
CHREF = re.compile(r"(?<![\d.])(\d{1,2})\s*장(?![가-힣]?[부분])")
bad = []; chbad = []; allrefs = Counter(); chrefs = Counter(); refwhere = defaultdict(list)
for p in files:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        for m in REF.finditer(ln):
            allrefs[m.group(1)] += 1; refwhere[m.group(1)].append(f"{os.path.basename(p)}:{no}")
            if m.group(1) not in secs:
                bad.append((rel(p), no, m.group(0), ln[max(0,m.start()-40):m.end()+40]))
        for m in CHREF.finditer(ln):
            n = int(m.group(1)); chrefs[n] += 1
            if n not in chaps:
                chbad.append((rel(p), no, m.group(0), ln[max(0,m.start()-40):m.end()+40]))
print("## 절 참조 토큰 수:", sum(allrefs.values()), "| 서로 다른 절:", len(allrefs))
print("## 현행에 없는 절 참조:", len(bad))
for b in bad: print("  ", b)
print()
print("## 장 참조 분포:", dict(sorted(chrefs.items())))
print("## 현행에 없는 장 참조:", len(chbad))
for b in chbad: print("  ", b)
print()
print("## 절별 참조 수와 자리(다른 장에서 부르는 것만; 절 번호 밈의 여파 자리)")
for s in sorted(allrefs, key=lambda x: [int(t) for t in x.split('.')]):
    own = os.path.basename(secs[s][0]) if s in secs else "?"
    outside = [w for w in refwhere[s] if w.split('.md')[0].rstrip('AB') != own.split('.md')[0].rstrip('AB')]
    print(f"   {s}절 x{allrefs[s]}  밖에서 {len(outside)}: {outside[:12]}")
print()
# 괄호 절 참조 (n.m) — 식 번호 태그가 없는 장(1·2·3·5A·7A·10·11)과 부록 D에서
PAREN = re.compile(r"\((\d{1,2})\.(\d{1,2})\)")
print("## 태그 없는 장·부록 D의 괄호 (n.m) 출현(절 참조인지 식 참조인지 읽어 가른다)")
for p in files:
    txt = io.open(p, encoding="utf-8").read()
    if BS + "tag{" in txt: continue
    for no, ln in enumerate(txt.split("\n"), 1):
        for m in PAREN.finditer(ln):
            print(f"   {rel(p)}:{no} {m.group(0)}  …{ln[max(0,m.start()-50):m.end()+30]}…")
print()
# 11.4·7.7·9장·9.x 흔적
TRACE = re.compile(r"11\.4|9\.\d절|9장|\{\{9:|첫째 증명|둘째 증명|두 증명|두 길|두 마무리|공유 입력|고유 입력|LRP|regen|mathsf\{FS\}|mathrm\{lk\}|P" + BS + BS + r"Diamond|old-6-22|old-2-39|old-2-41|increment-bounds|D-bound|pair-rearrange|regen-vs-ledger|둘째 문턱|1\.05\b|3\.6k|1\.009")
print("## 제거 물결 토큰 전수(장·부록 D)")
tot = Counter()
for p in files:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        for m in TRACE.finditer(ln):
            tot[m.group(0)] += 1
            print(f"   {rel(p)}:{no} 「{m.group(0)}」 …{ln[max(0,m.start()-50):m.end()+40]}…")
print("   합:", dict(tot))
