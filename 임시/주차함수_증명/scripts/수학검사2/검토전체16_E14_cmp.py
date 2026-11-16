# -*- coding: utf-8 -*-
"""E14: 장부 4절·대응표를 장 파일 진술 머리와 견주고, 네 파일이 부르는 라벨의 존재를 확인한다."""
import re, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
heads = []
for line in open(f"{ROOT}/scripts/수학검사2/_E14_heads.tsv", encoding='utf-8'):
    f, ln, sec, kind, ch, lab, paren, status = line.rstrip("\n").split("\t")
    if status.startswith("의 증명") or paren=="" and status.startswith("의"):
        continue
    heads.append(dict(f=f, ln=int(ln), sec=sec, kind=kind, ch=ch, lab=lab, paren=paren, status=status))
print("heads(진술 머리, 증명 머리 제외):", len(heads))
H = {(h['ch'], h['lab']): h for h in heads}
# 번호 매기기: 장마다 순서
num = {}
cnt = {}
for h in heads:
    cnt[h['ch']] = cnt.get(h['ch'], 0) + 1
    num[(h['ch'], h['lab'])] = f"{h['ch']}.{cnt[h['ch']]}"

def secnorm(s):
    # 5.2.1 -> 5.2 ; 5.5.6 -> 5.5
    p = s.split('.')
    return '.'.join(p[:2])

# ---- 장부 4절
print("\n==== 장부 4절 vs 진술 머리")
lines = open(f"{ROOT}/장부_v2.md", encoding='utf-8').read().split("\n")
start = next(i for i,l in enumerate(lines) if l.startswith("## 4."))
end = next(i for i,l in enumerate(lines) if l.startswith("## 5."))
rows4 = []
for l in lines[start:end]:
    if not l.startswith("|") or l.startswith("|---") or l.startswith("| 첫 판 번호"): continue
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells) != 6: print("CELLS", len(cells), l[:80]); continue
    rows4.append(cells)
print("4절 행:", len(rows4))
seen = set()
for old, kind, name, rec, sec, lab in rows4:
    m = re.match(r'\{\{(\d+):([^}]+)\}\}', lab)
    if not m:
        m2 = re.match(r'\((\d+):([^)]+)\)', lab)
        if m2 and (m2.group(1), m2.group(2)) in H:
            print("REMOVED-BUT-PRESENT", lab)
        if sec != "뺌": print("NOLABEL-NOT-뺌", old, name, sec, lab)
        continue
    key = (m.group(1), m.group(2))
    seen.add(key)
    if key not in H:
        print("MISSING IN CHAPTERS:", lab, kind, name, sec); continue
    h = H[key]
    if h['kind'] != kind: print("KIND", lab, "장부:", kind, "장:", h['kind'])
    if secnorm(h['sec']) != sec: print("SEC", lab, "장부:", sec, "장:", h['sec'])
    # 이름·기록
    paren = h['paren']
    if paren:
        if '; 기록' in paren:
            pname, prec = paren.split('; 기록', 1); prec = '기록' + prec
        else:
            pname, prec = paren, ""
    else:
        pname, prec = "", ""
    if pname.strip() != name.strip():
        print("NAME", lab, "장부:", repr(name), "장:", repr(pname))
    if prec.strip() != rec.strip():
        print("REC", lab, "장부:", repr(rec), "장:", repr(prec))
for key in H:
    if key not in seen: print("HEAD NOT IN 4절:", key, H[key]['kind'], H[key]['paren'][:40])

# ---- 대응표
print("\n==== 대응표 vs 진술 머리")
lines = open(f"{ROOT}/대조v2/라벨_번호_대응표_1114.md", encoding='utf-8').read().split("\n")
rowsT = []
for l in lines:
    if not l.startswith("|") or l.startswith("|---") or l.startswith("| 라벨"): continue
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells) != 6: print("CELLS", len(cells), l[:80]); continue
    rowsT.append(cells)
print("대응표 행:", len(rowsT))
seenT = set(); order = []
for lab, kind, name, cur, old, sec in rowsT:
    m = re.match(r'`\{\{(\d+):([^}]+)\}\}`', lab)
    if not m:
        m2 = re.match(r'`\((\d+):([^)]+)\)`', lab)
        if m2 and (m2.group(1), m2.group(2)) in H: print("REMOVED-BUT-PRESENT", lab)
        continue
    key = (m.group(1), m.group(2)); seenT.add(key); order.append(key)
    if key not in H: print("MISSING IN CHAPTERS:", lab); continue
    h = H[key]
    if h['kind'] != kind: print("KIND", lab, kind, h['kind'])
    if num[key] != cur: print("NUM", lab, "표:", cur, "실제:", num[key])
    if secnorm(h['sec']) != sec: print("SEC", lab, "표:", sec, "장:", h['sec'])
    pn = h['paren'] if h['paren'] else "—"
    if pn != name: print("NAME", lab, repr(name), repr(pn))
for key in H:
    if key not in seenT: print("HEAD NOT IN 대응표:", key)
# 순서 비교
hk = [(h['ch'], h['lab']) for h in heads]
if hk != order: 
    print("ORDER DIFFERS")
    for i,(a,b) in enumerate(zip(hk, order)):
        if a!=b: print("  first diff at", i, a, b); break

# ---- 라벨 존재(네 파일)
print("\n==== 네 파일이 부르는 라벨의 존재")
Dlabels = set()
for f in glob.glob(f"{ROOT}/장v2/부록D_*.md"):
    for m in re.finditer(r'\{\{D:([^}]+)\}\}', open(f, encoding='utf-8').read()):
        Dlabels.add(m.group(1))
print("부록 D 라벨 수:", len(Dlabels))
for fn in ["장부_v2.md", "구조표_v2.md", "의존지도_v2.md", "대조v2/라벨_번호_대응표_1114.md"]:
    txt = open(f"{ROOT}/{fn}", encoding='utf-8').read()
    bad = {}
    for m in re.finditer(r'\{\{(\d+|D):([^}]+)\}\}', txt):
        ch, lab = m.group(1), m.group(2)
        if ch == 'D':
            if lab not in Dlabels: bad.setdefault(f"D:{lab}", 0); bad[f"D:{lab}"] += 1
        elif (ch, lab) not in H:
            bad.setdefault(f"{ch}:{lab}", 0); bad[f"{ch}:{lab}"] += 1
    print(fn, "존재하지 않는 라벨:", bad if bad else "없음")
