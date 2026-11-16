# -*- coding: utf-8 -*-
"""ZV3 탐색: 묶음의 기록 코드 사본(원고_자료/r*/…)이 import하는데 같은 묶음 폴더에 없는 모듈을
연구 기록 원본 폴더에서 찾아, 그 기록 안의 상대 경로와 그 스크립트가 든 부록 D 항목(README 파일 목록의 라벨)을 적는다.
기록은 읽기만 한다.
사용: python -I scripts/수학검사2/검토_외부피드백_1116_ZV3_locate.py
"""
import ast
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUNDLE = os.path.join(ROOT, "원고_자료")
RECORDS = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
STD = set(sys.stdlib_module_names) | {"numpy", "mpmath", "scipy", "sympy", "gmpy2", "matplotlib", "pandas", "flint",
                                      "cypari2", "tqdm", "numba", "mpi4py"}

# README 파일 목록: 묶음 경로 -> (기록 경로, 라벨)
readme = {}
for ln in open(os.path.join(BUNDLE, "README.md"), encoding="utf-8"):
    if ln.startswith("| `"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 4:
            readme[cells[0].strip("`")] = (cells[1], cells[2])


def local_imports(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.add(node.module.split(".")[0])
    return sorted(m for m in out if m not in STD)


def record_dir(rid7):
    c = glob.glob(os.path.join(RECORDS, rid7 + "*"))
    return c[0] if c else None


rows = []
for rid_dir in sorted(glob.glob(os.path.join(BUNDLE, "r*"))):
    if not os.path.isdir(rid_dir):
        continue
    rid = os.path.basename(rid_dir)
    rdir = record_dir(rid)
    for dp, dn, fn in os.walk(rid_dir):
        pys = {f[:-3] for f in fn if f.endswith(".py")}
        for f in fn:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, BUNDLE).replace("\\", "/")
            for m in local_imports(p):
                if m in pys or m == f[:-3]:
                    continue
                hits = []
                if rdir:
                    for dp2, _, fn2 in os.walk(rdir):
                        if m + ".py" in fn2:
                            hits.append(os.path.relpath(os.path.join(dp2, m + ".py"), rdir).replace("\\", "/"))
                src_rec, label = readme.get(rel, ("?", "?"))
                rows.append((rel, label, src_rec, m, hits))

for rel, label, src_rec, m, hits in rows:
    print(f"{rel} | 항목 {label} | 기록 위치 {src_rec} | 모듈 {m} | 기록 안: {hits if hits else '없음'}")
print(f"\n총 {len(rows)}건")
