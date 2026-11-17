# -*- coding: utf-8 -*-
"""X4 (ㄹ) 보조: 「n.m절의 X」「n.m절에서 (정의한|세운|정한|둔|적은) X」 꼴의 X(첫 낱말)가 그 절 본문에 실제로 나오는지. 읽을 자리 안내용 색인. 읽기 전용."""
import glob, io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
def rel(p): return os.path.relpath(p, ROOT)
# 절 본문 모으기
sec_text = {}
cur = None
for p in sorted(glob.glob(os.path.join(CH, "장*.md"))):
    for ln in io.open(p, encoding="utf-8").read().split("\n"):
        m = re.match(r"^###+ (\d+\.\d+(?:\.\d+)?) ", ln)
        if m: cur = m.group(1); sec_text.setdefault(cur, [])
        if cur: sec_text[cur].append(ln)
def text_of(sec):
    # n.m절은 그 하위 n.m.k절도 포함
    out = []
    for s, ls in sec_text.items():
        if s == sec or s.startswith(sec + "."): out += ls
    return "\n".join(out)
PAT = re.compile(r"(\d{1,2}\.\d{1,2}(?:\.\d)?)절(?:의|에서(?: 정의한| 세운| 정한| 둔| 적은| 본| 말한| 쓴| 얻은)?|이)\s*((?:\$[^$]{1,60}\$|[가-힣A-Za-z\-]+)(?:\s+(?:\$[^$]{1,60}\$|[가-힣A-Za-z\-]+)){0,2})")
STOP = {"것", "곳", "자리", "결과", "말", "글자", "뜻", "꼴", "식", "증명", "첫", "두", "세", "네", "앞", "뒤", "끝", "처음", "표", "표에", "표의", "보조정리", "정리", "명제", "따름정리", "정의", "문단", "마지막", "같은", "그", "이", "모든", "어느", "다음", "아래", "위", "환원", "계산", "도구", "낱말", "이름", "논증", "방법", "길"}
n = 0; miss = []
for p in files:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        for m in PAT.finditer(ln):
            sec, phrase = m.group(1), m.group(2)
            if sec not in sec_text: continue
            words = [w for w in re.split(r"\s+", phrase) if w]
            key = None
            for w in words:
                core = w.strip("$")
                core = re.sub(r"(의|은|는|이|가|을|를|과|와|로|에|도|만|라|다|이다|에서|처럼|마다|까지|부터)$", "", core) if not w.startswith("$") else core
                if core and core not in STOP and len(core) >= 2:
                    key = (w, core); break
            if not key: continue
            n += 1
            body = text_of(sec)
            w, core = key
            found = (w in body) if w.startswith("$") else (core in body)
            if not found:
                miss.append((rel(p), no, sec, phrase, ln[max(0, m.start()-50):m.end()+30]))
print("## 절 가리킴에 딸린 낱말 검사 수:", n, "| 그 절 본문에 없는 낱말:", len(miss))
for t in miss: print("  ", t)
