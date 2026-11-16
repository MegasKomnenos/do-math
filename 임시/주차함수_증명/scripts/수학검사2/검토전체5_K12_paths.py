# K12: check that the paths in the 자료 lines of the six appendix-D files exist (records dir and 원고_자료)
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REC = r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records"
BUN = r"C:/math/임시/주차함수_증명/원고_자료"
base = r"C:/math/임시/주차함수_증명/장v2/"
def expand(p):
    p = p.strip()
    if p.startswith("records/"): p = p[len("records/"):]
    if p.startswith("원고_자료/"):
        return [os.path.join(BUN, p[len("원고_자료/"):])]
    m = re.match(r"(r[0-9a-f]{7})[0-9a-f]*…?(/.*)?$", p)
    if m:
        ids = glob.glob(os.path.join(REC, m.group(1)+"*"))
        rest = m.group(2) or ""
        return [i+rest for i in ids] or [os.path.join(REC, p)]
    return None
for f in ("부록D_장2.md", "부록D_장3.md", "부록D_장4.md", "부록D_장5A.md", "부록D_장5B.md", "부록D_장6.md"):
    txt = open(base+f, encoding="utf-8").read()
    for m in re.finditer(r"### D\.\{\{D:([^}]+)\}\}(.*?)(?=\n### D\.|\Z)", txt, re.S):
        key, body = m.group(1), m.group(2)
        r = re.search(r"\*\*자료\.\*\*\s*(.*?)\n", body)
        if not r: print(key, ": NO 자료 LINE"); continue
        line = r.group(1)
        toks = re.findall(r"`([^`]+)`", line)
        curdir = None; missing = []
        for t in toks:
            t = t.strip()
            if " " in t and "/" not in t: continue          # commands/options
            if t.startswith("-") or t.startswith("--"): continue
            if re.match(r"^[A-Za-z_]+$", t) and "." not in t: continue   # identifiers like zeta32
            if "(" in t and "/" not in t: continue
            cands = expand(t)
            if cands is None:
                if curdir is None: continue
                if "/" in t and not t.startswith("r"):  # relative with subdir
                    cands = [os.path.join(curdir, t)]
                else:
                    cands = [os.path.join(curdir, t)]
            else:
                if any(os.path.isdir(c.rstrip("/")) for c in cands):
                    curdir = [c for c in cands if os.path.isdir(c.rstrip("/"))][0].rstrip("/")
                else:
                    curdir = os.path.dirname(cands[0])
            ok = any(os.path.exists(c.rstrip("/")) or glob.glob(c.rstrip("/")) for c in cands)
            if not ok: missing.append(t)
        if missing: print(f"{f} {key}: MISSING {missing}")
        else: print(f"{f} {key}: all {len(toks)} tokens resolved")
