# -*- coding: utf-8 -*-
"""9장 제거 뒤 장 번호 전역 치환(세션 V7). 2026-11-17.

10장 → 9장, 11장 → 10장. 범위는 (1) 장 파일 `장v2/장*.md`·`장v2/부록D_*.md`와 그 이름, (2) 장부 `장부_v2.md`와 부록 A·B·C
(임자 V6이 「모두 현행」으로 확인하고 제외 자리를 인계 「세션」 10항에 적음), (3) 장 파일 경로·장 번호를 전제한 활성 스크립트.
구조표 `구조표_v2.md`는 설계 번호의 동결 기록(결정 102)이라 치환하지 않고 머리말에 메모 한 줄만 넣는다(V6 권고).
지도 덧씌우기·설정은 지도 갱신 작업자(라운드14)가 같은 대응으로 한다.

바꾸는 것:
  라벨   {{10:…}} → {{9:…}}, {{11:…}} → {{10:…}}(현행 0); 백틱 라벨 `10:…` → `9:…`
  머리   ## 10. → ## 9., ## 11. → ## 10., ### 10.N → ### 9.N, ### 11.N → ### 10.N
  낱말   10장 → 9장, 11장 → 10장(앞에 숫자가 없는 것)
  절 참조 10.N절 → 9.N절, 11.N절 → 10.N절(앞에 숫자·점·§가 없는 것)
  장11의 11.2 표(「| 부록 D.{{D:…}} |」 행)의 「놓인 곳」 칸 10.N → 9.N
  장부·부록 A·B·C의 맨 10.N·11.N(정의 절 열·뜻 열·자리 열·괄호의 현행 절 번호) → 9.N·10.N — 아래 제외 꼴만 빼고
제외(V6 인계 「세션」 10항; 2차 판·옛 번호·기록 안의 §·식 번호): 「2차–물결 2의 …(10.5)」「2차–물결 2의 10.5 묶음/절」「10.5 2차」
  「2차 10.N(절)」「옛 10.N(·10.M)」「(10.5의)」「§10.1–10.2」「§11.6」「[r0dc57fa]의 (10.1)」. 장 파일의 맨 10.N은 바꾸지 않는다
  (기록 식 번호 (10.1)·기록 절 §10.1–10.3·수치 11.10) — 남은 자리를 모두 출력한다.
이름: 장10.md → 장9.md, 부록D_장10.md → 부록D_장9.md, 장11.md → 장10.md (git mv; 내용 치환 뒤).

사용: python -I scripts/구조압축/장번호_치환_1117.py [--apply]   (기본은 건조 실행)
"""
import io, os, re, sys, subprocess, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHAP = os.path.join(ROOT, "장v2")
APPLY = "--apply" in sys.argv
MAP = {"10": "9", "11": "10"}

MASKS = [  # 장부·부록 A·B·C에서 치환하지 않을 꼴(V6 인계 「세션」 10항)
    r"2차–물결 2의 [^|]*?\(10\.5\)",  # 가운데 $\mathfrak h_y(q)$처럼 괄호 든 수식이 올 수 있다
    r"2차–물결 2의 10\.5 ?묶음",
    r"2차–물결 2의 10\.5절",
    r"10\.5 2차",
    r"2차 10\.\d+절?",
    r"옛 10\.\d+(?:·10\.\d+)*",
    r"\(10\.5의\)",
    r"§1[01]\.\d+(?:–1[01]\.\d+)?",
    r"\[r0dc57fa\]의 \(10\.1\)",
]

def common_subs(t):
    n = {}
    def cnt(k, c): n[k] = n.get(k, 0) + c
    t, c = re.subn(r"\{\{(10|11):", lambda m: "{{" + MAP[m.group(1)] + ":", t); cnt("{{N:", c)
    t, c = re.subn(r"`(10|11):", lambda m: "`" + MAP[m.group(1)] + ":", t); cnt("`N:", c)
    t, c = re.subn(r"^## (10|11)\.", lambda m: "## " + MAP[m.group(1)] + ".", t, flags=re.M); cnt("## N.", c)
    t, c = re.subn(r"^### (10|11)\.(\d)", lambda m: "### " + MAP[m.group(1)] + "." + m.group(2), t, flags=re.M); cnt("### N.m", c)
    t, c = re.subn(r"(?<!\d)(10|11)장", lambda m: MAP[m.group(1)] + "장", t); cnt("N장", c)
    t, c = re.subn(r"(?<![\d.§])(10|11)\.(\d)(?=절|–(?:10|11)\.\d절)", lambda m: MAP[m.group(1)] + "." + m.group(2), t); cnt("N.m절", c)
    return t, n

def chapter_subs(t, fname):
    t, n = common_subs(t)
    if fname == "장11.md":
        lines = t.split("\n"); c = 0
        for i, ln in enumerate(lines):
            if ln.startswith("| 부록 D.{{D:"):
                new, k = re.subn(r"\| (10|11)\.(\d) \|", lambda m: "| " + MAP[m.group(1)] + "." + m.group(2) + " |", ln)
                lines[i] = new; c += k
        t = "\n".join(lines); n["11.2표 칸"] = c
    return t, n

def ledger_subs(t):
    """장부·부록 A·B·C: 제외 꼴을 가린 뒤 공통 치환 + 맨 10.N·11.N 치환, 그리고 복원."""
    masked = []
    def hide(m):
        masked.append(m.group(0)); return f"\x00{len(masked)-1}\x00"
    for p in MASKS:
        t = re.sub(p, hide, t)
    t, n = common_subs(t)
    t, c = re.subn(r"(?<![\d.])(10|11)\.(\d)(?!\d)", lambda m: MAP[m.group(1)] + "." + m.group(2), t); n["맨 N.m"] = c
    t = re.sub(r"\x00(\d+)\x00", lambda m: masked[int(m.group(1))], t)
    n["제외(가림)"] = len(masked)
    return t, n

def leftovers(t, fname):
    out = []
    for i, ln in enumerate(t.split("\n"), 1):
        for m in re.finditer(r"(?<![\d.])(10|11)\.(\d\d?)(?!\d)|(?<!\d)11장|\{\{11:|`11:|^## 11\.|^### 11\.", ln):
            a = max(0, m.start() - 30); b = min(len(ln), m.end() + 20)
            out.append(f"  {fname}:{i}: …{ln[a:b]}…")
    return out

chapter_files = sorted(p for p in glob.glob(os.path.join(CHAP, "*.md")) if re.match(r"(장\d|부록D_장)", os.path.basename(p)))
ledger_files = [os.path.join(ROOT, "장부_v2.md"), os.path.join(CHAP, "부록A.md"), os.path.join(CHAP, "부록B.md"), os.path.join(CHAP, "부록C.md")]
_pre9 = sum(io.open(p, encoding="utf-8").read().count("{{9:") for p in chapter_files)
assert _pre9 == 0, f"장 파일에 {{{{9: 라벨이 {_pre9}개 남아 있다 — 먼저 거둔다"

total = {}; left = []; changed = {}
for p in chapter_files + ledger_files:
    fname = os.path.basename(p)
    raw = io.open(p, "rb").read(); assert b"\r" not in raw, fname
    t = raw.decode("utf-8")
    new, n = chapter_subs(t, fname) if p in chapter_files else ledger_subs(t)
    for k, v in n.items(): total[k] = total.get(k, 0) + v
    if new != t:
        changed[fname] = (len(raw), len(new.encode("utf-8")), n)
        if APPLY:
            io.open(p, "w", encoding="utf-8", newline="\n").write(new)
    left += leftovers(new, fname)

print("적용" if APPLY else "건조 실행", "— 바꾼 수(종류별):", total)
for f, (a, b, n) in changed.items():
    print(f"  {f}: {a:,} → {b:,} B  {n}")
print("남은 맨 10.N·11.N·11장·{{11: 자리(검토용):", len(left))
print("\n".join(left))

# 구조표 머리말 메모(치환하지 않음을 적는다)
STRUCT = os.path.join(ROOT, "구조표_v2.md")
MEMO = "(2026-11-17 9장 제거 뒤 세션 메모: 원고·장부·부록의 장 번호를 전역 치환했다 — 10장→9장, 11장→10장, `{{10:`→`{{9:`; 이 표는 설계 때의 번호와 라벨 접두를 그대로 둔다. 「옛 9장」은 지운 첫째 증명의 장이고, 이 표의 「10장」·`{{10:`은 현행 9장이다.)"
s_struct = io.open(STRUCT, encoding="utf-8").read()
if MEMO not in s_struct:
    lines = s_struct.split("\n")
    assert lines[2].startswith("작성일 2026-11-12."), lines[2][:40]
    lines[2] = lines[2].rstrip() + " " + MEMO
    if APPLY:
        io.open(STRUCT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        print("구조표 머리말 메모 추가")
    else:
        print("[건조] 구조표 머리말 3행에 메모 추가 예정")

RENAMES = [("장v2/장10.md", "장v2/장9.md"), ("장v2/부록D_장10.md", "장v2/부록D_장9.md"), ("장v2/장11.md", "장v2/장10.md")]
SCRIPT_EDITS = [
    ("scripts/_sync_11_2꺾쇠.py", [('"장11.md"', '"장10.md"'), ("11.2 표(장v2/장11.md)", "11.2 표(지금은 10.2절; 장v2/장10.md)")]),
    ("scripts/_sync_11_2행.py", [('"장11.md"', '"장10.md"'), ("--fill 장v2/장11.md", "--fill 장v2/장10.md"), ("11.2 표(장v2/장11.md)", "11.2 표(지금은 10.2절; 장v2/장10.md)")]),
    ("scripts/_gen_11_2표.py", [("--fill 장v2/장11.md", "--fill 장v2/장10.md"), ('"""11.2 「컴퓨터 계산의 명세」 표', '"""11.2(9장 제거 뒤 10.2) 「컴퓨터 계산의 명세」 표')]),
    ("scripts/_gen_의존지도_1절.py", [('CH11 = os.path.join(ROOT, "장v2", "장11.md")', 'CH11 = os.path.join(ROOT, "장v2", "장10.md")  # 9장 제거 뒤 보증 장은 10장'),
                                      ('if ln.startswith("### 11.4"):', 'if ln.startswith("### 10.3"):  # 문헌 표(옛 11.4 → 11.3 → 9장 제거 뒤 10.3)'),
                                      ('appd = "머리에 계산 보조 표시, 11.2 표에 항목 없음"', 'appd = "머리에 계산 보조 표시, 10.2 표에 항목 없음"'),
                                      ('"/ 문헌(11.4절)"', '"/ 문헌(10.3절)"')]),
    ("scripts/불변식_v2.py", [("in_body = 1 <= ch <= 10", "in_body = 1 <= ch <= 9  # 9장 제거 뒤 본문은 1–9장"), ("in_guarantee = ch == 11", "in_guarantee = ch == 10  # 보증 장은 10장"),
                             ('notes.append(f"{i}(11장/부록): 금지어', 'notes.append(f"{i}(10장/부록): 금지어'), ('failures.append(f"{i}: 11장 밖 운영 어휘', 'failures.append(f"{i}: 10장 밖 운영 어휘')]),
    ("scripts/수학검사2/정합검토_잔재검사_1114.py", [('"장11.md"', '"장10.md"'), ('11.2 행 {rows_112}', '10.2 행 {rows_112}')]),
    ("scripts/_보관_tmp/_파이프라인_수리후_1115.sh", [("장v2/장11.md", "장v2/장10.md")]),
    ("scripts/조립_v2.py", [("장v2/장1.md … 장v2/장11.md", "장v2/장1.md … 장v2/장10.md"), ("부록D_장N.md(N=1..11)", "부록D_장N.md(있는 N만; 9장 제거 뒤 N≤10)")]),
]
if APPLY:
    for src, dst in RENAMES:
        assert os.path.exists(os.path.join(ROOT, src)) and not os.path.exists(os.path.join(ROOT, dst)), (src, dst)
        r = subprocess.run(["git", "mv", src, dst], cwd=ROOT, capture_output=True)
        print("git mv", src, "→", dst, r.returncode, r.stderr.decode("utf-8", "replace").strip())
    for rel, edits in SCRIPT_EDITS:
        p = os.path.join(ROOT, rel); s = io.open(p, encoding="utf-8").read(); k = 0
        for a, b in edits:
            if a in s: s = s.replace(a, b); k += 1
            else: print("  !! 못 찾음:", rel, a[:60])
        io.open(p, "w", encoding="utf-8", newline="\n").write(s); print("스크립트", rel, "교체", k, "/", len(edits))
else:
    print("\n[건조] 이름 바꾸기 예정:", RENAMES)
    for rel, edits in SCRIPT_EDITS:
        s = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
        miss = [a for a, b in edits if a not in s]
        print(f"[건조] {rel}: 교체 {len(edits)-len(miss)}/{len(edits)}" + (f"  못 찾음: {miss}" if miss else ""))
