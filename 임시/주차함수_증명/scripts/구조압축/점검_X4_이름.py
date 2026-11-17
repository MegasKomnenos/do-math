# -*- coding: utf-8 -*-
"""X4 (ㅁ) 이름: 머리의 이름 목록, 지운 진술·옛 절 제목의 이름 흔적, 「…」 인용 문자열, 절 제목의 본문 호출. 읽기 전용."""
import glob, io, os, re
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
def rel(p): return os.path.relpath(p, ROOT)
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)\s*(?:\(([^)]*?)(?:;.*?)?\))?\s*(?:\[.*?\])?\.\*\*")
names = {}
texts = {p: io.open(p, encoding="utf-8").read().split("\n") for p in files}
for p in files:
    for no, ln in enumerate(texts[p], 1):
        m = HEAD.match(ln)
        if m and m.group(3): names[m.group(2)] = (m.group(3).strip(), rel(p), no)
print("## 이름 있는 머리:", len(names))
OLD = ["주 정리의 둘째 증명", "주 정리의 첫째 증명", "주 정리와 둘째 층 한 칸 비교의 동치", "둘째 층 한 칸 비교", "둘째 층의 한 나무 하계",
       "머리 합의 안쪽 층", "쌍 항의 정수 꼴", "무게 증분의 하계", "평평한 핵심의 하계", "짝 재배열", "두 장부의 차", "두 장부의 사전",
       "벌크의 둘째 증명", "FLQ 경로", "재생 원천", "첫 층 기저", "평평한 핵심", "평평한 무게", "머리 합", "출발 빚", "무게 증분", "감소율",
       "덮인 문턱", "머리 합 조건", "증가 시작점", "착지 비", "요구값", "쌍대 변수", "무게중심", "평평한 꼬리", "공유 입력과 고유 입력",
       "첫째 문턱", "둘째 문턱", "둘째 길", "첫째 길", "다른 길", "비교 상대", "두 장부", "입력 비교", "한 칸 비교"]
print("## 지운 진술·절·낱말의 이름 흔적(장·부록 D)")
tot = Counter()
for p in files:
    for no, ln in enumerate(texts[p], 1):
        for w in OLD:
            for m in re.finditer(re.escape(w), ln):
                tot[w] += 1
                print(f"   {rel(p)}:{no} 「{w}」 …{ln[max(0,m.start()-60):m.end()+50]}…")
print("   합:", dict(tot))
print()
# 절 제목을 본문이 부르는 자리
secs = {}
for p in files:
    for no, ln in enumerate(texts[p], 1):
        m = re.match(r"^###+ (\d+\.\d+(?:\.\d+)?) (.*)", ln)
        if m: secs[m.group(1)] = m.group(2).strip()
print("## 절 제목 문자열이 본문(머리 밖)에 나오는 자리")
for s, t in secs.items():
    core = re.sub(r"\$[^$]*\$", "", t).strip()
    if len(core) < 4: continue
    for p in files:
        for no, ln in enumerate(texts[p], 1):
            if ln.startswith("#"): continue
            if core in ln:
                i = ln.find(core)
                print(f"   {s} 「{core}」 ← {rel(p)}:{no} …{ln[max(0,i-50):i+len(core)+40]}…")
print()
print("## 「…」 인용 문자열 전수(서로 다른 것; 수·출처)")
q = Counter(); qwhere = defaultdict(list)
for p in files:
    for no, ln in enumerate(texts[p], 1):
        for m in re.finditer(r"「([^」]{1,40})」", ln):
            q[m.group(1)] += 1; qwhere[m.group(1)].append(f"{os.path.basename(p)}:{no}")
for k, v in sorted(q.items(), key=lambda x: (-x[1], x[0])):
    print(f"   x{v} 「{k}」  {qwhere[k][:4]}")
print()
print("## 머리 이름 목록")
for lab, (nm, f, no) in sorted(names.items(), key=lambda x: (x[1][1], x[1][2])):
    print(f"   {f}:{no} {lab} | {nm}")
