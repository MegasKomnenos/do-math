# -*- coding: utf-8 -*-
"""검토 C: 조립본 원고.md의 「상한」「하한」「사슬」 자리 추출(문맥), 용어 치환 스크립트 EDITS 수·적용 여부 점검."""
import io, os, re, sys, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")
s = io.open(os.path.join(ROOT, "원고.md"), encoding="utf-8").read()
lines = s.split("\n")
def show(pat, width=45):
    n = 0
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(pat, ln):
            n += 1
            a = max(0, m.start()-width); b = min(len(ln), m.end()+width)
            print(f"{i}: …{ln[a:b]}…")
    print(f"[{pat}] 총 {n}곳\n")
show("상한")
show("하한")
show("사슬", 30)
# 치환 스크립트 EDITS 점검
spec = importlib.util.spec_from_file_location("fx", os.path.join(ROOT, "scripts", "_fix_결정96_용어.py"))
src = io.open(os.path.join(ROOT, "scripts", "_fix_결정96_용어.py"), encoding="utf-8").read()
# EDITS 리스트만 평가
ns = {}
exec(src[src.index("EDITS = ["):src.index("\nn = 0")], ns)
E = ns["EDITS"]
print("EDITS 쌍 수:", len(E))
for rel, old, new in E:
    t = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    co, cn = t.count(old), t.count(new)
    flag = "OK" if (co == 0 and cn >= 1) else "??"
    print(flag, rel, "old=%d new=%d" % (co, cn), new[:50].replace("\n", "/"))
