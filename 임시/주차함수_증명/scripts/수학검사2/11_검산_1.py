# -*- coding: utf-8 -*-
"""수학검사2 태그 11, 검산 1: 11.2 표 45행을 부록 D 항목과 전수 대조한다(읽기 전용).
(가) 「확인하는 진술」 열의 라벨 집합 = D 항목 머리 괄호의 라벨 집합(종류 포함)
(나) 「산술 등급」 열의 등급 집합 = D 「산술 등급」 줄의 첫 문장(「기록의 계산은…」 앞)에서 읽은 등급 집합
(다) 「재계산」 열의 꺾쇠 괄호 = D 「독립 재계산」 줄 첫머리 괄호
(라) 「독립 재계산」 열의 모든 수식 토큰·산문 숫자가 D 「독립 재계산」 줄(필요하면 항목 전체)에 있는지, 문장 단위 포함
(마) 「쓰인 곳」 열 = 진술 머리가 있는 절
"""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
ch11 = open(R+"장v2/장11.md", encoding="utf-8").read().split("\n")
rows = {}
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔.*?〕) \| (.*) \|$", line)
    if m:
        rows[m.group(1)] = dict(ln=ln, stmts=m.group(2), grade=m.group(3), where=m.group(4), rec=m.group(5), indep=m.group(6))
items = {}; order = []
for f in sorted(glob.glob(R+"장v2/부록D_장*.md")):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^### D\.\{\{(D:[^}]+)\}\}", txt)
    for i in range(1, len(parts), 2):
        lab, body = parts[i], parts[i+1]
        head = body.split("\n", 1)[0].strip()
        hp = re.findall(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", head)
        grade = re.search(r"\*\*산술 등급\.\*\*\s*(.*)", body)
        indep = re.search(r"\*\*독립 재계산\.\*\*\s*(.*)", body)
        items[lab] = dict(file=f.split("/")[-1], headpar=hp[0] if hp else "", grade=grade.group(1) if grade else "",
                          indep=indep.group(1) if indep else "", body=body)
        order.append(lab)
# 절 위치
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}(.*?)\*\*")
secof = {}; heads = {}; kinds = {}
for f in sorted(glob.glob(R+"장v2/장*.md")):
    sec = None
    for l in open(f, encoding="utf-8"):
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l)
        if ms: sec = ms.group(1)
        m = HEAD.match(l)
        if m and not m.group(3).startswith("의 증명"): secof[m.group(2)] = sec; kinds[m.group(2)] = m.group(1); heads[m.group(2)] = m.group(3)
print("11.2 행", len(rows), "/ D 항목", len(items), "/ 표에 없는 항목", [l for l in order if l not in rows], "/ 항목 없는 행", [l for l in rows if l not in items])
GR = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "인증 아님"]
def grades_in(s):
    return set(g for g in GR if g in s)
def labset(s):
    out = set()
    for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}((?:·\{\{\d+:[^}]+\}\})*)", s):
        out.add((m.group(1), m.group(2)))
        for x in re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(3)): out.add((m.group(1), x))
    return out
MATH = re.compile(r"\$[^$\n]+\$")
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])")
def norm(s):
    s = s.replace(r"\vert ", "|").replace(r"\vert", "|")
    s = s.replace("이 글을 쓰며", "이 글의 재계산에서는").replace("「재계산」 열의 꺾쇠 괄호", "이 문단 머리의 꺾쇠 괄호")
    return re.sub(r"\s+", "", s)
nbad = 0
for lab in order:
    r, it = rows[lab], items[lab]
    msgs = []
    # (가)
    a, b = labset(r['stmts']), labset(it['headpar'])
    if a != b: msgs.append(f"(가) 라벨 다름: 표 {sorted(a)} / D 머리 {sorted(b)}")
    # (나)
    gline = re.split(r"기록의 계산은|기록의 원 계산은", it['grade'])[0]
    ga, gb = grades_in(r['grade']), grades_in(gline)
    if ga != gb: msgs.append(f"(나) 등급 다름: 표 {sorted(ga)} / D 첫 문장 {sorted(gb)} ⟨{it['grade'][:200]}⟩")
    # 표 등급 열 자체가 등급 이름만으로 이루어졌는지
    rest = r['grade']
    for g in GR: rest = rest.replace(g, "")
    if re.sub(r"[,\s·]", "", rest): msgs.append(f"(나) 표 등급 열에 등급 이름 아닌 글자: {r['grade']}")
    # (다)
    m = re.match(r"(〔.*?〕)\s*(.*)", it['indep'])
    dbr, dtxt = (m.group(1), m.group(2)) if m else ("", it['indep'])
    if dbr != r['rec']: msgs.append(f"(다) 괄호 다름:\n     표 {r['rec']}\n     D  {dbr}")
    # (라) 토큰
    nd, nb_ = norm(dtxt), norm(it['body'])
    for tok in MATH.findall(r['indep']):
        if norm(tok) not in nd:
            msgs.append(f"(라) 수식 토큰이 D 독립 재계산 줄에 없음: {tok}" + ("" if norm(tok) not in nb_ else " (항목의 다른 줄에는 있음)"))
    for tok in NUM.findall(MATH.sub(" ", r['indep'])):
        if tok not in MATH.sub(" ", dtxt):
            msgs.append(f"(라) 산문 숫자가 D 독립 재계산 줄에 없음: {tok}")
    sents = re.split(r"(?<=다\.)\s+|(?<=\)\.)\s+", r['indep'])
    for s in sents:
        if norm(s) and norm(s) not in nd:
            msgs.append(f"(라) 문장이 D 줄에 없음: {s[:300]}")
    # (마)
    st = re.findall(r"\{\{(\d+:[^}]+)\}\}", r['stmts'])
    secs = sorted(set(secof.get(s, "?") for s in st), key=lambda x: [int(t) for t in x.split(".")] if x != "?" else [99])
    if "·".join(secs) != r['where']: msgs.append(f"(마) 쓰인 곳 다름: 표 {r['where']} / 진술 절 {secs}")
    # 머리 등급 대조(진술 머리의 계산 보조/증거 괄호)
    for s in st:
        h = heads.get(s, "")
        hg = set();
        for mm in re.finditer(r"계산 (?:보조|증거)\(([^)]*)\)", h): hg |= grades_in(mm.group(1))
        if hg and not (hg & ga): msgs.append(f"(머리) {s} 머리 등급 {sorted(hg)} vs 표 {sorted(ga)}")
        if not hg and "계산" not in h: msgs.append(f"(머리) {s} 머리에 계산 표지 없음: {h[:100]}")
    status = "OK" if not msgs else "<<<"
    print(f"\n[{r['ln']}행] {lab} ({it['file']}) {status}")
    for x in msgs: print("   ", x)
    nbad += bool(msgs)
print("\n문제 있는 행:", nbad)
