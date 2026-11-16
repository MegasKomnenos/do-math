# -*- coding: utf-8 -*-
"""V3 잔존 전수: 장부 3절 4열의 첫 판 낱말, 칸/경계/블록/배치/…열 꼴을 본문(장·부록 A·D)에서 센다. python -I"""
import glob, io, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BODY = [p for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) if not p.endswith(("부록B.md", "부록C.md"))]
led = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read().split("\n")
i3 = next(i for i, l in enumerate(led) if l.startswith("## 3. 낱말 사전"))
i4 = next(i for i, l in enumerate(led) if i > i3 and l.startswith("## 4."))
tokens = {}
for l in led[i3:i4]:
    if not l.startswith("| ") or l.startswith("| 낱말") or l.startswith("|---"):
        continue
    c = [x.strip() for x in l.strip()[1:-1].split("|")]
    if len(c) != 4:
        continue
    w1 = [x.strip() for x in re.split(r"[,;·]", c[0])]
    col4 = c[3]
    # 「A」는 「B」 꼴: A가 첫 판 낱말
    quoted = re.findall(r"「([^」]+)」는", col4)
    rest = re.sub(r"「[^」]+」는 「[^」]+」", "", col4)
    rest = re.sub(r"\([^)]*\)", "", rest)
    cands = quoted + [x.strip() for x in re.split(r"[;,]", rest)]
    for t in cands:
        t = t.strip().strip("「」")
        if not t or t in ("같음", "—", "없음") or "같음" in t or t in w1 or len(t) < 2:
            continue
        if re.search(r"[A-Za-z$]", t) or "\\" in t:
            continue
        tokens.setdefault(t, c[0])
mode = sys.argv[1] if len(sys.argv) > 1 else "words"
if mode == "words":
    for t, w1 in sorted(tokens.items()):
        hits = []
        for p in BODY:
            for i, line in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
                if t in line:
                    hits.append((os.path.basename(p), i, line))
        if hits:
            print(f"== 「{t}」 (3절 행: {w1}) {len(hits)}건")
            for f, i, line in hits[:6]:
                j = line.find(t)
                print(f"   {f}:{i}: …{line[max(0,j-60):j+60]}…")
else:
    PAT = {"칸": re.compile(r"칸"), "경계": re.compile(r"경계"), "블록": re.compile(r"블록"), "배치": re.compile(r"배치"),
           "X열": re.compile(r"(크기열|걸음열|초과열|간격열|길이 열|용량 구간 길이 열)"), "상해": re.compile(r"(?<!손)상해(?!석)"),
           "임계점": re.compile(r"임계점"), "한쪽": re.compile(r"한쪽 [^ ]+"), "사슬해": re.compile(r"사슬 해|한 줄 사슬|해석적 사슬")}
    ALLOW_K = re.compile(r"\$r\$ 칸|한 칸|번째 칸|증인의 칸|표의 칸|주차 칸|칸 차분|\$\sigma\$ 칸|두 칸|세 칸|\$j\$ 칸|칸 떨어|칸 민|칸 위|칸씩|칸 앞|칸 뒤|칸 더|칸 큰|칸 작|칸만|칸이 넓|칸의 수")
    ALLOW_B = re.compile(r"두 절반의 경계|증가 경계|반감 경계|경계 다항식|경계 응답|경계항|경계값|셀 경계|경계점|경계 조건|가장자리")
    key = sys.argv[1]
    for p in BODY:
        for i, line in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
            for m in PAT[key].finditer(line):
                s = line[max(0, m.start()-55):m.end()+45]
                if key == "칸" and ALLOW_K.search(line[max(0, m.start()-8):m.end()+6]):
                    continue
                if key == "경계" and ALLOW_B.search(line[max(0, m.start()-8):m.end()+6]):
                    continue
                print(f"{os.path.basename(p)}:{i}: …{s}…")
