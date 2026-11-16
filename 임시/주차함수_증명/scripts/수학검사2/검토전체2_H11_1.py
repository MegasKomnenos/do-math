# -*- coding: utf-8 -*-
"""H11 검산: 장11·부록 A·B·C의 라벨·종류·절·산술 등급·식별자를 본문과 대조한다. 파일은 고치지 않는다."""
import re, glob, os, sys, json
ROOT = r"C:\math\임시\주차함수_증명"
V2 = os.path.join(ROOT, "장v2")
RECORDS = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read().splitlines()

HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([\w\-']+)\}\}\s*(?:\((.*?)\)\s*)?\[(.*?)\]\.\*\*")
HEAD2 = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([\w\-']+)\}\}(.*?)\*\*")
SEC = re.compile(r"^#{2,4}\s*(\d+(?:\.\d+)*)\b")

stmts = {}  # label -> dict
order = []
for fn in sorted(glob.glob(os.path.join(V2, "장*.md"))):
    if "장11" in fn: continue
    lines = rd(fn)
    sec = None
    cur = None
    for i, ln in enumerate(lines, 1):
        m = SEC.match(ln)
        if m:
            sec = m.group(1)
        m = HEAD.match(ln)
        if m:
            kind, ch, lab, title, tag = m.groups()
            key = f"{ch}:{lab}"
            stmts[key] = dict(kind=kind, title=title or "", tag=tag, file=os.path.basename(fn), line=i, sec=sec, block=[])
            order.append(key); cur = key
        elif ln.startswith("**") and HEAD2.match(ln):
            m2 = HEAD2.match(ln)
            kind, ch, lab, rest = m2.groups()
            key = f"{ch}:{lab}"
            # 정의 without bracket
            if key not in stmts:
                stmts[key] = dict(kind=kind, title="", tag=rest.strip(), file=os.path.basename(fn), line=i, sec=sec, block=[])
                order.append(key)
            cur = key
        if cur:
            stmts[cur]["block"].append(ln)

print("진술 수", len(stmts))

# 부록 D 항목
ditems = {}
for fn in sorted(glob.glob(os.path.join(V2, "부록D_*.md"))):
    lines = rd(fn)
    cur = None
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^### D\.\{\{D:([\w\-]+)\}\}\s*(.*?)\s*\((.*)\)\s*$", ln)
        if m:
            cur = m.group(1)
            ditems[cur] = dict(file=os.path.basename(fn), line=i, title=m.group(2), head_stmts=m.group(3), grade=None, recomp=None)
        elif cur:
            if ln.startswith("**산술 등급.**"):
                ditems[cur]["grade"] = ln[len("**산술 등급.**"):].strip()
            elif ln.startswith("**독립 재계산.**"):
                ditems[cur]["recomp"] = ln[len("**독립 재계산.**"):].strip()
print("부록 D 항목 수", len(ditems))

L11 = rd(os.path.join(V2, "장11.md"))
LAB = re.compile(r"(정리|명제|보조정리|따름정리|정의)?\s*\{\{(\w+):([\w\-']+)\}\}")

def labels_in(s):
    out = []
    for m in re.finditer(r"(정리|명제|보조정리|따름정리|정의)\s*((?:\{\{\w+:[\w\-']+\}\}\s*·?\s*)+)", s):
        kind = m.group(1)
        for mm in re.finditer(r"\{\{(\w+):([\w\-']+)\}\}", m.group(2)):
            out.append((kind, f"{mm.group(1)}:{mm.group(2)}"))
    return out

issues = []
def issue(where, msg):
    issues.append((where, msg)); print("!!", where, msg)

# ---- 11.2 표 ----
print("\n== 11.2 표 ==")
GRADES = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석"]
for i, ln in enumerate(L11, 1):
    if ln.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 6:
            issue(f"장11 {i}", f"열 수 {len(cells)}"); continue
        dlab = re.search(r"\{\{D:([\w\-]+)\}\}", cells[0]).group(1)
        if dlab not in ditems:
            issue(f"장11 {i}", f"부록 D 항목 없음 {dlab}"); continue
        d = ditems[dlab]
        # 확인하는 진술 vs 부록 D 머리 괄호
        a = set(labels_in(cells[1])); b = set(labels_in(d["head_stmts"]))
        if a != b:
            issue(f"장11 {i}", f"D.{dlab} 확인 진술 불일치: 11.2 {a} vs 부록D 머리 {b}")
        for kind, key in a:
            if key not in stmts:
                issue(f"장11 {i}", f"라벨 없음 {key}")
            else:
                if stmts[key]["kind"] != kind:
                    issue(f"장11 {i}", f"종류 불일치 {key}: 11.2 {kind} vs 본문 {stmts[key]['kind']}")
                # 쓰인 곳
                secs = [s.strip() for s in cells[3].split("·")]
                ssec = stmts[key]["sec"]
                ssec2 = ".".join(ssec.split(".")[:2]) if ssec else None
                if ssec2 not in secs:
                    issue(f"장11 {i}", f"D.{dlab} 쓰인 곳 {cells[3]} vs {key} 실제 절 {ssec} ({stmts[key]['file']}:{stmts[key]['line']})")
                # 산술 등급 vs 표지
                tag = stmts[key]["tag"]
                tg = set(g for g in GRADES if g in tag)
                if "평가" in tag:
                    tg.add("평가")
                cg = set(g for g in GRADES if g in cells[2])
                if not cg <= tg or not tg <= cg:
                    print(f"  ? 장11 {i} D.{dlab} {key}: 11.2 등급 [{cells[2]}] vs 표지 [{tag}]")
        # 산술 등급 열 vs 부록 D 산술 등급 줄 첫 등급
        g = d["grade"] or ""
        first = re.split(r"[;。.]", g)[0]
        cg = [x for x in GRADES if x in cells[2]]
        if not all(x in g for x in cg):
            issue(f"장11 {i}", f"D.{dlab} 11.2 등급 [{cells[2]}] 가 부록 D 등급 줄 [{g[:120]}] 에 없음")
        # 재계산 열 꺾쇠 vs 부록 D 독립 재계산 줄 첫머리
        rc = d["recomp"] or ""
        m = re.match(r"〔(.*?)〕\s*(.*)$", rc)
        if m:
            if cells[4] != f"〔{m.group(1)}〕":
                issue(f"장11 {i}", f"D.{dlab} 재계산 꺾쇠 불일치:\n   11.2 {cells[4]}\n   부록D {m.group(1)}")
            rest = m.group(2).strip()
            if cells[5].strip() != rest:
                # 비교: 공백 정규화
                if re.sub(r"\s+", "", cells[5]) != re.sub(r"\s+", "", rest):
                    issue(f"장11 {i}", f"D.{dlab} 독립 재계산 서술 불일치 (len {len(cells[5])} vs {len(rest)})")
                    # 첫 차이 위치
                    x, y = cells[5], rest
                    k = next((j for j in range(min(len(x), len(y))) if x[j] != y[j]), min(len(x), len(y)))
                    print("   11.2:", x[max(0,k-40):k+80]); print("   부록D:", y[max(0,k-40):k+80])
        else:
            issue(f"장11 {i}", f"D.{dlab} 부록 D 독립 재계산 줄에 꺾쇠 없음: {rc[:80]}")

# 11.2 표에 없는 부록 D 항목
rows = set(re.search(r"\{\{D:([\w\-]+)\}\}", ln).group(1) for ln in L11 if ln.startswith("| 부록 D.{{D:"))
for k in ditems:
    if k not in rows: issue("장11 11.2", f"부록 D 항목 {k}가 11.2 표에 없음")

# ---- 11.3·11.4 라벨 존재·종류 ----
print("\n== 11.3·11.4 라벨 ==")
for i, ln in enumerate(L11, 1):
    if i < 65: continue
    for kind, key in labels_in(ln):
        if key not in stmts:
            issue(f"장11 {i}", f"라벨 없음 {key}")
        elif stmts[key]["kind"] != kind:
            issue(f"장11 {i}", f"종류 불일치 {key}: 장11 {kind} vs 본문 {stmts[key]['kind']} ({stmts[key]['file']}:{stmts[key]['line']})")

# 11.3 쓰는 자리: 9장·10장 진술 블록이 입력 라벨을 포함하는지
print("\n== 11.3 쓰는 자리(블록 인용 검사) ==")
def table_rows(start_pat, L):
    out = []
    on = False
    for i, ln in enumerate(L, 1):
        if ln.startswith(start_pat): on = True; continue
        if on and ln.startswith("| 입력"): continue
        if on and ln.startswith("|---"): continue
        if on and ln.startswith("|"): out.append((i, [c.strip() for c in ln.strip().strip("|").split("|")]))
        elif on and not ln.strip():
            if out: on = False
    return out
shared = table_rows("**공유 입력.**", L11)
own1 = table_rows("**첫째 증명의 고유 입력.**", L11)
own2 = table_rows("**둘째 증명의 고유 입력.**", L11)
print(len(shared), len(own1), len(own2))

def check_uses(rowi, inputs, usecell, tag):
    inkeys = set(k for _, k in labels_in(inputs))
    # 9장/10장 진술 라벨 in usecell (바깥 괄호 밖의 것만 보기 어려우므로 전부 본 뒤 7:old-6-22 등 특수 처리)
    for kind, key in labels_in(usecell):
        if key in inkeys: continue
        if key not in stmts: continue
        ch = key.split(":")[0]
        blk = "\n".join(stmts[key]["block"])
        hit = [k for k in inkeys if "{{"+k+"}}" in blk]
        if not hit:
            print(f"  ? 장11 {rowi} [{tag}] 자리 {key}({stmts[key]['file']}:{stmts[key]['line']}) 블록에 입력 {sorted(inkeys)} 인용 없음")
for i, c in shared:
    if len(c) >= 4:
        check_uses(i, c[0] + " " + c[1], c[2], "공유·첫째"); check_uses(i, c[0] + " " + c[1], c[3], "공유·둘째")
for i, c in own1:
    if len(c) >= 3: check_uses(i, c[0] + " " + c[1], c[2], "첫째 고유")
for i, c in own2:
    if len(c) >= 3: check_uses(i, c[0] + " " + c[1], c[2], "둘째 고유")

# 11.3 등급 열: 라벨의 표지 등급과 대조
print("\n== 11.3 계산 진술 등급 vs 표지 ==")
for i, c in shared + own1 + own2:
    if len(c) < 2: continue
    cell = c[1]
    # 분할: ';' 로 그룹, 각 그룹 '라벨들: 등급'
    for grp in cell.split(";"):
        if ":" not in grp.replace("{{", "").replace("}}", ""):
            pass
        m = re.match(r"(.*?)\}\}\s*(?:\(.*?\))?\s*:\s*([^()]+?)(?:\(.*)?$", grp.strip())
        if not m:
            continue
        labs = labels_in(m.group(1) + "}}")
        grades = m.group(2).strip()
        for kind, key in labs:
            if key not in stmts: continue
            tag = stmts[key]["tag"]
            for g in GRADES:
                if g in grades and g not in tag:
                    print(f"  ? 장11 {i} {key}: 11.3 등급 [{grades}] 에 {g} 있으나 표지 [{tag}] 에 없음")
            for g in GRADES:
                if g in tag and g not in grades:
                    print(f"  ? 장11 {i} {key}: 표지 [{tag}] 에 {g} 있으나 11.3 등급 [{grades}] 에 없음")

# 계산 증거/계산 보조 진술 가운데 11.3 세 표 어디에도 없는 것(참고)
print("\n== 계산 진술 가운데 11.3에 없는 것(참고) ==")
all113 = set(k for i, c in shared + own1 + own2 for _, k in labels_in(" ".join(c)))
for key, s in stmts.items():
    if ("계산 증거" in s["tag"] or "계산 보조" in s["tag"]) and key not in all113:
        print("  ", key, s["file"], s["line"], s["tag"][:80])

# ---- 부록 B ----
print("\n== 부록 B ==")
LB = rd(os.path.join(V2, "부록B.md"))
bids = {}
for i, ln in enumerate(LB, 1):
    m = re.match(r"^\| (r[0-9a-f]{7}) \| ([\d\-: ]+) \| (.*?) \| `(\w+)` \|", ln)
    if m:
        bids[m.group(1)] = dict(line=i, time=m.group(2).strip(), title=m.group(3), folder=m.group(4))
        if not m.group(4).startswith(m.group(1)):
            issue(f"부록B {i}", "폴더 이름과 식별자 불일치")
print("부록 B 식별자 수", len(bids))
used = {}
for fn in glob.glob(os.path.join(V2, "*.md")):
    if fn.endswith("부록B.md"): continue
    for i, ln in enumerate(rd(fn), 1):
        for m in re.finditer(r"\br([0-9a-f]{7})\b", ln):
            used.setdefault("r"+m.group(1), []).append((os.path.basename(fn), i))
for k in used:
    if k not in bids: issue("부록B", f"본문·부록에 쓰인 식별자 {k}가 부록 B에 없음: {used[k][:3]}")
for k in bids:
    if k not in used: print(f"  ? 부록B {bids[k]['line']} {k}: 본문·부록 어디에도 안 쓰임")
# 시각 순서
times = [(bids[k]["time"], k, bids[k]["line"]) for k in bids]
for (t1, k1, l1), (t2, k2, l2) in zip(times, times[1:]):
    if t2 < t1: issue(f"부록B {l2}", f"시각 순서 어긋남 {k1} {t1} -> {k2} {t2}")
# 폴더 존재·제목
if os.path.isdir(RECORDS):
    folders = os.listdir(RECORDS)
    for k, v in bids.items():
        cand = [f for f in folders if f.startswith(v["folder"])]
        if not cand:
            issue(f"부록B {v['line']}", f"기록 폴더 없음 {v['folder']}")
        else:
            rj = os.path.join(RECORDS, cand[0], "record.json")
            if os.path.exists(rj):
                try:
                    j = json.load(open(rj, encoding="utf-8"))
                    t = j.get("title") or j.get("제목") or ""
                    if t and re.sub(r"\s+", "", t) != re.sub(r"\s+", "", v["title"]):
                        print(f"  ? 부록B {v['line']} {k} 제목 다름:\n     B: {v['title']}\n     J: {t}")
                except Exception as e:
                    print("  json err", k, e)
else:
    print("records 폴더 없음(건너뜀)")

# ---- 부록 C 둘째 표 ----
print("\n== 부록 C 둘째 표 ==")
LC = rd(os.path.join(V2, "부록C.md"))
on = False
for i, ln in enumerate(LC, 1):
    if ln.startswith("### 기록이 결과에 붙인 이름"): on = True; continue
    if ln.startswith("### 기록의 글자"): on = False
    if on and ln.startswith("| 기록") and "{{" in ln:
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 3: issue(f"부록C {i}", "열 수"); continue
        labs = labels_in(c[1])
        if not labs: issue(f"부록C {i}", f"라벨 못 읽음 {c[1]}"); continue
        for kind, key in labs:
            if key not in stmts: issue(f"부록C {i}", f"라벨 없음 {key}"); continue
            s = stmts[key]
            if s["kind"] != kind: issue(f"부록C {i}", f"종류 불일치 {key}: C {kind} vs 본문 {s['kind']}")
            title = s["title"].split(";")[0].strip()
            name = c[2].strip()
            if name != "—" and re.sub(r"\s+", "", name) != re.sub(r"\s+", "", title):
                print(f"  ? 부록C {i} {key} 이름 다름: C「{name}」 vs 본문 제목「{title}」")
            # 기록 이름이 본문 머리 괄호에 있는지
            recname = c[0]
            m = re.match(r"기록 \[(r[0-9a-f]{7})\]", recname)
            if m and m.group(1) not in s["title"] and m.group(1) not in s["tag"]:
                print(f"  ? 부록C {i} {key}: 기록 {m.group(1)}이 본문 머리(제목·표지)에 없음: 「{s['title']}」[{s['tag']}]")
# 본문 머리 제목에 '기록 [...]의' 가 있는 진술 가운데 부록 C 둘째 표에 없는 것
ctab = set()
on = False
for ln in LC:
    if ln.startswith("### 기록이 결과에 붙인 이름"): on = True; continue
    if ln.startswith("### 기록의 글자"): on = False
    if on:
        for _, k in labels_in(ln): ctab.add(k)
for key, s in stmts.items():
    if "기록 [" in s["title"] and key not in ctab:
        print(f"  ? 본문 {key} ({s['file']}:{s['line']}) 제목에 기록 이름 있으나 부록 C 둘째 표에 없음: {s['title']}")

# ---- 부록 A: 라벨 존재 ----
print("\n== 부록 A·C 라벨 존재 ==")
for fnm in ["부록A.md", "부록C.md"]:
    for i, ln in enumerate(rd(os.path.join(V2, fnm)), 1):
        for m in re.finditer(r"\{\{(\w+):([\w\-']+)\}\}", ln):
            key = f"{m.group(1)}:{m.group(2)}"
            if key not in stmts: issue(f"{fnm} {i}", f"라벨 없음 {key}")

# ---- 11.4: 절 번호 존재 ----
print("\n== 11.4 절 번호 ==")
secs = set()
for fn in glob.glob(os.path.join(V2, "장*.md")):
    for ln in rd(fn):
        m = SEC.match(ln)
        if m: secs.add(m.group(1))
for i, ln in enumerate(L11, 1):
    if i >= 134 and ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| 문헌"):
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        for m in re.finditer(r"(?<![\d.])(\d+\.\d+)절", c[2]):
            if m.group(1) not in secs: issue(f"장11 {i}", f"절 없음 {m.group(1)}")

print("\n문제 수", len(issues))
