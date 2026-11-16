# -*- coding: utf-8 -*-
"""11.2 표(장v2/장11.md)의 여섯 열을 부록 D 항목의 머리·산술 등급 줄·독립 재계산 줄과 대조한다(읽기 전용).
A11(11차 수리)이 세션에 알릴 어긋남을 찾는 데 썼다. 사용: python -I scripts/수학검사2/수리_전체11_A11_11_2대조.py"""
import glob, io, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import importlib.util
spec = importlib.util.spec_from_file_location("gen", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_gen_11_2표.py"))
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
ROOT = gen.ROOT
rows = {r["name"]: r for r in gen.rows()}
# 독립 재계산 전문(_sync_11_2행.py와 같은 규칙)
PREFIX = re.compile(r"^\*\*독립 재계산\.\*\*\s*〔[^〕]*〕\s*")
full = {}
for p in glob.glob(os.path.join(ROOT, "장v2", "부록D_*.md")):
    cur = None
    for l in io.open(p, encoding="utf-8").read().split("\n"):
        m = gen.HEAD.match(l)
        if m: cur = m.group(1); continue
        if cur and l.startswith("**독립 재계산.**"):
            s = PREFIX.sub("", l).strip().replace("이 문단 머리의 꺾쇠 괄호", "「재계산」 열의 꺾쇠 괄호")
            full[cur] = gen.cell(s)
lines = io.open(os.path.join(ROOT, "장v2", "장11.md"), encoding="utf-8").read().split("\n")
n = 0
for ln in lines:
    if not ln.startswith("| 부록 D.{{D:"): continue
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    name = re.match(r"부록 D\.\{\{D:([A-Za-z0-9\-]+)\}\}", cells[0]).group(1)
    r = rows.get(name)
    if r is None: print("D에 없음:", name); continue
    n += 1
    exp = [gen.cell(r["stmt"]), gen.cell(r["grade"]), r["secs"], r["tag"], full.get(name, "")]
    names = ["확인하는 진술", "산술 등급", "쓰인 곳", "재계산 꺾쇠", "독립 재계산 전문"]
    for nm, got, ex in zip(names, cells[1:6], exp):
        if got != ex:
            print(f"[{name}] {nm} 다름\n  표: {got[:300]}\n  D : {ex[:300]}")
print("대조한 행", n, "/ D 항목", len(rows))
