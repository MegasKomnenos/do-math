# -*- coding: utf-8 -*-
"""11.3절 「공유 입력과 고유 입력」 세 표의 둘째·셋째·넷째 열을 원고에서 생성한다(결정 K5-13).

입력
  장v2/_11_3행.json  — 사람이 정하는 행 정의(정본). {"설명": […], "행": [행…]}; 행마다 {"표": "공유"|"첫째"|"둘째", "이름", "입력": [라벨…],
                       "딸림": [라벨…], "메모", "입력열"} + 선택 {"등급": {라벨: 등급}, "계산제외": [라벨…]}.
  장v2/장*.md        — 진술 머리·진술·증명·인용·식 번호(이 파일 안에서 자족해 파싱한다; dependency_map을 import하지 않는다).
  장v2/부록D_장*.md  — 항목 머리 `### D.{{D:이름}} 제목 (정리 {{N:라벨}}, …)`와 `**산술 등급.**` 줄.

출력(세 표의 마크다운)
  첫째 열 「입력」은 행 정의에서(「입력열」이 있으면 그대로, 없으면 종류 낱말과 라벨로 조립한다).
  「계산 진술과 산술 등급」: 행의 입력 라벨들에서 증명 인용(머리의 의존 괄호·증명 본문·식 번호)을 따라 내려간 의존 폐포 안의 진술 가운데
    부록 D 항목 머리가 확인한다고 든 라벨을 모아 「종류 라벨: 등급」으로 적는다. 폐포가 다른 행의 입력 라벨에 닿으면 거기서 멈춘다(그 계산은 그 행의 몫).
    앞 행에 이미 적힌 진술은 다시 적지 않는다(현행 표의 관행; --no-dedupe로 끈다). 아무것도 없으면 「없음」.
  「…에서 직접 인용하는 자리」: 첫째 증명 쪽은 정리 {{9:old-7-46}}에서 거슬러 닿는 9장 진술과 정리 {{7:old-6-22}}의 증명, 둘째 증명 쪽은
    정리 {{10:old-8-37}}에서 거슬러 닿는 10장 진술의 범위에서, 입력 라벨(또는 그 진술이 세운 식 번호)을 인용하는 자리를 적는다.
    머리의 의존 괄호 안 인용 → 「종류 라벨」, 증명 안(「**증명.**」부터 ∎까지와 뒤로 미룬 증명) 인용 → 「종류 라벨의 증명」,
    정의의 본문 인용 → 「정의 라벨」. 정리 {{7:old-6-22}}는 늘 「정리 {{7:old-6-22}}의 증명」으로, 정리 {{10:old-8-37}}의 증명은
    「N째 고리는 …」 문단마다 「10.7절 N째 고리」로 적는다. 진술 본문(괄호 밖 머리 줄·증명 앞 줄)과 ∎ 뒤 산문, 진술 밖 준비 문단의 인용은
    근거 인용이 아니므로 셀에 넣지 않고 --diff 보고의 진단에만 적는다. 입력이 여럿이면 자리 뒤 괄호에 어느 입력인지 붙인다.
    직접 인용이 없으면 「직접 인용 없음(경유: 라벨들)」 — 경유는 그 증명의 뿌리에서 거슬러 닿는 진술 가운데 입력을 인용하는 것 중 뿌리에 가장 가까운 것들.

명령
  python -I scripts/_gen_11_3표.py --init-rows            현행 장11.md 세 표의 첫째 열에서 행 정의 파일을 처음 뽑는다(있으면 --force 필요)
  python -I scripts/_gen_11_3표.py --out <파일>            생성 표를 파일로
  python -I scripts/_gen_11_3표.py --diff [--diff-out <파일>]   현행 장11.md의 세 표와 행·열 단위로 대조해 차이를 출력
  python -I scripts/_gen_11_3표.py --fill 장v2/장11.md     세 표를 생성 표로 바꿔 넣는다(수리 뒤 U16에서 실행)
  공통 선택지: --base <git 판>(예: HEAD; 장v2 파일을 작업 트리 대신 그 판에서 읽는다), --rows <행 정의 파일>, --no-dedupe
"""
import argparse
import collections
import io
import json
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAP = os.path.join(ROOT, "장v2")
ROWS_DEFAULT = os.path.join(CHAP, "_11_3행.json")

KINDS = ("정의", "정리", "명제", "보조정리", "따름정리")
GRADES = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "배정밀도 평가", "40자리 평가", "30자리 평가"]
LABEL_RE = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
D_LABEL_RE = re.compile(r"\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
DEFER_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}의 증명\.\*\*")
PROOF_RE = re.compile(r"^\*\*증명\.\*\*")
D_HEAD_RE = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}\s*(.*)$")
SECTION_RE = re.compile(r"^### (\d+\.\d+(?:\.\d+)?)")
CHAPTER_RE = re.compile(r"^## (\d+)\.")
TAG_RE = re.compile(r"\\tag\s*\*?\s*\{\s*([^}]+?)\s*\}")
EQ_REF_RE = re.compile(r"\((\d{1,2}\.\d{1,3})\)")
RECORD_REF_RE = re.compile(r"기록\s*\[[^\]]+\][^()\n]*?\(\d{1,2}\.\d{1,3}\)(?:[^()\n]{0,24}\(\d{1,2}\.\d{1,3}\))*")
HEAD_BRACKET_RE = re.compile(r"\[([^\[\]]*(?:\[[^\]]*\][^\[\]]*)*)\]\.\*\*")
ORDINALS = ["첫째", "둘째", "셋째", "넷째", "다섯째", "여섯째", "일곱째", "여덟째", "아홉째", "열째"]
LINK_RE = re.compile(r"^(" + "|".join(ORDINALS) + r") 고리는")
SUB_TRIGGER_RE = re.compile(r"그 증명이 (?:거쳐 )?부르는")
LETTERED_RE = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}((?:\([가-힣a-z]\))+)")

FIRST_ROOT, FIRST_CH, FIRST_EXTRA = "9:old-7-46", 9, "7:old-6-22"
SECOND_ROOT, SECOND_CH = "10:old-8-37", 10
TABLE_TITLES = {"공유": "**공유 입력.**", "첫째": "**첫째 증명의 고유 입력.**", "둘째": "**둘째 증명의 고유 입력.**"}
TABLE_HEADS = {
    "공유": ("| 입력 | 계산 진술과 산술 등급 | 첫째 증명에서 직접 인용하는 자리 | 둘째 증명에서 직접 인용하는 자리 |", "|---|---|---|---|"),
    "첫째": ("| 입력 | 계산 진술과 산술 등급 | 첫째 증명에서 직접 인용하는 자리 |", "|---|---|---|"),
    "둘째": ("| 입력 | 계산 진술과 산술 등급 | 둘째 증명에서 직접 인용하는 자리 |", "|---|---|---|"),
}


# ---------------------------------------------------------------- 파일 읽기(작업 트리 또는 git 판)
class Source:
    def __init__(self, base=None):
        self.base = base
        self._cache = {}

    def names(self, prefix):
        """장v2의 파일 이름(작업 트리 목록; git 판을 읽을 때도 이름은 작업 트리에서 가져오고 내용만 그 판에서 읽는다 —
        한글 경로의 `git ls-tree`가 이 환경에서 빈 출력을 내기 때문)."""
        names = os.listdir(CHAP)
        res = []
        for i in range(1, 12):
            whole = f"{prefix}{i}.md"
            if whole in names:
                res.append(whole)
                continue
            res.extend(sorted(n for n in names if re.fullmatch(rf"{re.escape(prefix)}{i}[A-Z]\.md", n)))
        return res

    def _git_root(self):
        out = subprocess.run(["git", "-C", ROOT, "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8")
        return out.stdout.strip()

    def lines(self, name):
        if name in self._cache:
            return self._cache[name]
        if self.base:
            rel = os.path.relpath(os.path.join(CHAP, name), self._git_root()).replace("\\", "/")
            out = subprocess.run(["git", "-C", ROOT, "show", f"{self.base}:{rel}"], capture_output=True, encoding="utf-8", errors="replace")
            if out.returncode != 0:
                raise SystemExit(f"git show 실패({name}): {out.stderr.strip()}")
            text = out.stdout
        else:
            text = io.open(os.path.join(CHAP, name), encoding="utf-8").read()
        self._cache[name] = text.split("\n")
        return self._cache[name]


# ---------------------------------------------------------------- 원고 파싱
def parse_chapters(src):
    """{라벨: 진술}. 진술 = dict(kind, label, ch, section, file, line(1-based), order, head, lines=[(줄번호, 글, 구역)], defer=[...])
    구역: head(머리 줄) · stmt(증명 앞 진술 줄) · proof(「**증명.**」부터 ∎까지) · tail(∎ 뒤 산문) · def(정의의 본문) · dproof(뒤로 미룬 증명).
    prose: {(파일, 줄번호): (장, 절, 앞 진술 라벨)} — 어느 진술 범위에도 들지 않는 줄(준비 문단)."""
    stmts, prose, defers = {}, {}, []
    order = 0
    for name in src.names("장"):
        L = src.lines(name)
        marks = []  # (i, kind, key)
        ch, sec = 0, ""
        sec_at = {}
        for i, ln in enumerate(L):
            m = CHAPTER_RE.match(ln)
            if m:
                ch = int(m.group(1)); sec = str(ch)
            m = SECTION_RE.match(ln)
            if m:
                sec = m.group(1); marks.append((i, "section", None)); sec_at[i] = sec; continue
            d = DEFER_RE.match(ln)
            if d:
                marks.append((i, "defer", f"{d.group(2)}:{d.group(3)}")); continue
            h = HEAD_RE.match(ln)
            if h:
                marks.append((i, "head", f"{h.group(2)}:{h.group(3)}"))
        covered = set()
        cur_sec = str(ch)
        sec_of_line = {}
        for i, ln in enumerate(L):
            if i in sec_at:
                cur_sec = sec_at[i]
            sec_of_line[i] = cur_sec
        for j, (i, kind, key) in enumerate(marks):
            if kind == "section":
                continue
            end = len(L)
            for (i2, k2, _) in marks[j + 1:]:
                if k2 in ("head", "defer", "section"):
                    end = i2; break
            block = L[i:end]
            if kind == "defer":
                # 머리 줄부터 첫 ∎까지(머리 줄에 ∎가 있으면 한 줄)
                lines = []
                for t in range(i, end):
                    lines.append((t + 1, L[t], "dproof"))
                    if "∎" in L[t]:
                        break
                defers.append((key, name, lines))
                covered.update(range(i, i + len(lines)))
                continue
            order += 1
            hm = HEAD_RE.match(L[i])
            lines = [(i + 1, L[i], "head")]
            if hm.group(1) == "정의":
                # 정의의 본문은 머리 줄뿐이다. 뒤 문단(뜻풀이·준비 문단)은 어느 진술에도 들지 않는 산문으로 돌린다(현행 표가 정의 10.1의 머리 줄 인용만 자리로 든다).
                stmts[key] = dict(kind="정의", label=key, ch=int(hm.group(2)), section=sec_of_line[i], file=name, line=i + 1,
                                  order=order, head=L[i], lines=lines, defer=[])
                covered.add(i)
                continue
            zone = "stmt"
            qed = False
            for t in range(i + 1, end):
                ln = L[t]
                if zone != "def" and not qed and PROOF_RE.match(ln):
                    zone = "proof"
                if zone == "proof" and qed:
                    zone = "tail"
                lines.append((t + 1, ln, zone))
                if zone == "proof" and "∎" in ln:
                    qed = True
            # 증명 표지 없이 ∎로 끝나는 진술(증명을 본문에 바로 적은 꼴): 머리 다음부터 ∎까지를 증명으로 본다
            if zone == "stmt" and any("∎" in ln for _, ln, _ in lines[1:]):
                new, done = [], False
                for (n, ln, z) in lines[1:]:
                    new.append((n, ln, "tail" if done else "proof"))
                    if "∎" in ln:
                        done = True
                lines = lines[:1] + new
            # 범위 안 줄 가운데 ∎ 없이 끝났고 다음이 절 머리면 tail은 없다
            stmts[key] = dict(kind=hm.group(1), label=key, ch=int(hm.group(2)), section=sec_of_line[i], file=name, line=i + 1,
                              order=order, head=L[i], lines=lines, defer=[])
            covered.update(range(i, end))
        for i, ln in enumerate(L):
            if i not in covered and not SECTION_RE.match(ln) and not CHAPTER_RE.match(ln) and ln.strip():
                prev = None
                for (i2, k2, key2) in marks:
                    if k2 == "head" and i2 < i:
                        prev = key2
                    if i2 > i:
                        break
                prose[(name, i + 1)] = (ch, sec_of_line[i], prev, ln)
    for key, name, lines in defers:
        if key not in stmts:
            print(f"[경고] 미룬 증명의 진술이 없음: {key} ({name}:{lines[0][0]})")
            continue
        v = stmts[key]
        if not any(z == "proof" for _, _, z in v["lines"]):
            # 증명을 뒤로 미룬 진술의 머리 뒤 줄은 증명 개요다(9.35의 「증명이 이 절 밖에서 끌어오는 것은 …」). 머리도 증명도 아니므로 자리로 적지 않고 진단에만 둔다
            v["lines"] = [(n, ln, "overview" if z == "stmt" else z) for n, ln, z in v["lines"]]
        v["lines"].extend(lines)
        v["defer"].append(f"{name}:{lines[0][0]}")
    return stmts, prose


def equation_owners(stmts, src):
    """식 태그 → 소속 진술 라벨(태그 줄이 진술 범위 안에 있을 때)."""
    out = {}
    by_file = collections.defaultdict(list)
    for v in stmts.values():
        rng = [n for n, _, z in v["lines"] if z != "dproof"]
        by_file[v["file"]].append((min(rng), max(rng), v["label"]))
    for name in src.names("장"):
        for n, ln in enumerate(src.lines(name), 1):
            for tag in TAG_RE.findall(ln):
                owner = next((lab for a, b, lab in by_file[name] if a <= n <= b), None)
                out[tag] = (owner, name, n)
    return out


def head_bracket_labels(head):
    m = HEAD_BRACKET_RE.search(head)
    if not m:
        return set(), head
    return {f"{a}:{b}" for a, b in LABEL_RE.findall(m.group(1))}, head[m.end():]


def citations(v, eq_owner):
    """진술 v가 인용하는 {라벨: {"zones": set, "lines": [...], "eq": set}}.
    zones ⊂ {bracket, stmt, proof, dproof, tail, def}. 식 번호 인용은 그 식의 소속 진술에 귀속시키고 zone은 식 번호가 놓인 구역."""
    out = collections.defaultdict(lambda: {"zones": set(), "lines": [], "eq": set()})
    br, rest = head_bracket_labels(v["head"])
    for a in br:
        if a != v["label"]:
            out[a]["zones"].add("bracket"); out[a]["lines"].append(v["line"])
    for a, b in LABEL_RE.findall(rest):
        lab = f"{a}:{b}"
        if lab != v["label"] and lab not in br:
            out[lab]["zones"].add("def" if v["kind"] == "정의" else "stmt"); out[lab]["lines"].append(v["line"])
    for n, ln, zone in v["lines"][1:]:
        for a, b in LABEL_RE.findall(ln):
            lab = f"{a}:{b}"
            if lab == v["label"]:
                continue
            out[lab]["zones"].add(zone); out[lab]["lines"].append(n)
    for n, ln, zone in v["lines"]:
        for tag in EQ_REF_RE.findall(RECORD_REF_RE.sub(lambda m: " " * len(m.group(0)), ln)):
            owner = (eq_owner.get(tag) or (None,))[0]
            if owner and owner != v["label"]:
                z = zone if zone != "head" else "stmt"
                out[owner]["zones"].add(z); out[owner]["lines"].append(n); out[owner]["eq"].add(tag)
    return out


GROUND = {"bracket", "proof", "dproof"}


def build_graph(stmts, eq_owner):
    """근거 인용(머리 괄호·증명 본문·식 번호)의 의존 간선 {라벨: {인용 라벨: 정보}}. 정의는 결과가 아니라 언어이므로 간선의 도착점에서 뺀다.
    앞선 언급(뒤 진술의 인용)은 괄호 안이거나 미룬 증명 안일 때만 의존으로 센다."""
    cites, deps = {}, {}
    for lab, v in stmts.items():
        c = citations(v, eq_owner)
        cites[lab] = c
        d = {}
        for a, info in c.items():
            if a not in stmts or stmts[a]["kind"] == "정의":
                continue
            if not (info["zones"] & GROUND):
                continue
            forward = stmts[a]["order"] > v["order"]
            if forward and not (info["zones"] & {"bracket", "dproof"}) and not v["defer"]:
                continue
            d[a] = info
        deps[lab] = d
    return cites, deps


def reach(deps, root):
    """뿌리에서 거슬러 닿는 진술과 깊이 {라벨: 깊이}(너비 우선)."""
    depth = {root: 0}
    q = collections.deque([root])
    while q:
        x = q.popleft()
        for y in deps.get(x, {}):
            if y not in depth:
                depth[y] = depth[x] + 1; q.append(y)
    return depth


# ---------------------------------------------------------------- 부록 D
def grades_in(text):
    """**산술 등급.** 줄에서 등급 이름을 뽑는다. 「기록의 계산은 …」처럼 기록 쪽 산술을 적은 문장은 등급으로 읽지 않는다
    (_gen_11_2표.py는 첫 「. 기록의 」에서 자르지만, 그 뒤에 (ㄴ) 같은 이 글의 등급이 이어지는 항목이 있어 문장 단위로 거른다)."""
    text = text.replace("**산술 등급.**", "")
    sents = re.split(r"(?<=다)\.\s+|(?<=\))\.\s+", text)
    out = []
    for sent in sents:
        if re.match(r"^\s*(?:\([ㄱ-ㅎ]\)의\s*)?기록(?:의)?\s*계산", sent):
            continue
        for g in GRADES:
            if g in sent and g not in out:
                out.append(g)
    return out


def parse_appendix_d(src):
    """[{name, order, head_labels, verify_labels, grades, file, line}] (파일·등장 순)."""
    items = []
    for name in src.names("부록D_장"):
        cur = None
        for n, ln in enumerate(src.lines(name), 1):
            m = D_HEAD_RE.match(ln)
            if m:
                letters = {f"{a}:{b}": set(re.findall(r"\(([가-힣a-z])\)", ls)) for a, b, ls in LETTERED_RE.findall(m.group(2))}
                cur = dict(name=m.group(1), order=len(items) + 1, head_labels=[f"{a}:{b}" for a, b in LABEL_RE.findall(m.group(2))],
                           head_letters=letters, verify_labels=[], grades=[], file=name, line=n)
                items.append(cur); continue
            if cur and ln.startswith("**확인하는 진술.**"):
                cur["verify_labels"] = [f"{a}:{b}" for a, b in LABEL_RE.findall(ln)]
            if cur and ln.startswith("**산술 등급.**"):
                cur["grades"] = grades_in(ln)
    return items


def grade_map(items):
    """라벨 → [(항목 이름, 등급 목록, 머리의 항목 글자 집합)](항목 머리가 확인하는 진술로 든 라벨; 항목 순)."""
    g = collections.OrderedDict()
    for it in items:
        for lab in it["head_labels"]:
            g.setdefault(lab, []).append((it["name"], list(it["grades"]), it["head_letters"].get(lab, set())))
    return g


def head_grades(v):
    """진술 머리의 표지에서 「계산 증거(등급)」·「계산 보조(등급, 등급)」의 등급 이름을 뽑는다(1.5절의 표지 규칙). 없으면 빈 목록."""
    m = HEAD_BRACKET_RE.search(v["head"])
    if not m:
        return []
    out = []
    for g in re.finditer(r"계산 (?:증거|보조)\(([^()]*)\)", m.group(1)):
        inner = g.group(1)
        for x in sorted((x for x in GRADES if x in inner), key=inner.index):   # 머리에 적힌 차례대로
            if x not in out:
                out.append(x)
    return out


def grades_for(lab, gmap, stmts, row_letters=None, override=None):
    """라벨의 등급 목록. 차례: 행 정의의 「등급」 덧씌우기 → 진술 머리 표지의 「계산 증거/보조(…)」 괄호(진술 하나의 등급을 바로 적은 자리) →
    부록 D 항목의 「산술 등급」 줄(항목 하나가 여러 진술을 확인하면 등급이 섞인다). 행 정의가 그 라벨에 항목 글자를 적었고(「정리 {{X}}(가)」)
    부록 D 머리도 글자를 적었는데 겹치지 않으면(「(나)」) 그 항목은 이 행의 계산이 아니다."""
    if override and lab in override:
        return [override[lab]]
    items = [(name, grades, letters) for name, grades, letters in gmap.get(lab, []) if not (row_letters and letters and not (row_letters & letters))]
    if not items:
        return []
    hg = head_grades(stmts[lab]) if lab in stmts else []
    if hg:
        return hg
    out = []
    for name, grades, letters in items:
        for x in grades:
            if x not in out:
                out.append(x)
    return out


# ---------------------------------------------------------------- 행 정의
def _split_cells(line):
    """표 줄을 칸으로 가른다(수식 안의 \\vert 는 건드리지 않는다; 칸 경계는 ` | `)."""
    s = line.strip()
    assert s.startswith("|") and s.endswith("|"), line
    return [c.strip() for c in s[1:-1].split(" | ")]


def read_current_tables(src):
    """현행 장11.md 11.3절의 세 표 → {표: [행 칸 목록]}과 각 표의 (시작 줄, 끝 줄)(1-based, 머리 줄 포함)."""
    L = src.lines("장11.md")
    i0 = next(i for i, ln in enumerate(L) if ln.startswith("### 11.3"))
    i1 = next(i for i, ln in enumerate(L) if i > i0 and ln.startswith("### 11.4"))
    tables, spans, cur = {}, {}, None
    for i in range(i0, i1):
        ln = L[i]
        for k, title in TABLE_TITLES.items():
            if ln.startswith(title):
                cur = k; tables[cur] = []; spans[cur] = [None, None]
        if cur and ln.startswith("|"):
            if spans[cur][0] is None:
                spans[cur][0] = i + 1
            spans[cur][1] = i + 1
            if ln.startswith("|---") or ln.startswith("| 입력 |"):
                continue
            tables[cur].append(_split_cells(ln))
    return tables, spans


def split_name(first_cell):
    """첫째 열을 (행 이름, 입력열)로 가른다 — 수식·라벨 밖의 첫 「: 」에서."""
    depth_math = False
    i = 0
    while i < len(first_cell) - 1:
        ch = first_cell[i]
        if ch == "$":
            depth_math = not depth_math
        elif not depth_math and first_cell.startswith("{{", i):
            i = first_cell.index("}}", i) + 2; continue
        elif not depth_math and first_cell.startswith(": ", i):
            return first_cell[:i].strip(), first_cell[i + 2:].strip()
        i += 1
    return first_cell.strip(), ""


def memo_of(inp_text):
    """입력열에서 라벨·종류 낱말·구분 부호를 걷어 낸 산문."""
    s = LABEL_RE.sub(" ", inp_text)
    s = re.sub(r"(정의|정리|명제|보조정리|따름정리)", " ", s)
    s = re.sub(r"[·,;]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


ROWS_DOC = [
    "11.3절 세 표의 행 정의(사람이 고치는 정본; 결정 K5-13). scripts/_gen_11_3표.py가 읽어 세 표의 나머지 열을 생성한다.",
    "행마다: 「표」 공유|첫째|둘째, 「이름」 첫째 열의 행 이름(콜론 앞), 「입력」 행의 입력 라벨(순서 보존), 「딸림」 입력의 증명이 거쳐 부르는 라벨(「…과 그 증명이 (거쳐) 부르는」 뒤; 계산 폐포의 출발점이 되고 다른 행의 멈춤점이 되지만 인용 자리는 적지 않는다), 「메모」 첫째 열의 라벨 밖 산문, 「입력열」 첫째 열의 콜론 뒤 글(있으면 그대로 첫째 열에 쓴다).",
    "선택: 「등급」 {라벨: 등급 글} — 부록 D 항목 하나가 여러 진술·여러 등급을 적어 기계가 진술별 등급을 가르지 못할 때 사람이 정한 값; 「계산제외」 [라벨…] — 이 행의 계산 열에서 뺄 진술(다른 행의 몫으로 돌릴 때).",
    "처음 만들 때: python -I scripts/_gen_11_3표.py --init-rows [--base HEAD]. 그 뒤로는 손으로 고친다.",
]


def init_rows(src, path, force=False):
    if os.path.exists(path) and not force:
        raise SystemExit(f"행 정의 파일이 이미 있다(--force로 덮어쓴다): {path}")
    tables, _ = read_current_tables(src)
    rows = []
    for t in ("공유", "첫째", "둘째"):
        for cells in tables.get(t, []):
            name, inp = split_name(cells[0])
            labs = [f"{a}:{b}" for a, b in LABEL_RE.findall(inp)]
            # 「…과 그 증명이 (거쳐) 부르는」 뒤의 라벨은 딸림이다. 다만 그 뒤에 적혔어도 인용자 열이 직접 인용 자리로 드는 라벨은 행의 입력이다
            # (「첫째/둘째 증명만 부르는 앞 장의 진술」 행이 딸림 묶음 뒤에 입력을 이어 적는다; dependency_map/scripts/지도/파생.py read_11_3과 같은 규칙).
            m = SUB_TRIGGER_RE.search(inp)
            if m:
                cited = {f"{a}:{b}" for c in cells[2:] for a, b in LABEL_RE.findall(NO_DIRECT_SUBJECT_RE.sub(" ", c))}
                before = [f"{a}:{b}" for a, b in LABEL_RE.findall(inp[:m.start()])]
                after = [f"{a}:{b}" for a, b in LABEL_RE.findall(inp[m.end():])]
                main = before + [x for x in after if x in cited]
                sub = [x for x in after if x not in cited]
            else:
                main, sub = labs, []
            rows.append({"표": t, "이름": name, "입력": main, "딸림": sub, "메모": memo_of(inp), "입력열": inp})
    doc = {"설명": ROWS_DOC, "행": rows}
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(f"행 정의 {len(rows)}행 → {path}")


def load_rows(path):
    doc = json.load(io.open(path, encoding="utf-8"))
    rows = doc["행"] if isinstance(doc, dict) else doc
    for r in rows:
        assert r["표"] in TABLE_TITLES, r
        assert isinstance(r["입력"], list) and r["입력"], r
    return rows


# ---------------------------------------------------------------- 생성
def kind_label_list(labels, stmts, with_kind=True):
    """「정리 {{a}}·{{b}}, 보조정리 {{c}}」 — 같은 종류가 이어지면 가운뎃점으로 묶는다(주어진 순서 보존)."""
    out, prev = [], None
    for lab in labels:
        k = stmts[lab]["kind"] if lab in stmts else "?"
        if with_kind and k != prev:
            out.append((", " if out else "") + f"{k} {{{{{lab}}}}}")
        else:
            out.append(("·" if out else "") + f"{{{{{lab}}}}}")
        prev = k
    return "".join(out)


def gen_calc_cell(row, all_inputs, stmts, deps, gmap, seen, dedupe=True):
    """의존 폐포(다른 행의 입력에서 멈춤) 안의 부록 D 확인 진술을 「종류 라벨: 등급」으로. (셀 글, 적은 라벨들, 폐포)"""
    own = set(row["입력"]) | set(row.get("딸림", []))
    stop = all_inputs - own
    closure, stack = set(), [l for l in row["입력"] + row.get("딸림", []) if l in stmts]
    while stack:
        x = stack.pop()
        if x in closure:
            continue
        closure.add(x)
        for y in deps.get(x, {}):
            if y in stop or y in closure:
                continue
            stack.append(y)
    row_letters = {f"{a}:{b}": set(re.findall(r"\(([가-힣a-z])\)", ls)) for a, b, ls in LETTERED_RE.findall(row.get("입력열", ""))}
    exclude = set(row.get("계산제외", []))
    grades = {}
    for l in closure:
        if l in gmap and l not in exclude:
            g = grades_for(l, gmap, stmts, row_letters.get(l), row.get("등급"))
            if g:
                grades[l] = g
    cands = sorted(grades, key=lambda l: stmts[l]["order"])
    if dedupe:
        cands = [l for l in cands if l not in seen]
    groups = collections.OrderedDict()
    for l in cands:
        groups.setdefault(tuple(grades[l]), []).append(l)
    parts = [f"{kind_label_list(ls, stmts)}: {', '.join(g)}" for g, ls in groups.items()]
    return ("; ".join(parts) if parts else "없음"), cands, closure


def prep_places(stmts, prose, chapter):
    """--prep: 절 안 준비 문단이 라벨을 인용하면 「N.m절 준비 문단(종류 {{앞 진술}} 뒤)」을 자리로 더한다. 준비 문단은 둘이다 —
    어느 진술 범위에도 들지 않는 산문(정의 뒤 문단 포함)과, 진술의 ∎ 뒤에 이어지는 산문(현행 표의 「정리 X 뒤의 준비 문단」). 장 머리말은 언급으로 보아 넣지 않는다."""
    places = collections.defaultdict(list)

    def add(lab, prev, sec):
        text = f"{sec}절 준비 문단({stmts[prev]['kind']} {{{{{prev}}}}} 뒤)"
        key = (0, -stmts[prev]["order"], 99)
        if (key, text, prev) not in places[lab]:
            places[lab].append((key, text, prev))

    for (fname, n), (ch, sec, prev, ln) in prose.items():
        if ch != chapter or prev is None:
            continue
        for a, b in LABEL_RE.findall(ln):
            add(f"{a}:{b}", prev, sec)
    for s, v in stmts.items():
        if v["ch"] != chapter:
            continue
        for n, ln, zone in v["lines"]:
            if zone == "tail":
                for a, b in LABEL_RE.findall(ln):
                    if f"{a}:{b}" != s:
                        add(f"{a}:{b}", s, v["section"])
    return places


def proof_places(stmts, cites, deps, root, chapter, extra=None):
    """증명 쪽 범위(뿌리에서 닿는 chapter 장의 진술 + extra의 증명)에서 「입력 라벨 → [(정렬 키, 자리 글, 인용 진술)]」와 진단을 모은다."""
    depth = reach(deps, root)
    scope = [l for l in depth if stmts[l]["ch"] == chapter]
    # 정의는 의존 간선의 도착점이 아니라 닿음으로 걸러지지 않으므로 그 장의 정의는 모두 범위에 둔다(정의의 머리 줄 인용은 자리다 — 현행 표의 정의 10.1)
    for a, v in stmts.items():
        if v["kind"] == "정의" and v["ch"] == chapter and a not in scope:
            scope.append(a)
    if extra and extra in stmts:
        scope.append(extra)
    places = collections.defaultdict(list)   # 입력 라벨 → [(키, 글, 인용자)]
    diag = collections.defaultdict(list)     # 입력 라벨 → [(종류, 인용자, 줄들)] — 셀에 넣지 않는 인용(진술 본문·뒤 산문)
    for s in scope:
        v = stmts[s]
        for lab, info in cites[s].items():
            z = info["zones"]
            key = (0 if v["ch"] == chapter else 1, -v["order"])
            if s == extra:
                if z & GROUND or z & {"stmt"}:
                    places[lab].append((key, f"정리 {{{{{s}}}}}의 증명", s))
                continue
            if s == root and chapter == SECOND_CH and (z & GROUND):
                # 10.7절 고리: 증명 문단 「N째 고리는 …」마다
                links = set()
                for n, ln, zone in v["lines"]:
                    if zone == "proof" and (f"{{{{{lab}}}}}" in ln or any(f"({t})" in ln for t in info["eq"])):
                        m = LINK_RE.match(ln)
                        if m:
                            links.add(ORDINALS.index(m.group(1)))
                if links:
                    for i in sorted(links):
                        places[lab].append(((key[0], key[1], i), f"{v['section']}절 {ORDINALS[i]} 고리", s))
                    continue
            if z & {"bracket", "stmt"}:
                places[lab].append((key, f"{v['kind']} {{{{{s}}}}}", s))
            elif v["kind"] == "정의" and "def" in z:
                places[lab].append((key, f"정의 {{{{{s}}}}}", s))
            elif z & {"proof", "dproof"}:
                places[lab].append((key, f"{v['kind']} {{{{{s}}}}}의 증명", s))
            else:
                diag[lab].append(("증명 개요" if "overview" in z else "∎ 뒤 산문", s, sorted(set(info["lines"]))))
    return places, diag, depth


def via_candidates(lab, depth, cites, stmts, all_inputs=()):
    """뿌리에서 닿는 진술 가운데 입력 lab을 근거로 인용하는 것 중 뿌리에 가장 가까운 것들.
    그 가운데 세 표의 행 입력인 진술이 있으면 그것들만 든다(독자가 표 안에서 따라갈 수 있게; 없으면 모든 후보 가운데 가장 가까운 것들)."""
    cands = []
    for s, d in depth.items():
        if s == lab:
            continue
        info = cites[s].get(lab)
        if info and (info["zones"] & GROUND):
            cands.append((d, s))
    pref = [c for c in cands if c[1] in all_inputs]
    pool = pref or cands
    if not pool:
        return []
    best = min(d for d, _ in pool)
    return sorted((s for d, s in pool if d == best), key=lambda s: stmts[s]["order"])


def merge_links(texts):
    """「10.7절 넷째 고리」·「10.7절 다섯째 고리」를 「10.7절 넷째 고리·다섯째 고리」로 묶는다."""
    out, prev_sec = [], None
    for t in texts:
        m = re.match(r"^(\d+\.\d+)절 (\S+ 고리)$", t)
        if m and prev_sec == m.group(1):
            out[-1] += "·" + m.group(2)
        else:
            out.append(t)
        prev_sec = m.group(1) if m else None
    return out


def gen_cite_cell(row, places, diag, depth, cites, stmts, all_inputs=()):
    inputs = [l for l in row["입력"] if l in stmts]
    n = len(inputs)
    by_place = collections.OrderedDict()   # (키, 글) → 인용하는 입력들
    for lab in inputs:
        for key, text, s in places.get(lab, []):
            by_place.setdefault((key, text), []).append(lab)
    # 입력 집합이 같은 자리끼리 묶는다(입력 순 → 자리 순)
    groups = collections.OrderedDict()
    for (key, text), labs in sorted(by_place.items(), key=lambda kv: kv[0][0]):
        groups.setdefault(tuple(labs), []).append(text)
    parts = []
    for labs, texts in sorted(groups.items(), key=lambda kv: tuple(inputs.index(l) for l in kv[0])):
        body = ("·" if n > 1 else ", ").join(merge_links(texts))
        if n > 1:
            tag = {2: "둘 다", 3: "셋 다"}.get(n, "모두") if len(labs) == n else kind_label_list(list(labs), stmts)
            body += f"({tag})"
        parts.append(body)
    missing = [l for l in inputs if not any(l in labs for labs in groups)]
    extra = []
    by_via = collections.OrderedDict()
    for l in missing:
        by_via.setdefault(tuple(via_candidates(l, depth, cites, stmts, all_inputs)), []).append(l)
    for via, labs in by_via.items():
        via_text = kind_label_list(list(via), stmts) if via else "없음"
        if len(labs) == n:
            extra.append(f"직접 인용 없음(경유: {via_text})")
        else:
            subj = "·".join(f"{stmts[l]['kind']} {{{{{l}}}}}" for l in labs)
            extra.append(f"{subj}은 직접 인용 없음(경유: {via_text})")
    cell = ", ".join(parts)
    if extra:
        cell = (cell + "; " if cell else "") + ", ".join(extra)
    return cell, missing


def build(src, rows, dedupe=True, prep=False):
    stmts, prose = parse_chapters(src)
    eq_owner = equation_owners(stmts, src)
    cites, deps = build_graph(stmts, eq_owner)
    items = parse_appendix_d(src)
    gmap = grade_map(items)
    all_inputs = {l for r in rows for l in r["입력"] + r.get("딸림", [])}
    unknown = sorted(l for l in all_inputs if l not in stmts)
    for r in rows:
        r.setdefault("딸림", [])
    first = proof_places(stmts, cites, deps, FIRST_ROOT, FIRST_CH, FIRST_EXTRA)
    second = proof_places(stmts, cites, deps, SECOND_ROOT, SECOND_CH)
    if prep:
        for side, ch in ((first, FIRST_CH), (second, SECOND_CH)):
            for lab, lst in prep_places(stmts, prose, ch).items():
                side[0][lab].extend(lst)
    seen = set()
    gen = []   # [{"표", "행", "셀": [...], "진단": {...}}]
    for r in rows:
        calc, used, closure = gen_calc_cell(r, all_inputs, stmts, deps, gmap, seen, dedupe)
        seen.update(used)
        first_cell = f"{r['이름']}: " + (r.get("입력열") or kind_label_list(r["입력"] + r.get("딸림", []), stmts))
        cells = [first_cell, calc]
        d = {"폐포": sorted(closure, key=lambda l: stmts[l]["order"]), "진술본문인용": {}, "준비문단": {}}
        for side in (("첫째", first), ("둘째", second)):
            if r["표"] in ("공유", side[0]):
                c, miss = gen_cite_cell(r, side[1][0], side[1][1], side[1][2], cites, stmts, all_inputs)
                cells.append(c)
                d["진술본문인용"][side[0]] = {l: side[1][1].get(l, []) for l in r["입력"] if side[1][1].get(l)}
                d.setdefault("직접인용없음", {})[side[0]] = miss
        # 준비 문단(진술 밖 산문)의 인용 — 9장·10장
        for (fname, n), (ch, sec, prev, ln) in prose.items():
            if ch not in (FIRST_CH, SECOND_CH):
                continue
            hit = [l for l in r["입력"] if f"{{{{{l}}}}}" in ln]
            if hit:
                d["준비문단"].setdefault("첫째" if ch == FIRST_CH else "둘째", []).append((sec, prev, n, hit))
        gen.append({"표": r["표"], "행": r, "셀": cells, "진단": d})
    return dict(stmts=stmts, prose=prose, cites=cites, deps=deps, items=items, gmap=gmap, gen=gen, unknown=unknown,
                first_depth=first[2], second_depth=second[2])


def tables_markdown(gen):
    out = []
    for t in ("공유", "첫째", "둘째"):
        out.append(TABLE_TITLES[t]); out.append("")
        out.extend(TABLE_HEADS[t])
        for g in gen:
            if g["표"] == t:
                out.append("| " + " | ".join(cell_safe(c) for c in g["셀"]) + " |")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def cell_safe(s):
    return re.sub(r"\$[^$]*\$", lambda m: m.group().replace("|", r"\vert "), s)


# ---------------------------------------------------------------- 대조
def _outside_parens(text):
    out, depth = [], 0
    for ch in text:
        if ch == "(":
            depth += 1; continue
        if ch == ")":
            depth = max(0, depth - 1); continue
        if depth == 0:
            out.append(ch)
    return "".join(out)


def _split_top(text, seps):
    out, buf, depth = [], [], 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch in seps and depth == 0:
            out.append("".join(buf)); buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return [s.strip() for s in out if s.strip()]


def parse_calc_cell(text):
    """「종류 {{a}}·{{b}}: 등급, 등급; …」 → {라벨: 등급 글}(괄호 안 라벨은 뺀다)."""
    out = {}
    if text.strip() == "없음":
        return out
    for part in _split_top(text, ";"):
        if ":" not in _outside_parens(part):
            continue
        # 마지막 괄호 밖 「: 」에서 가른다
        depth, cut = 0, None
        for i, ch in enumerate(part):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == ":" and depth == 0:
                cut = i
        names, grade = part[:cut], re.sub(r"\s+", " ", _outside_parens(part[cut + 1:])).strip()
        for a, b in LABEL_RE.findall(_outside_parens(names)):
            out[f"{a}:{b}"] = grade
    return out


NO_DIRECT_RE = re.compile(r"직접 인용 없음(\((?:[^()]|\([^()]*\))*\))?")
_KIND = r"(?:정리|명제|보조정리|따름정리|정의)"
_LAB = r"\{\{\d+:[A-Za-z][A-Za-z0-9\-]*\}\}(?:\([가-힣a-z]\))?"
# 「X·Y은 직접 인용 없음(…)」 — 주어 라벨과 괄호째 지운다(파생.py와 같은 규칙)
NO_DIRECT_SUBJECT_RE = re.compile(r"(?:(?:%s\s*)?%s(?:[·,]\s*)?)*[은는이가]?\s*직접 인용 없음(?:\((?:[^()]|\([^()]*\))*\))?" % (_KIND, _LAB))


def parse_cite_cell(text, inputs):
    """인용 셀 → (직접 인용 자리 집합, 경유 라벨 집합, 직접 인용 없다고 적힌 입력 집합).
    자리: 라벨(입력 밖) 또는 「N째 고리」 글자. 「…의 증명」 구별은 자리 글에 「의 증명」을 덧붙여 표시한다."""
    places, via, nodirect = set(), set(), set()
    rest = text
    for m in NO_DIRECT_RE.finditer(text):
        inside = m.group(1) or ""
        via.update(f"{a}:{b}" for a, b in LABEL_RE.findall(inside))
        # 주어(앞의 라벨들)
        head = text[:m.start()]
        seg = re.split(r"[;,]", head)[-1]
        subj = {f"{a}:{b}" for a, b in LABEL_RE.findall(seg)} & set(inputs)
        nodirect.update(subj if subj else (set(inputs) if len(inputs) == 1 or not head.strip() else set()))
    rest = NO_DIRECT_RE.sub(" ", text)
    rest = re.sub(r"(?:정의|정리|명제|보조정리|따름정리)?\s*\{\{\d+:[A-Za-z][A-Za-z0-9\-]*\}\}\s*(?:앞|뒤)(?:의|에서)", " ", rest)   # 준비 문단의 닻
    # 주어 라벨 걷기: 「종류 {{입력}}은 직접 인용 없음」의 주어가 남아 있으면 자리에서 빼야 하므로 입력 라벨은 자리에서 제외한다
    for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리)?\s*\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(의 증명)?", _outside_parens(rest)):
        lab = f"{m.group(2)}:{m.group(3)}"
        if lab in inputs:
            continue
        places.add(lab + ("의 증명" if m.group(4) else ""))
    for m in re.finditer(r"(\d+\.\d+)절 ((?:\S+ 고리(?:·)?)+)", _outside_parens(rest)):
        for o in re.findall(r"(\S+) 고리", m.group(2)):
            places.add(f"{m.group(1)}절 {o} 고리")
    if "준비 문단" in rest:
        places.add("준비 문단")
    return places, via, nodirect


def diff_report(res, cur_tables, rows):
    lines, stats = [], collections.defaultdict(lambda: collections.Counter())
    cur_by_table = {t: list(v) for t, v in cur_tables.items()}
    for g in res["gen"]:
        t, r = g["표"], g["행"]
        cur = next((c for c in cur_by_table.get(t, []) if split_name(c[0])[0] == r["이름"]), None)
        lines.append(f"### [{t}] {r['이름']}")
        lines.append("")
        lines.append(f"- 입력: {', '.join(r['입력'])}" + (f"; 딸림: {', '.join(r['딸림'])}" if r.get("딸림") else ""))
        if cur is None:
            lines.append("- 현행 표에 같은 이름의 행이 없다.")
            lines.append(""); continue
        cols = ["계산 진술과 산술 등급"] + (["첫째 증명에서 직접 인용하는 자리", "둘째 증명에서 직접 인용하는 자리"] if t == "공유" else [f"{t} 증명에서 직접 인용하는 자리"])
        for ci, col in enumerate(cols, 1):
            cur_c, gen_c = cur[ci], g["셀"][ci]
            if cur_c == gen_c:
                lines.append(f"- **{col}**: 일치(글자까지).")
                stats[col]["일치"] += 1; continue
            if ci == 1:
                a, b = parse_calc_cell(cur_c), parse_calc_cell(gen_c)
                if a == b:
                    lines.append(f"- **{col}**: 일치(라벨·등급; 글자 순서만 다름).")
                    stats[col]["일치(순서)"] += 1
                else:
                    stats[col]["불일치"] += 1
                    lines.append(f"- **{col}**: 불일치.")
                    only_cur = sorted(set(a) - set(b)); only_gen = sorted(set(b) - set(a))
                    both_diff = sorted(l for l in set(a) & set(b) if a[l] != b[l])
                    if only_cur:
                        lines.append(f"    - 현행에만: {', '.join(f'{l}({a[l]})' for l in only_cur)}")
                    if only_gen:
                        lines.append(f"    - 생성에만: {', '.join(f'{l}({b[l]})' for l in only_gen)}")
                    if both_diff:
                        lines.append(f"    - 등급 다름: {', '.join(f'{l}: 현행 {a[l]} / 생성 {b[l]}' for l in both_diff)}")
            else:
                ins = r["입력"] + r.get("딸림", [])
                a = parse_cite_cell(cur_c, ins); b = parse_cite_cell(gen_c, ins)
                strip = lambda S: {x.replace("의 증명", "") for x in S}
                if a[0] == b[0] and a[2] == b[2]:
                    lines.append(f"- **{col}**: 일치(자리 집합; 글자·경유 설명만 다름).")
                    stats[col]["일치(순서)"] += 1
                elif strip(a[0]) == strip(b[0]) and a[2] == b[2]:
                    lines.append(f"- **{col}**: 일치(인용 진술 집합; 「…의 증명」 표기만 다름 — 현행에만 「의 증명」: {', '.join(sorted(a[0] - b[0])) or '없음'}; 생성에만 「의 증명」: {', '.join(sorted(b[0] - a[0])) or '없음'}).")
                    stats[col]["일치(표기)"] += 1
                else:
                    stats[col]["불일치"] += 1
                    lines.append(f"- **{col}**: 불일치.")
                    if a[0] - b[0]:
                        lines.append(f"    - 현행에만 있는 자리: {', '.join(sorted(a[0] - b[0]))}")
                    if b[0] - a[0]:
                        lines.append(f"    - 생성에만 있는 자리: {', '.join(sorted(b[0] - a[0]))}")
                    if a[2] != b[2]:
                        lines.append(f"    - 「직접 인용 없음」 입력: 현행 {sorted(a[2]) or '없음'} / 생성 {sorted(b[2]) or '없음'}")
                lines.append(f"    - 현행: {cur_c}")
                lines.append(f"    - 생성: {gen_c}")
            if ci == 1 and cur_c != gen_c:
                lines.append(f"    - 현행: {cur_c}")
                lines.append(f"    - 생성: {gen_c}")
        d = g["진단"]
        for side, dd in d["진술본문인용"].items():
            for lab, lst in dd.items():
                for kind, s, ls in lst:
                    lines.append(f"- 진단({side}): {lab}을 {s}의 {kind}이 인용한다(줄 {','.join(map(str, ls))}) — 증명 밖이라 셀에 넣지 않았다.")
        for side, lst in d["준비문단"].items():
            for sec, prev, n, hit in lst:
                where = f"{sec}장 머리말" if prev is None else f"{sec}절 준비 문단(진술 {prev} 뒤)"
                lines.append(f"- 진단({side}): {where}(줄 {n})이 {', '.join(hit)}을 인용한다 — 진술 밖이라 셀에 넣지 않았다.")
        lines.append("")
    # 현행에만 있는 행
    gen_names = {(g["표"], g["행"]["이름"]) for g in res["gen"]}
    for t, cs in cur_by_table.items():
        for c in cs:
            nm = split_name(c[0])[0]
            if (t, nm) not in gen_names:
                lines.append(f"### [{t}] {nm} — 행 정의에 없다(현행에만 있는 행)"); lines.append("")
    return lines, stats


# ---------------------------------------------------------------- 채우기
def fill(path, gen):
    L = io.open(path, encoding="utf-8").read().split("\n")
    i0 = next(i for i, ln in enumerate(L) if ln.startswith("### 11.3"))
    i1 = next(i for i, ln in enumerate(L) if i > i0 and ln.startswith("### 11.4"))
    starts = {}
    for i in range(i0, i1):
        for k, title in TABLE_TITLES.items():
            if L[i].startswith(title):
                starts[k] = i
    if set(starts) != set(TABLE_TITLES):
        raise SystemExit(f"세 표의 제목을 모두 찾지 못했다: {sorted(starts)}")
    first = min(starts.values())
    # 마지막 표 뒤의 끝: 마지막 표 줄 다음의 빈 줄까지
    last_title = max(starts.values())
    end = last_title
    for i in range(last_title + 1, i1):
        if L[i].startswith("|"):
            end = i
    new = tables_markdown(gen).rstrip("\n").split("\n")
    L[first:end + 1] = new
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print(f"filled {path}: 줄 {first + 1}–{end + 1} → {len(new)}줄")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=None, help="장v2 파일을 읽을 git 판(예: HEAD)")
    ap.add_argument("--rows", default=ROWS_DEFAULT)
    ap.add_argument("--init-rows", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--diff", action="store_true")
    ap.add_argument("--diff-out", default=None)
    ap.add_argument("--fill", default=None)
    ap.add_argument("--no-dedupe", action="store_true")
    ap.add_argument("--prep", action="store_true", help="절 안 준비 문단의 인용도 자리로 적는다(기본은 진술 범위만)")
    ap.add_argument("--debug", default=None, help="라벨 하나의 인용 정보를 적는다")
    args = ap.parse_args()
    src = Source(args.base)
    if args.init_rows:
        init_rows(src, args.rows, args.force)
        return
    rows = load_rows(args.rows)
    res = build(src, rows, dedupe=not args.no_dedupe, prep=args.prep)
    stmts = res["stmts"]
    print(f"진술 {len(stmts)}개, 부록 D 항목 {len(res['items'])}개(확인 라벨 {len(res['gmap'])}개), 행 {len(rows)}개"
          + (f", 판 {args.base}" if args.base else ""))
    if res["unknown"]:
        print(f"[경고] 행 정의의 라벨 가운데 원고에 없는 것: {', '.join(res['unknown'])}")
    noproof = [l for l, v in stmts.items() if v["kind"] != "정의" and not any(z in ("proof", "dproof") for _, _, z in v["lines"])]
    if noproof:
        print(f"[참고] 증명 범위를 찾지 못한 진술 {len(noproof)}개: {', '.join(noproof)}")
    if args.debug:
        lab = args.debug
        print(f"== {lab}: {stmts[lab]['kind']} {stmts[lab]['file']}:{stmts[lab]['line']} 절 {stmts[lab]['section']}")
        print("  의존:", ", ".join(sorted(res["deps"][lab], key=lambda l: stmts[l]["order"])))
        print("  인용하는 진술:")
        for s, c in res["cites"].items():
            if lab in c:
                print(f"    {s} ({stmts[s]['kind']}, {stmts[s]['file']}:{stmts[s]['line']}): 구역 {sorted(c[lab]['zones'])}, 줄 {sorted(set(c[lab]['lines']))}, 식 {sorted(c[lab]['eq'])}")
        print("  첫째 증명에서 닿음:", lab in res["first_depth"], "/ 둘째 증명에서 닿음:", lab in res["second_depth"])
    md = tables_markdown(res["gen"])
    if args.out:
        p = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(p, "w", encoding="utf-8", newline="\n").write(md)
        print("written", p)
    if args.diff:
        cur_tables, _ = read_current_tables(src)
        lines, stats = diff_report(res, cur_tables, rows)
        head = ["## 열별 셈", ""]
        for col, c in stats.items():
            head.append(f"- {col}: 글자 일치 {c['일치']}, 집합 일치(글자 순서·경유 설명만 다름) {c['일치(순서)']}, 진술 집합 일치(「의 증명」 표기만 다름) {c['일치(표기)']}, 불일치 {c['불일치']}")
        head.append("")
        text = "\n".join(head + lines)
        if args.diff_out:
            p = args.diff_out if os.path.isabs(args.diff_out) else os.path.join(ROOT, args.diff_out)
            io.open(p, "w", encoding="utf-8", newline="\n").write(text + "\n")
            print("diff written", p)
        else:
            print(text)
    if args.fill:
        p = args.fill if os.path.isabs(args.fill) else os.path.join(ROOT, args.fill)
        fill(p, res["gen"])


if __name__ == "__main__":
    main()
