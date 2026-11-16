# -*- coding: utf-8 -*-
import io, re
ROOT = r"C:\math\임시\주차함수_증명"
def ctx(rel, needles, w=140):
    s = io.open(ROOT + "\\" + rel, encoding="utf-8").read()
    for nd in needles:
        for m in re.finditer(re.escape(nd), s):
            ln = s.count("\n", 0, m.start()) + 1
            print(f"[{rel} {ln}] …{s[max(0,m.start()-w):m.end()+w]}…".replace("\n", "⏎"))
        if not re.search(re.escape(nd), s):
            print(f"[{rel}] 없음: {nd}")
ctx("장부_v2.md", ["\\psi_V", "P^{\\mathrm V}_k", "n^{\\mathrm V}_k"])
ctx("장부_v2.md", ["$G$"], 60)
ctx("구조표_v2.md", ["\\le V"], 100)
ctx(r"원고_자료\README.md", ["V\\sqrt", "\\psi_V"], 120)
ctx(r"장v2\부록D_장7A.md", ["3.250", "7.808"], 300)
ctx(r"장v2\장7A.md", ["3.24", "7.80"], 250)
