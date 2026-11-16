# -*- coding: utf-8 -*-
"""M11: 11.3 표의 '…의 증명을 거쳐' 주장을 (인용하는 블록, 인용되는 라벨) 쌍으로 확인한다. '…의 증명.' 분리 블록은 본 블록에 합친다."""
import re, glob, os
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()
HEAD0 = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}(의 증명)?")
blocks = {}
for f in sorted(glob.glob(os.path.join(ROOT, "장*.md"))):
    cur = None; buf = []
    def flush():
        if cur is not None: blocks[cur] = blocks.get(cur, "") + "\n" + "\n".join(buf)
    for ln in rd(f).splitlines():
        if re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln): flush(); cur = None; buf = []; continue
        m = HEAD0.match(ln)
        if m: flush(); cur = f"{m.group(2)}:{m.group(3)}"; buf = [ln]
        elif cur is not None: buf.append(ln)
    flush()
def cites(k, lab):
    t = blocks.get(k, "")
    hits = [m.start() for m in re.finditer(r"\{\{" + re.escape(lab) + r"\}\}", t)]
    out = []
    for h in hits:
        out.append(t[max(0, h-90):h+110].replace("\n", " "))
    return out
pairs = [("6:old-8-11", "5:witness-position-bound"), ("6:small-k-bulk", "5:witness-position-bound"), ("6:above-window", "5:witness-position-bound"),
         ("6:old-6-19", "6:old-8-11"), ("6:D-bound", "6:old-8-11"), ("6:V-all", "6:critical-front"), ("6:V-all", "6:prop-R"), ("6:critical-front", "6:old-8-11"), ("6:prop-R", "6:old-8-11"),
         ("6:lemma-Hprime", "2:zeta-constants"), ("8:closed-form-envelope", "2:zeta-constants"), ("8:table-tolerance", "2:zeta-constants"),
         ("8:hazard-H1", "6:old-7-24"), ("7:theorem-W", "6:old-7-24"), ("7:src-plus", "7:theorem-W"), ("6:old-7-24", "6:tilt-sum"), ("7:src-plus", "7:polar-PD"), ("7:polar-PD", "7:old-6-12"),
         ("6:old-7-21", "6:old-7-20"), ("6:tilt-split", "2:old-2-45"), ("6:path-shift", "2:old-2-45"), ("2:b-top", "2:old-2-6"), ("2:old-2-31", "2:old-2-6"),
         ("6:old-8-13", "6:same-kernel"), ("6:old-8-13", "6:stay-margin-identity"), ("6:old-8-13", "6:lemma-omega"), ("6:old-8-13", "6:lemma-phi"), ("2:old-2-46", "2:old-2-44"),
         ("7:old-6-15", "7:old-6-14"), ("7:old-6-21", "7:old-6-14"), ("5:old-5-18", "5:old-5-11"), ("5:old-5-18", "6:cor-L"), ("7:old-6-13", "4:old-4-5"),
         ("9:old-7-35", "8:old-6-28"), ("2:old-2-38", "2:old-2-35"), ("2:old-2-38", "2:old-2-36"), ("2:old-2-39", "2:old-2-38"), ("9:old-7-29", "2:old-2-39"), ("9:old-7-28", "2:old-2-38"),
         ("10:old-8-14", "6:old-8-13"), ("10:old-8-14", "6:DD-lower-bound"), ("10:old-8-31", "2:old-2-46"), ("10:families", "2:old-2-46"), ("10:bulk-majorants", "6:old-8-12"),
         ("9:old-7-16", "6:old-7-13"), ("9:old-7-16", "2:old-2-34"), ("9:regeneration-S", "2:b-top"), ("9:old-7-12", "2:b-top"), ("9:H-star-plus", "2:b-top"), ("9:old-7-6", "2:old-2-41"), ("9:old-7-38", "2:old-2-41"),
         ("10:row-3k", "7:threshold-unit-ratio"), ("10:row-3k", "6:V-all"), ("10:row-3k", "6:old-6-19"), ("10:old-8-14", "6:old-7-13"), ("10:old-8-14", "6:old-8-11"),
         ("9:old-7-37", "8:old-6-28"), ("9:psi-two-sided", "2:zeta-constants"), ("9:psi-low", "2:zeta-constants")]
for k, lab in pairs:
    cs = cites(k, lab)
    print(f"[{k} ← {lab}] {'O' if cs else 'X 인용 없음'}")
    for c in cs[:2]: print("     …", c, "…")
