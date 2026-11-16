# -*- coding: utf-8 -*-
"""검토 D: 세 치환 스크립트(용어 41, fix2, fix)의 EDITS가 현재 파일에 적용돼 있는지(new 존재·old 부재)."""
import ast, io, os, sys
ROOT = r"C:\math\임시\주차함수_증명"
def load_edits(path):
    src = io.open(os.path.join(ROOT, path), encoding="utf-8").read()
    tree = ast.parse(src)
    g = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("EDITS", "ROOT", "S", "D"):
            try:
                g[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    if "EDITS" not in g:
        # 변수 참조가 섞인 경우: 모듈을 실행하지 않고 간단 평가
        ns = {"__file__": os.path.join(ROOT, path)}
        code = src.split("\nfor rel, old, new in EDITS")[0]
        exec(compile(code, path, "exec"), ns)
        g["EDITS"] = ns["EDITS"]
    return g["EDITS"]
for sp in ["scripts/_fix_결정96_용어.py", "scripts/수학검사2/피드백_1114b_fix2.py", "scripts/수학검사2/피드백_1114b_fix.py"]:
    E = load_edits(sp)
    print("==", sp, "EDITS", len(E))
    bad = 0
    cache = {}
    for i, (rel, old, new) in enumerate(E):
        p = os.path.join(ROOT, rel)
        if rel not in cache:
            cache[rel] = io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
        s = cache[rel]
        if s is None:
            print(f"  {i+1:2d} 파일 없음 {rel}"); bad += 1; continue
        co, cn = s.count(old), s.count(new)
        ok = (cn >= 1 and (co == 0 or old in new))
        if not ok:
            bad += 1
            print(f"  {i+1:2d} !! {rel} old={co} new={cn} | old[:50]={old[:50]!r}")
    print("  문제", bad)
