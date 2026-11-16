# -*- coding: utf-8 -*-
"""검토 D: _patch_README_세션파일.py의 PARAS가 README 문단과 같은지, _fix_결정96_자료.py의 15 치환이 대상에 들어 있는지."""
import ast, io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
src = io.open(os.path.join(ROOT, "scripts/_patch_README_세션파일.py"), encoding="utf-8").read()
tree = ast.parse(src)
paras = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PARAS":
        paras = ast.literal_eval(node.value)
readme = io.open(os.path.join(ROOT, "원고_자료/README.md"), encoding="utf-8").read()
print("PARAS 수", len(paras))
for key, para in paras:
    c = readme.count(para)
    flag = "OK" if c == 1 else f"!! count={c}"
    print(f"{flag:12s} {key}")
    if c != 1:
        i = readme.find(para[:40])
        if i >= 0:
            seg = readme[i:i+len(para)+200]
            k = 0
            while k < min(len(seg), len(para)) and seg[k] == para[k]:
                k += 1
            print("   첫 차이 위치", k, "PARAS:", repr(para[max(0,k-40):k+60]))
            print("                README:", repr(seg[max(0,k-40):k+60]))
fx = io.open(os.path.join(ROOT, "scripts/_fix_결정96_자료.py"), encoding="utf-8").read()
STUB = "CALLS = []\ndef sub1(path, old, new, must=True):\n    CALLS.append((path, old, new)); return 0\n\nn = 0"
fx2 = re.sub(r"def sub1\(.*?\n\nn = 0", lambda m: STUB, fx, flags=re.S).replace('print("치환", n)', "")
g = {"__file__": os.path.join(ROOT, "scripts/_fix_결정96_자료.py")}
exec(compile(fx2, "fx", "exec"), g)
calls = g["CALLS"]
print("sub1 호출 수", len(calls))
for i, (path, old, new) in enumerate(calls):
    s = io.open(os.path.join(ROOT, path), encoding="utf-8").read()
    co, cn = s.count(old), s.count(new)
    hazard = (old in new) and co == 1
    print(f"{i+1:2d} {path:40s} old={co} new={cn} {'(재실행 시 중복 위험: 앵커가 새 문자열에 포함)' if hazard else ''}")
