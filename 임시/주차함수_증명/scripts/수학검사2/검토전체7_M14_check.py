# -*- coding: utf-8 -*-
"""M14: 대응표·의존지도 1절·장부 4절을 장 파일의 진술 머리와 맞춘다.
출력은 어긋남 후보 목록이며 판단은 손으로 한다."""
import re, pathlib, collections
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
chap_of = {"장1":1,"장2":2,"장3":3,"장4":4,"장5A":5,"장5B":5,"장6":6,"장7A":7,"장7B":7,"장8":8,"장9":9,"장10":10,"장11":11}
KINDS = "정의|정리|명제|보조정리|따름정리"
head_re = re.compile(r"^\*\*(" + KINDS + r")\s+\{\{([^}]+)\}\}\s*(\((.*?)\))?\s*(\[(.*?)\])?\.?\*\*")
proof_re = re.compile(r"^\*\*(?:" + KINDS + r")\s+\{\{([^}]+)\}\}\s*(?:\([^)]*\))?\s*(?:\((가|나|다|라|마|바|사|아)\)\s*)?의 증명")
sec_re = re.compile(r"^(#{2,4})\s+([0-9]+(?:\.[0-9]+)*)\s*(.*)")
ref_re = re.compile(r"\{\{([^}]+)\}\}")

heads = collections.OrderedDict()
bodies = collections.defaultdict(list)   # label -> list of lines (body + deferred proofs)
counter = collections.Counter()
for f in order:
    lines = (CH / (f + ".md")).read_text(encoding="utf-8").splitlines()
    cur_sec = None; cur_label = None
    for i, line in enumerate(lines, 1):
        m = sec_re.match(line)
        if m:
            cur_sec = m.group(2)
        mp = proof_re.match(line)
        mh = head_re.match(line)
        if mh and not mp:
            kind, label, _, name, _, status = mh.groups()
            c = chap_of[f]; counter[c] += 1
            heads[label] = dict(kind=kind, name=(name or "").strip(), status=(status or "").strip(),
                                file=f, line=i, sec=cur_sec, num=f"{c}.{counter[c]}", headline=line)
            cur_label = label
            continue
        if mp:
            cur_label = mp.group(1)
            bodies[cur_label].append(line)
            continue
        if cur_label:
            bodies[cur_label].append(line)
print("heads", len(heads))

def sec2(s):
    if not s: return s
    p = s.split("."); return ".".join(p[:2])

def cell_labels(s):
    return set(ref_re.findall(s))

# ---------- 대응표 ----------
print("\n===== 대응표 =====")
rows = 0; seen = set()
for line in (ROOT/"대조v2"/"라벨_번호_대응표_1114.md").read_text(encoding="utf-8").splitlines():
    if not line.startswith("| `{{"): continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    label = cells[0].strip("`{}"); kind, name, num, old, sec = cells[1:6]
    rows += 1; seen.add(label)
    h = heads.get(label)
    if not h: print("  없는 라벨", label); continue
    if h["kind"] != kind: print(f"  종류 {label}: 표 {kind} / 장 {h['kind']}")
    hn = h["name"] if h["name"] else "—"
    if hn.replace("\\*","*") != name.replace("\\*","*"): print(f"  이름 {label}: 표 「{name}」 / 장 「{hn}」")
    if h["num"] != num: print(f"  번호 {label}: 표 {num} / 장 {h['num']}")
    if sec2(h["sec"]) != sec: print(f"  절 {label}: 표 {sec} / 장 {h['sec']}")
print("rows", rows, "; 장에 있으나 표에 없는 라벨:", [l for l in heads if l not in seen])

# ---------- 장부 4절 ----------
print("\n===== 장부 4절 =====")
txt = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
in4 = False; seen4 = set(); first_ed = {}
for line in txt:
    if line.startswith("## 4."): in4 = True; continue
    if line.startswith("## 5."): break
    if not in4 or not line.startswith("| "): continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 6 or cells[0] in ("첫 판 번호","---"): continue
    old, kind, name, rec, sec, lab = cells[:6]
    if lab.startswith("("):
        l = lab.strip("()")
        if l in heads: print("  뺌 행인데 장에 머리 있음:", l)
        continue
    label = lab.strip("{}")
    seen4.add(label); first_ed[label] = old
    h = heads.get(label)
    if not h: print("  없는 라벨", label); continue
    if h["kind"] != kind: print(f"  종류 {label}: 장부 {kind} / 장 {h['kind']}")
    full = name + ("; " + rec if rec else "")
    if full.strip() != h["name"].strip(): print(f"  이름 {label}: 장부 「{full}」 / 장 「{h['name']}」")
    if sec2(h["sec"]) != sec: print(f"  절 {label}: 장부 {sec} / 장 {h['sec']}")
print("장에 있으나 4절에 없는 라벨:", [l for l in heads if l not in seen4])

# ---------- 의존지도 1절 ----------
print("\n===== 의존지도 1절 =====")
dep_rows = 0; seen_d = set()
for line in (ROOT/"의존지도_v2.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("### 1.1"): break
    if not line.startswith("| `{{"): continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    label = cells[0].strip("`{}"); sec, old, gist, status, inputs = cells[1:6]
    dep_rows += 1; seen_d.add(label)
    h = heads.get(label)
    if not h: print("  없는 라벨", label); continue
    if sec2(h["sec"]) != sec: print(f"  절 {label}: 지도 {sec} / 장 {h['sec']}")
    # 첫 판 번호
    fe = first_ed.get(label, "")
    exp_old = "새 진술" if fe == "—" else f"{h['kind']} {fe}"
    if old != exp_old: print(f"  첫판번호 {label}: 지도 「{old}」 / 장부4절 「{exp_old}」")
    # 요지 vs head name
    if h["name"] and gist.replace("\\*","*") != h["name"].replace("\\*","*"):
        print(f"  요지 {label}: 지도 「{gist}」 / 장 「{h['name']}」")
    # 지위
    st = h["status"].split(";")[0].strip()
    st_norm = re.sub(r"`", "", st)
    if status.replace("`","") != st_norm:
        print(f"  지위 {label}: 지도 「{status}」 / 장 「{st}」")
    # 입력 라벨
    if "본문 인용:" in inputs:
        hd, bd = inputs.split("본문 인용:", 1)
    else:
        hd, bd = inputs, ""
    hd_set = cell_labels(hd); bd_set = cell_labels(bd)
    real_hd = cell_labels(h["headline"]) - {label}
    real_bd = set()
    for bl in bodies[label]:
        real_bd |= cell_labels(bl)
    real_bd -= {label}
    real_bd = {l for l in real_bd if not l.startswith("D:")}
    real_bd -= real_hd
    if hd_set != real_hd:
        print(f"  머리 인용 {label}: 지도에만 {sorted(hd_set-real_hd)} / 장에만 {sorted(real_hd-hd_set)}")
    if bd_set != real_bd:
        print(f"  본문 인용 {label}: 지도에만 {sorted(bd_set-real_bd)} / 장에만 {sorted(real_bd-bd_set)}")
print("rows", dep_rows, "; 장에 있으나 지도에 없는 라벨:", [l for l in heads if l not in seen_d])
