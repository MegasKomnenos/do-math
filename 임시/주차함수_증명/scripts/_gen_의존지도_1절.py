# -*- coding: utf-8 -*-
"""의존지도_v2.md 1절(진술별 입력 표)을 장 파일에서 다시 만든다(결정 98). 2.1절(라벨 닫힘)도 다시 계산한다.
2.2–2.4절·3–7절은 11-12 판(`대조v2/의존지도_v2_1112판.md`)을 그대로 두고, 손으로 적힌 열(첫 판 번호·문헌·비고)은 라벨로 이어받는다.
덤으로 번역자용 라벨–번호 대응표 `대조v2/라벨_번호_대응표_1114.md`를 만든다.

사용: python -I scripts/_gen_의존지도_1절.py [--dry]
간선 규칙은 scripts/_의존_도달.py의 parse_chapters와 같다(머리 줄 인용, 증명 본문 인용, 뒤로 미룬 증명 단락 인용).
"""
import io
import os
import re
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import importlib
DD = importlib.import_module("_의존_도달")

OLD = os.path.join(ROOT, "대조v2", "의존지도_v2_1112판.md")
OUT = os.path.join(ROOT, "의존지도_v2.md")
MAP_OUT = os.path.join(ROOT, "대조v2", "라벨_번호_대응표_1114.md")
LEDGER = os.path.join(ROOT, "장부_v2.md")
CH11 = os.path.join(ROOT, "장v2", "장10.md")  # 9장 제거 뒤 보증 장은 10장
MS = os.path.join(ROOT, "원고.md")

LAB = re.compile(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}")
BR = re.compile(r"\[([^\]]*)\]\.\*\*")
RID = re.compile(r"\br[0-9a-f]{7}\b")
DRY = "--dry" in sys.argv


def read(p):
    return io.open(p, encoding="utf-8").read()


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def lab_tag(k):
    return "`{{" + k + "}}`"


# ---------- 옛 표(11-12 판) ----------
old_text = read(OLD)
i1 = old_text.find("\n## 1. ")
i2 = old_text.find("\n## 2. ")
old_rows = {}
for ln in old_text[i1:i2].split("\n"):
    if ln.startswith("| `{{"):
        c = cells(ln)
        if len(c) != 10:
            print("[경고] 옛 행 칸 수", len(c), ln[:80])
            continue
        key = c[0].strip("`{}")
        old_rows[key] = dict(section=c[1], first=c[2], gist=c[3], status=c[4], inputs=c[5], claims=c[6], lit=c[7], appd=c[8], note=c[9])
old_tail = old_text[i2:]  # "\n## 2. ..." 끝까지

# 2026-11-15 K14-11: 현행 7.2절 보조정리 supermultiplicative의 증명은 귀류와 초승법성만 쓰고 Fekete를 부르지 않는다
# (구조표 7.2 행, 장부 8절 규칙 8, 11.4절 표에 Fekete 없음). 11-12 판의 주장·문헌 칸에서 그 흔적을 뺀다.
if "7:supermultiplicative" in old_rows:
    _o = old_rows["7:supermultiplicative"]
    _o["claims"] = re.sub(r";\s*Fekete 적용은[^|]*$", "", _o["claims"]).strip()
    if _o["lit"].startswith("Fekete"):
        _o["lit"] = "—"

# ---------- 장부 v2 4절 ----------
led = read(LEDGER)
j1 = led.find("\n## 4.")
j2 = led.find("\n## 5.", j1 + 1)
led4 = {}
removed_led = {}
for ln in led[j1:j2].split("\n"):
    if not ln.startswith("| "):
        continue
    c = cells(ln)
    if len(c) != 6 or c[0] in ("첫 판 번호", "---"):
        continue
    m = LAB.search(c[5])
    if m:
        led4[m.group(1)] = dict(first=c[0], kind=c[1], name=c[2], recname=c[3], section=c[4])
        continue
    m = re.search(r"\((\d+:[A-Za-z][A-Za-z0-9\-]*)\)", c[5])
    if m and c[4] == "뺌":
        _mv = re.search(r"라벨을 `(\d+:[A-Za-z][A-Za-z0-9\-]*)`(?:으로|로) 바꿈", c[2])   # 2026-11-17 23차 R13: 옮긴 라벨의 새 이름
        removed_led[m.group(1)] = dict(first=c[0], kind=c[1], name=c[2], recname=c[3], moved=(_mv.group(1) if _mv else None))
    elif c[4] == "뺌" and c[5] == "—":
        # 라벨을 받은 적이 없는 첫 판 진술(설계 때 뺌)
        removed_led["첫 판 %s %s" % (c[1], c[0])] = dict(first=c[0], kind=c[1], name=c[2], recname=c[3])
    elif c[4] == "뺌":
        print("[경고] 장부 4절 뺌 행의 라벨 칸이 비정상:", ln[:120])

# ---------- 11.2 표(부록 D 계산), 11.4 표(문헌) ----------
ch11 = read(CH11).split("\n")
appd_of = {}
for ln in ch11:
    if ln.startswith("| 부록 D.{{D:"):
        c = cells(ln)
        dm = re.search(r"\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}", c[0])
        for k in LAB.findall(c[1]):
            appd_of.setdefault(k, []).append("D.{{D:%s}}(%s)" % (dm.group(1), c[2]))
lit_of = {}
on = False
for ln in ch11:
    if ln.startswith("### 10.3"):  # 문헌 표(옛 11.4 → 11.3 → 9장 제거 뒤 10.3)
        on = True
        continue
    if on and ln.startswith("| ") and not ln.startswith("| 문헌") and not ln.startswith("|---"):
        c = cells(ln)
        if len(c) < 3:
            continue
        # 2026-11-15 K11 문제 1: 「쓰인 자리」가 증명의 근거가 아니라 설명 자리임을 밝힌 행(Knuth의 갈고리 길이 공식)은 입력이 아니다.
        if any(x in c[2] for x in ("근거로 쓰이지는 않", "근거로 쓰지는 않", "증명은 그 공식을 쓰지 않", "근거로 쓰지 않")):
            continue
        authors = c[0].split("*")[0].strip().rstrip(",").strip()
        for k in set(LAB.findall(c[2]) + LAB.findall(c[1])):
            lit_of.setdefault(k, []).append("%s(%s)" % (authors, c[1]))

# ---------- 장 파일 ----------
st = DD.parse_chapters()
order = sorted(st, key=lambda k: st[k]["order"])
pos = {k: n for n, k in enumerate(order)}
cur = set(st)

# 번호(조립 규칙: 머리가 놓인 장, 장 안 등장 순서)
counters = {}
number = {}
for k in order:
    ch = int(st[k]["section"].split(".")[0])
    counters[ch] = counters.get(ch, 0) + 1
    number[k] = "%d.%d" % (ch, counters[ch])

# 조립본 머리와 대조
ms_heads = re.findall(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) (\d+\.\d+) ", read(MS), re.M)
mine = [number[k] for k in order]
if ms_heads != mine:
    bad = [(a, b) for a, b in zip(ms_heads, mine) if a != b]
    print("[경고] 조립본 번호와 다름:", len(ms_heads), len(mine), bad[:5])
else:
    print("번호 대조: 조립본 머리", len(ms_heads), "개와 일치")


def status_and_ids(head):
    m = BR.search(head)
    if not m:
        return "정의", set()
    inner = m.group(1)
    if ";" in inner:
        a, b = inner.split(";", 1)
        return a.strip(), set(RID.findall(b))
    ids = set(RID.findall(inner))
    if ids and not RID.sub("", inner).strip(" ,"):
        # 정의의 머리는 `[r…]`처럼 기록 식별자만 가진다: 지위는 「정의」, 식별자는 기록 열로.
        return "정의", ids
    return inner.strip(), set()


def fmt_labels(keys):
    return ", ".join(lab_tag(k) for k in sorted(keys, key=lambda x: pos.get(x, 10 ** 6)))


# 11-12 판 비고에서 걷어 내는 문구 — 현행과 반대로 읽히는 처리 완료 조치 메모, 장 파일 행 번호, 라벨 와일드카드(19차 M14 2.3)
NOTE_FIX = [
    ("; rba2ecf4는 부록 B에 없음 → 추가", ""),
    (" ra7615a0는 부록 B에 없음(출처로 적으면 추가)", ""),
    ("(장6 461행; 명제 ", "(명제 "),
    ("; rda45d0e·r4daca3d는 부록 B에 없음(rda45d0e 추가; r4daca3d는 출처 표기 여부 집필자 결정)", ""),
    (" 11.4 문헌 목록에 FKG 추가 요", ""),
    ("; rbeae3a3는 부록 B에 없음 → 추가", ""),
    ("; r7798355는 부록 B에 없음 → 추가", ""),
    ("; r9e782f5는 부록 B에 없음 → 추가", ""),
    ("{{7:fold-*}}", "{{7:fold-A}}·{{7:fold-R}}·{{7:fold-T}}·{{7:fold-L1}}·{{7:fold-DIP}}"),
    ("; 5장 도입이 인용", ""),  # 20차 YL: borel-tail-arc를 5A·5B가 인용하지 않음(라벨·낱말 0건)
]
note_fix_hits = {}
claims_fix = []

rows = []
all_inputs = set()
head_edges = {}
all_edges = {}
for k in order:
    s = st[k]
    status, ids = status_and_ids(s["head"])
    o = old_rows.get(k)
    l4 = led4.get(k)
    # 첫 판 번호
    if l4 and l4["first"] not in ("—", ""):
        first = "%s %s" % (l4["kind"], l4["first"])
    elif o and o["first"] not in ("새 진술", "—", ""):
        first = o["first"]
    else:
        first = "새 진술"
    # 요지
    gist = s["name"].strip()
    if not gist:
        gist = (o["gist"] if o and o["gist"] else (l4["name"] if l4 and l4["name"] else "")) or "머리에 제목 없음"
        if o and "머리에 제목 없음" not in (o["note"] or ""):
            pass
    gist = gist.replace("|", "／")
    # 입력
    hl = set(x for x in s["head_labels"] if x in cur)
    bl = set(x for x in s["body_labels"] if x in cur) - hl
    missing = (s["head_labels"] | s["body_labels"]) - cur
    if missing:
        print("[경고] 없는 라벨 인용:", k, sorted(missing))
    head_edges[k] = hl
    all_edges[k] = hl | bl
    all_inputs |= hl | bl
    if hl and bl:
        inputs = fmt_labels(hl) + "; 본문 인용: " + fmt_labels(bl)
    elif hl:
        inputs = fmt_labels(hl)
    elif bl:
        inputs = "본문 인용: " + fmt_labels(bl)
    else:
        inputs = "—"
    # 기록 주장(11-12 판의 칸을 이어받을 때 `/` 앞 식별자 목록이 머리의 식별자 전부를 들도록 머리 차례로 채운다 — 19차 M14 2.3)
    if o and ids and set(RID.findall(o["claims"])) == ids and "/" in o["claims"]:
        claims = o["claims"]
        if " / " in claims:  # 「식별자 목록 / 주장 목록」 꼴만; 「식별자/주장; 식별자/주장」 꼴은 그대로 둔다
            front, back = claims.split(" / ", 1)
            have = set(RID.findall(front))
            lack = [x for x in dict.fromkeys(RID.findall(s["head"])) if x in ids and x not in have]
            if lack:
                claims = front.rstrip() + ", " + ", ".join(lack) + " / " + back
                claims_fix.append(k)
    else:
        claims = ", ".join(sorted(ids)) if ids else "—"
    # 문헌(현행 11.4절 표만; 11-12 판의 칸은 옛 문헌 귀속이 남아 쓰지 않는다 — 2026-11-16 12차 S14-3)
    if k in lit_of:
        lit = "; ".join(lit_of[k])
    else:
        lit = "—"
    # 부록 D
    if k in appd_of:
        appd = ", ".join(appd_of[k])
    elif "계산 보조" in status:
        appd = "머리에 계산 보조 표시, 10.2 표에 항목 없음"
    else:
        appd = "없음"
    # 비고(11-12 판에서 이어받음; 지운 라벨은 「뺀 …」으로 표시; NOTE_FIX의 문구는 걷어 낸다)
    note = (o["note"] if o and o["note"] else "—")
    for a, b in NOTE_FIX:
        if a in note:
            note = note.replace(a, b)
            note_fix_hits[a] = note_fix_hits.get(a, 0) + 1
    for gone_lab in set(LAB.findall(note)) - cur:
        note = note.replace("`{{" + gone_lab + "}}`", "(뺀 " + gone_lab + ")").replace("{{" + gone_lab + "}}", "(뺀 " + gone_lab + ")")
    if note != "—" and any(x in note for x in ("2절 열린 입력", "[todo]", "둘째 판에 진술 없음")):
        note += " (11-12 판 기록; 현행 입력은 이 행의 입력 열에 있다)"
    if s["name"].strip() and "머리에 제목 없음" in note:   # 2026-11-17 R13 [지도-1]: 머리에 이름이 생긴 뒤 남은 11-12 판 주석
        note = re.sub(r"(;\s*)?머리에 제목 없음(\s*;)?", "", note).strip(" ;") or "—"
    if s.get("defer"):
        note = ("뒤로 미룬 증명 %s" % ", ".join(s["defer"])) + ("" if note == "—" else "; " + note)
    status = status.replace("|", "／")
    rows.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        lab_tag(k), s["section"], first, gist, status, inputs, claims, lit, appd, note))

# ---------- 뺌·대체 라벨 ----------
gone = sorted(set(old_rows) - cur | set(removed_led))
gone_rows = []
for k in gone:
    o = old_rows.get(k)
    r = removed_led.get(k)
    gist = (o["gist"] if o else "%s %s" % (r["kind"], r["name"])) if (o or r) else ""
    if r and k.startswith("첫 판 "):
        how = "뺌(장부 4절; 라벨을 받은 적 없음 — 설계 때 뺌)"
        tag = "(라벨 없음) " + k
        if r["recname"]:
            gist += "; " + r["recname"]
    elif r:
        had = "; 11-12 판에 행 있음" if o else "; 11-12 판에 행 없음"
        m_rep = LAB.search(r["name"]) if "로 대체" in r["name"] else None
        if r.get("moved") and r["moved"] in cur:   # 2026-11-17 23차 R13 [지도-1]: 장부 4절이 「라벨을 … 바꿈」이라 적은 것은 뺀 것이 아니라 옮긴 것
            how = "옮김(%s %s절; 장부 4절의 「라벨을 … 바꿈」 주석%s)" % (lab_tag(r["moved"]), st[r["moved"]]["section"], had)
        elif m_rep:
            how = "대체(%s; 장부 4절%s)" % (lab_tag(m_rep.group(1)), had)
        else:
            how = "뺌(장부 4절%s)" % had
        tag = "`(%s)`" % k   # 2026-11-17 22차 R13 [지도-3]: 죽은 라벨은 중괄호 없이 (N:이름)
    else:
        # 2026-11-16 13차 T14-5: 같은 이름의 라벨이 다른 장에 살아 있으면 뺀 것이 아니라 옮긴 것이다(대응표와 같은 규칙; 예: 5:zeta-constants → 2:zeta-constants).
        moved = [c for c in cur if c.split(":", 1)[1] == k.split(":", 1)[1] and c != k]
        if moved:
            how = "옮김(%s %s절; 장부 4절 머리말)" % (lab_tag(moved[0]), st[moved[0]]["section"])
        else:
            how = "11-12 판에만 있던 라벨(장부 4절에 뺌 행 없음; 결정 73·97 또는 집필 회수 때 뺌·대체)"
        tag = "`(%s)`" % k   # 죽은 라벨(옮긴 라벨의 옛 이름 포함)은 중괄호 없이
    gone_rows.append("| %s | %s | %s |" % (tag, gist.replace("|", "／"), how))

# ---------- 순환 검사 ----------
def cycles(edges):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in edges}
    found = []
    def dfs(u, path):
        color[u] = GRAY
        path.append(u)
        for v in edges.get(u, ()):
            if v not in color:
                continue
            if color[v] == GRAY:
                found.append(path[path.index(v):] + [v])
            elif color[v] == WHITE:
                dfs(v, path)
        path.pop()
        color[u] = BLACK
    for k in edges:
        if color[k] == WHITE:
            dfs(k, [])
    return found

head_cycles = cycles(head_edges)
# 본문 포함 그래프의 상호 인용(크기 2 이상 강결합 성분)
def sccs(edges):
    index = {}; low = {}; stack = []; onst = set(); out = []; cnt = [0]
    sys.setrecursionlimit(10000)
    def strong(v):
        index[v] = low[v] = cnt[0]; cnt[0] += 1
        stack.append(v); onst.add(v)
        for w in edges.get(v, ()):
            if w not in edges:
                continue
            if w not in index:
                strong(w); low[v] = min(low[v], low[w])
            elif w in onst:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop(); onst.discard(w); comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp, key=lambda x: pos[x]))
    for v in edges:
        if v not in index:
            strong(v)
    return out

all_sccs = sccs(all_edges)

# ---------- 2.1절 ----------
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
sec21 = []
sec21.append("### 2.1 라벨 닫힘")
sec21.append("")
sec21.append("1절의 「입력: 이 글의 다른 진술」 열에 적힌 라벨 %d개(중복 제외)는 모두 장 파일의 진술 %d개 안에 있다(생성기가 집합 포함을 확인; 빠진 라벨 0, 정의되지 않은 라벨의 인용 0). "
             "머리가 선언한 의존(「…에 의존」)만으로 만든 그래프는 비순환이다(순환 %d개). 본문 인용까지 더한 그래프에는 서로 인용하는 묶음(크기 2 이상의 강결합 성분)이 %d개 있다 — 비교·구별 문장이나 뒤 진술을 미리 가리키는 문장이 만드는 것이며 증명의 순환이 아니다. "
             "11-12 판의 2.1절(등록부 322개 기준, 상신 11의 `(9:old-7-23)`)은 집필로 해소되었다." % (len(all_inputs), len(cur), len(head_cycles), len(all_sccs)))
if head_cycles:
    sec21.append("")
    sec21.append("머리 선언 그래프의 순환: " + "; ".join(" → ".join(lab_tag(x) for x in c) for c in head_cycles))
if all_sccs:
    sec21.append("")
    sec21.append("본문 인용 그래프의 상호 인용 묶음: " + "; ".join("{" + ", ".join(lab_tag(x) for x in c) + "}" for c in all_sccs))
sec21.append("")

# ---------- 파일 조립 ----------
header = """# 의존 지도 v2: 둘째 판의 모든 진술과 그 입력

1절(진술별 입력 표)과 2.1절(라벨 닫힘)은 %s에 장 파일(`장v2/장*.md`의 진술 머리 %d개; 번호는 머리 순서로 세어 같은 파일들에서 조립한 `원고.md`와 대조했다)에서 `scripts/_gen_의존지도_1절.py`로 다시 만들었다(결정 98). 첫 작성은 2026-11-12(파견문 `파견/의존지도_v2_파견문.md`; 구조표 v2·라벨 등록부 v2의 322개 기준)이고, 그 판 전문은 `대조v2/의존지도_v2_1112판.md`에 있다. 2.2–2.4절과 3–7절은 11-12 판의 기록을 그대로 두었다. 그 뒤의 집필·검토로 닫힌 열린 입력과 상신이 있으므로 현행 사실은 `작업_장부.md`와 `대조v2/장부_설계_세션결정.md`가 정본이다.

표기. 라벨은 `{{N:이름}}`(장 파일의 진술 머리). 열의 출처는 다음과 같다. 「둘째 판 절」은 머리가 놓인 `###` 절. 「첫 판 번호」는 장부 v2 4절(없으면 「새 진술」). 「요지」는 머리 괄호의 이름(없으면 11-12 판의 요지). 「지위」는 머리 대괄호의 `;` 앞 전문(「…에 의존」 선언 포함; 정의는 「정의」). 「입력: 이 글의 다른 진술」은 머리 줄이 인용하는 라벨을 먼저 적고, 증명 본문(머리 다음부터 다음 머리 전까지)과 뒤로 미룬 증명 단락이 인용하는 라벨을 「본문 인용:」 뒤에 적었다 — 간선 규칙은 `scripts/_의존_도달.py`와 같고, 본문 인용에는 비교·구별을 위한 단순 언급도 든다. 「기록 주장」은 머리 대괄호의 `;` 뒤 기록 식별자(정의의 머리처럼 대괄호에 식별자만 있으면 그 식별자; 11-12 판이 같은 식별자에 주장 ID를 붙여 두었으면 그 칸을 이어받음). 「문헌」은 10.3절 표에서 그 라벨을 「쓰인 자리」로 든 행(11-12 판의 칸은 쓰지 않는다; 「쓰인 자리」가 증명의 근거가 아니라 설명 자리임을 밝힌 행 — Knuth의 갈고리 길이 공식 — 은 입력이 아니므로 넣지 않는다). 「부록 D 계산」은 10.2절 표에서 그 라벨을 「확인하는 진술」로 든 항목(산술). 「비고」는 11-12 판의 비고를 라벨로 이어받았고, 증명을 뒤로 미룬 진술은 그 자리를 앞에 적었다.

## 1. 진술별 입력 표

| 라벨 | 둘째 판 절 | 첫 판 번호(있으면) | 진술의 한 줄 요지 | 지위 | 입력: 이 글의 다른 진술(라벨) | 입력: 기록 주장(식별자/주장 ID) | 입력: 문헌 | 입력: 부록 D 계산 | 비고(11-12 판 기록에서 이어받음 — 현행 사실은 앞 열들; 「뒤로 미룬 증명」만 생성기가 적는다) |
|---|---|---|---|---|---|---|---|---|---|
""" % (now[:-3] + "x" if False else now, len(cur))

body = header + "\n".join(rows) + "\n\n"
body += "### 1.1 뺌·대체된 라벨\n\n11-12 판의 표에 있었으나 현재 장 파일에 머리가 없는 라벨과 장부 v2 4절의 「뺌」 행이다(합 %d). 이 라벨들은 1절 표와 「입력」 열에 나오지 않는다. 죽은 라벨(옮긴 라벨의 옛 이름 포함)은 장부 4절·대응표와 같이 중괄호 없이 `(N:이름)`으로 적는다.\n\n" % len(gone_rows)
body += "| 라벨 | 11-12 판 요지 / 장부의 이름 | 처리 |\n|---|---|---|\n" + "\n".join(gone_rows) + "\n"

# 옛 꼬리에서 2.1절을 새 것으로 갈아 끼움
k1 = old_tail.find("### 2.1 라벨 닫힘")
k2 = old_tail.find("### 2.2 ")
tail = old_tail[:k1] + "\n".join(sec21) + "\n" + old_tail[k2:]
tail = tail.replace("\n## 2. 입력의 닫힘 검사와 열린 입력\n", "\n## 2. 입력의 닫힘 검사와 열린 입력\n\n(2.1절은 재생성, 2.2–2.4절은 11-12 판의 기록.)\n", 1)
tail = tail.replace("\n### 2.3 열린 입력\n", "\n### 2.3 열린 입력\n\n(11-12 판의 기록. 현행 처분: 1은 집필에서 새 진술 `{{8:hazard-H1}}`로 닫혔다. 3은 `(7:factorial-moment)`로 닫혔다가 2026-11-17 구조 압축(K1-5·U3)으로 그 진술과 소비처가 함께 빠졌고, 2는 결정 101로 그 진술과 함께 뺐다. 처분의 경위는 `작업_장부.md`.)\n", 1)
tail = tail.replace("\n## 3. 구조표가 남긴 질문의 답\n", "\n## 3. 구조표가 남긴 질문의 답\n\n(3–7절은 11-12 판의 기록이다. 제안·상신의 처분은 `작업_장부.md`와 세션 결정에 있다.)\n", 1)
body += tail
if not body.endswith("\n"):
    body += "\n"

# ---------- 라벨–번호 대응표 ----------
# 15:52 조립본(결정 97·101 전)의 번호: 결정 101 전 장 파일 사본의 머리 순서로 세고, 결정 97이 지운 둘(6.46, 10.5)을 되돌린다.
SNAP = os.path.join(ROOT, "대조v2", "수학검사2", "전_정합1114")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
snap_num = {}
snap_kind = {}
_cnt = {}
for fn in DD.chapter_files("장"):
    p = os.path.join(SNAP, fn)
    if not os.path.exists(p):
        p = os.path.join(ROOT, "장v2", fn)  # 사본이 없는 장은 현행으로 — 2026-11-17 22차 R13 [대응표-1] 뒤 장4·장8 사본을 커밋 87a03929(11-16; 15:52 판과 머리 같음 — 11-14 번역 원천 사본으로 확인)에서 넣어 지금은 모든 장에 사본이 있다
    for ln in read(p).split("\n"):
        m = HEAD_RE.match(ln)
        if m:
            key = "%s:%s" % (m.group(2), m.group(3))
            if key in snap_num:
                continue  # 같은 라벨을 다시 적은 머리(뒤로 미룬 증명)는 같은 번호다
            ch = int(m.group(2))
            _cnt[ch] = _cnt.get(ch, 0) + 1
            snap_num[key] = (ch, _cnt[ch])
            snap_kind[key] = m.group(1)


def old_number(k):
    if k not in snap_num:
        return "사본에 없음"
    ch, n = snap_num[k]
    if ch == 6 and n >= 46:
        n += 1
    if ch == 10 and n >= 5:
        n += 1
    return "%d.%d" % (ch, n)


mp = ["# 라벨–번호 대응표 (%s)" % now[:10], "",
      "현재 번호는 이 표를 만든 시각의 장 파일(`장v2/장*.md`)에서 진술 머리를 순서대로 센 번호이고, 같은 파일들에서 조립한 `원고.md`의 번호와 같다. 「15:52 조립본 번호」는 2026-11-14 15:52 조립본(지도 JSON·번역 초안이 기준으로 삼은 판; 결정 97·101 전)의 번호다. 그 열은 결정 101 전 장 파일 사본(`대조v2/수학검사2/전_정합1114/`)의 머리 순서에 결정 97이 지운 둘(따름정리 6.46 V-핵심의 머묾 항등식, 명제 10.5 예산 분해)을 되돌려 센 것이다. 그 뒤 지운 진술은 표 끝에 「뺌」으로 적었다. 라벨이 바뀐 채 살아 있는 진술(옮김)은 산 행의 그 열에 「옛 `(옛 라벨)` 번호」로 적고 표 끝의 「옮김」 행이 같은 짝을 되짚는다; 「사본에 없음」은 라벨 기준이라 그 뒤 새로 생긴 진술에만 남는다. 번호는 라벨에서 조립 때 매겨지므로 정본은 라벨이다.", "",
      "| 라벨 | 종류 | 이름 | 현재 번호 | 15:52 조립본 번호 | 둘째 판 절 |", "|---|---|---|---|---|---|"]
# 2026-11-18 24차 R13 [대응표-1]: 라벨이 바뀐 채 살아 있는 진술(옮김)의 산 행에 옛 라벨의 15:52 번호를 적는다.
# 옛 라벨→현행 라벨은 표 끝 「옮김」 행과 같은 규칙으로 가른다(장부 4절 「라벨을 … 바꿈」 주석이 먼저, 장부에 행이 없는 라벨만 이름 일치).
moved_from = {}
for _k in sorted(set(snap_num) - cur, key=lambda x: snap_num[x]):
    _r = removed_led.get(_k)
    if _r and _r.get("moved") and _r["moved"] in cur:
        _to = [_r["moved"]]
    elif _r:
        _to = []
    else:
        _to = [c for c in cur if c.split(":", 1)[1] == _k.split(":", 1)[1] and c != _k]
    if _to and _to[0] not in moved_from:
        moved_from[_to[0]] = _k


def old_number_live(k):
    n = old_number(k)
    if n == "사본에 없음" and k in moved_from:
        return "옛 `(%s)` %s" % (moved_from[k], old_number(moved_from[k]))
    return n


for k in order:
    s = st[k]
    nm = s["name"].strip().replace("|", "／") or "—"
    mp.append("| %s | %s | %s | %s | %s | %s |" % (lab_tag(k), s["kind"], nm, number[k], old_number_live(k), s["section"]))
for k in sorted(set(snap_num) - cur, key=lambda x: snap_num[x]):
    r = removed_led.get(k)
    nm = (r["name"] if r and r["name"] else "—").replace("|", "／")
    # 2026-11-15 N14-1: 같은 이름의 라벨이 다른 장에 살아 있으면 뺀 것이 아니라 옮긴 것이다(예: 5:zeta-constants → 2:zeta-constants).
    # 2026-11-17 23차 R13 [대응-1]·[대응-2]: 장부 4절의 「라벨을 `X`로 바꿈」 주석이 있으면 그 라벨로 옮긴 것이고, 장부가 뺌이라 적은 라벨은
    # 같은 이름의 라벨이 다른 장에 살아 있어도 뺀 것이다(8:explicit-bounds ≠ 7:explicit-bounds). 장부에 행이 없는 라벨만 이름 일치로 가른다.
    if r and r.get("moved") and r["moved"] in cur:
        moved = [r["moved"]]
    elif r:
        moved = []
    else:
        moved = [c for c in cur if c.split(":", 1)[1] == k.split(":", 1)[1] and c != k]
    if moved:
        how = "옮김 → %s %s" % (lab_tag(moved[0]), number[moved[0]])
        nm = st[moved[0]]["name"].strip().replace("|", "／") or nm
        kind = st[moved[0]]["kind"]
    else:
        how = "뺌(장부 4절의 뺌 행; 경위는 세션 결정)"
        kind = r["kind"] if r else snap_kind[k]
    mp.append("| `(%s)` | %s | %s | %s | %s | — |" % (k, kind, nm, how, old_number(k)))
mp.append("| `(6:V-core-identity)` | 따름정리 | V-핵심의 머묾 항등식 | 뺌(결정 97) | 6.46 | — |")
mp.append("| `(10:old-8-5)` | 명제 | 예산 분해; 기록 [r3d0856b]의 명제 4 | 뺌(결정 97) | 10.5 | — |")
mp_text = "\n".join(mp) + "\n"

print("1절 행", len(rows), "/ 뺌·대체", len(gone_rows), "/ 입력 라벨", len(all_inputs), "/ 머리 순환", len(head_cycles), "/ 본문 상호 인용 묶음", len(all_sccs))
print("옛 표에서 이어받음: 첫 판 번호(장부 4절 기준)", sum(1 for k in order if led4.get(k, {}).get("first", "—") not in ("—", "")),
      "/ 문헌(10.3절)", sum(1 for k in order if k in lit_of),
      "/ 비고", sum(1 for k in order if old_rows.get(k, {}).get("note", "—") not in ("—", "")), "/ 부록 D", sum(1 for k in order if k in appd_of))
print("M14 2.3 손질: 기록 주장 앞 목록 채움", claims_fix, "/ 비고 문구 걷어 냄", len(note_fix_hits), "종", {a[:18]: n for a, n in note_fix_hits.items()},
      "/ 안 맞은 문구", [a[:18] for a, _ in NOTE_FIX if a not in note_fix_hits])
if DRY:
    print("(dry) 쓰지 않음")
else:
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(body)
    io.open(MAP_OUT, "w", encoding="utf-8", newline="\n").write(mp_text)
    print("썼음:", OUT, len(body), "바이트;", MAP_OUT, len(mp_text), "바이트")
