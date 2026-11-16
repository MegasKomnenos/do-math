# -*- coding: utf-8 -*-
"""M14: 장 파일의 진술 머리(라벨·종류·이름·지위·절)를 뽑고,
장부/구조표/의존지도/대응표가 인용하는 라벨 가운데 정의가 없는 것을 센다."""
import re, sys, json, pathlib
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11",
         "부록A","부록B","부록C","부록D_장2","부록D_장3","부록D_장4","부록D_장5A","부록D_장5B",
         "부록D_장6","부록D_장7A","부록D_장7B","부록D_장8","부록D_장9","부록D_장10"]
head_re = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|관찰|예|주의|추측)\s+\{\{([^}]+)\}\}\s*(\((.*?)\))?\s*(\[([^\]]*(?:\][^\]]*)*?)\])?\.?\*\*")
sec_re = re.compile(r"^(#{2,4})\s+(\S+)\s+(.*)")
heads = {}
sections = []
for f in files:
    p = CH / (f + ".md")
    cur_sec = None
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        m = sec_re.match(line)
        if m:
            cur_sec = m.group(2)
            sections.append((f, i, m.group(1), m.group(2), m.group(3)))
        m = head_re.match(line)
        if m:
            kind, label, _, name, _, status = m.groups()
            if label in heads:
                print("DUP head", label, f, i, heads[label]["file"], heads[label]["line"])
            heads[label] = dict(kind=kind, name=(name or "").strip(), status=(status or "").strip(),
                                file=f, line=i, sec=cur_sec, text=line)
print("heads:", len(heads))
# all labels referenced anywhere in chapters
ref_re = re.compile(r"\{\{([^}]+)\}\}")
all_refs_ch = {}
for f in files:
    for i, line in enumerate((CH / (f + ".md")).read_text(encoding="utf-8").splitlines(), 1):
        for lab in ref_re.findall(line):
            all_refs_ch.setdefault(lab, []).append((f, i))
undefined_in_ch = sorted(l for l in all_refs_ch if l not in heads and not l.startswith("D:"))
print("chapter refs without head (non-D):", undefined_in_ch)
# D labels: defined in 부록D as '**{{D:...}}' or '### ' lines?
d_defs = set()
for f in files:
    if f.startswith("부록D"):
        for line in (CH / (f + ".md")).read_text(encoding="utf-8").splitlines():
            for lab in ref_re.findall(line):
                if lab.startswith("D:") and (line.startswith("**") or line.startswith("#")):
                    d_defs.add(lab)
undefined_D = sorted(l for l in all_refs_ch if l.startswith("D:") and l not in d_defs)
print("D refs without def line:", undefined_D)

# my files
mine = {"장부": ROOT / "장부_v2.md", "구조표": ROOT / "구조표_v2.md", "의존지도": ROOT / "의존지도_v2.md",
        "대응표": ROOT / "대조v2" / "라벨_번호_대응표_1114.md"}
for nm, p in mine.items():
    refs = {}
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for lab in ref_re.findall(line):
            refs.setdefault(lab, []).append(i)
    missing = {l: v for l, v in refs.items() if l not in heads and not (l.startswith("D:") and l in d_defs)}
    print(f"\n== {nm}: {len(refs)} distinct labels; not defined in chapters: {len(missing)}")
    for l, v in sorted(missing.items()):
        print("  ", l, "lines", v[:6])
json.dump({k: {kk: vv for kk, vv in v.items() if kk != 'text'} for k, v in heads.items()},
          open(ROOT / "scripts" / "수학검사2" / "_M14_heads.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(sections, open(ROOT / "scripts" / "수학검사2" / "_M14_sections.json", "w", encoding="utf-8"), ensure_ascii=False)
print("\nsections:", len(sections))
