# -*- coding: utf-8 -*-
"""V5 (ㄹ): README 기록 사본 표·세션 표를 디스크와 대조(존재·SHA), 사본 README와의 행 차이, 자료묶음_v2 건조 수집과의 대조."""
import io, os, re, sys, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
B = os.path.join(ROOT, "원고_자료")
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()
def rows(path):
    s = io.open(path, encoding="utf-8").read()
    head, tab = s.split("## 파일 목록", 1)
    R = []
    for l in tab.split("\n"):
        m = re.match(r"^\| `([^`]+)` \| (.*?) \| ([^|]+) \| `([0-9a-f]{64})` \|$", l)
        if m: R.append((m.group(1), m.group(2), m.group(3).strip(), m.group(4)))
    S = []
    sess = head.split("## 세션이 만든 수정판", 1)[1]
    for l in sess.split("\n"):
        m = re.match(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", l)
        if m: S.append((m.group(1), m.group(2)))
    return R, S
R, S = rows(os.path.join(B, "README.md"))
R0, S0 = rows(os.path.join(ROOT, "대조v2", "수학검사2", "전_정합1114", "README.md"))
print("기록 사본 표 행", len(R), "(사본", len(R0), ") 세션 표 행", len(S), "(사본", len(S0), ")")
print("새 기록 사본 행:"); [print("  +", r[0], "|", r[1], "|", r[2]) for r in sorted(set(R) - set(R0))]
print("지운 기록 사본 행:"); [print("  -", r[0], "|", r[2]) for r in sorted(set(R0) - set(R))]
print("새 세션 표 행:"); [print("  +", r[0]) for r in S if r not in S0]
print("지운 세션 표 행:"); [print("  -", r[0]) for r in S0 if r not in S]
bad = 0
for p, _, _, d in R:
    fp = os.path.join(B, p)
    if not os.path.isfile(fp): print("  없음", p); bad += 1
    elif sha(fp) != d: print("  SHA 불일치", p); bad += 1
print("기록 사본 표 디스크 대조: 문제", bad)
bad = 0
for p, d in S:
    fp = os.path.join(B, p)
    if not os.path.isfile(fp): print("  없음", p); bad += 1
    elif sha(fp) != d: print("  SHA 불일치", p); bad += 1
print("세션 표 디스크 대조: 문제", bad)
# 디스크에 있는데 표에 없는 기록 사본 파일
listed = {p for p, *_ in R}
extra = []
for rd in sorted(os.listdir(B)):
    if re.match(r"r[0-9a-f]{7}$", rd):
        for root_, dirs_, files_ in os.walk(os.path.join(B, rd)):
            for fn in files_:
                rel = os.path.relpath(os.path.join(root_, fn), B).replace("\\", "/")
                if rel not in listed: extra.append(rel)
print("표에 없는 기록 사본 파일", len(extra)); [print("  ?", e) for e in extra[:40]]
# 자료묶음_v2 건조 수집 대조(main의 행 계산을 되풀이; 복사하지 않음)
import 자료묶음_v2 as Z
import glob as G
base = os.path.join(ROOT, "장v2")
texts = [io.open(os.path.join(base, n), encoding="utf-8").read() for n in sorted(os.listdir(base)) if n.startswith("부록D_장")]
items = Z.collect(texts)
want = set(); seen = set(); problems = []
for d_item, rid, rel in items:
    rdir = Z.find_record_dir(rid)
    if not rdir: problems.append((d_item, rid, rel)); continue
    src = os.path.join(Z.RECORDS, rdir, rel); short = rdir[:8]
    if "*" in rel or "?" in rel:
        for fsrc in sorted(p for p in G.glob(src) if os.path.isfile(p)):
            frel = os.path.relpath(fsrc, os.path.join(Z.RECORDS, rdir)).replace("\\", "/")
            want.add((f"{short}/{frel}", d_item))
        continue
    if not os.path.exists(src): problems.append((d_item, rid, rel)); continue
    if os.path.isdir(src):
        for root_, dirs_, files_ in os.walk(src):
            dirs_[:] = [d for d in dirs_ if d != "__pycache__"]
            for fn in sorted(files_):
                frel = os.path.relpath(os.path.join(root_, fn), os.path.join(Z.RECORDS, rdir)).replace("\\", "/")
                want.add((f"{short}/{frel}", d_item))
        continue
    bn = os.path.basename(rel); sub = os.path.dirname(rel).replace("/", "__"); dn = bn
    key = (short, bn)
    if key in seen: dn = f"{sub}__{bn}" if sub else bn
    seen.add(key)
    want.add((f"{short}/{dn}", d_item))
have = {(p, d) for p, _, d, _ in R}
print("건조 수집 문제", problems)
print("건조 수집에는 있으나 표에 없음:"); [print("  +", x) for x in sorted(want - have)]
print("표에는 있으나 건조 수집에 없음:"); [print("  -", x) for x in sorted(have - want)]
