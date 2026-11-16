# -*- coding: utf-8 -*-
"""ZV3 탐색: 자료 묶음 원고_자료/ 안의 모든 .py가 import하는 지역 모듈(같은 묶음 폴더의 .py)이 묶음에 있는지,
그리고 README가 정한 `python -I`(3.11+에서 -P를 함의해 스크립트 폴더를 sys.path에 넣지 않음)로 돌릴 때
그 import가 성립하는지(스크립트가 sys.path를 스스로 손보는지)를 조사한다.

출력: 모듈 이름이 (가) 표준 라이브러리/서드파티가 아니고 (나) 스크립트와 같은 폴더에 .py가 없으면 「빠짐」,
      같은 폴더에 있으나 스크립트가 sys.path를 고치지 않으면 「-I에서 경로 필요」.
사용: python -I scripts/수학검사2/검토_외부피드백_1116_ZV3_imports.py
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUNDLE = os.path.join(ROOT, "원고_자료")
STD = set(sys.stdlib_module_names) | {"numpy", "mpmath", "scipy", "sympy", "gmpy2", "matplotlib", "pandas",
                                      "flint", "cypari2", "tqdm", "numba", "mpi4py"}


def imports_of(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except SyntaxError as e:
        return None, None, f"구문 오류 {e}"
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.append(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.append(node.module.split(".")[0])
    touches_path = "sys.path" in src
    return names, touches_path, None


def main():
    rows = []
    for dp, dn, fn in os.walk(BUNDLE):
        if "_tmp" in dp or "_claims" in dp:
            continue
        pys = {f[:-3] for f in fn if f.endswith(".py")}
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            names, tp, err = imports_of(p)
            rel = os.path.relpath(p, BUNDLE).replace("\\", "/")
            if err:
                rows.append((rel, "", err))
                continue
            for m in sorted(set(names)):
                if m in STD or m == f[:-3]:
                    continue
                if m in pys:
                    if not tp:
                        rows.append((rel, m, "같은 폴더에 있음; sys.path 손보지 않음 → `python -I`로는 ModuleNotFoundError"))
                else:
                    # 묶음 어딘가에 있는지
                    found = []
                    for dp2, _, fn2 in os.walk(BUNDLE):
                        if m + ".py" in fn2:
                            found.append(os.path.relpath(os.path.join(dp2, m + ".py"), BUNDLE).replace("\\", "/"))
                    rows.append((rel, m, "빠짐(같은 폴더에 없음)" + (f"; 묶음의 다른 곳: {found}" if found else "; 묶음 어디에도 없음")))
    for r in rows:
        print(" | ".join(r))
    print(f"\n총 {len(rows)}건")


if __name__ == "__main__":
    main()
