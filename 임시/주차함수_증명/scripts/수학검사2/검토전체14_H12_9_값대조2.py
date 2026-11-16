# H12 검산 9: 5A 항목 세부 수치 대조 (둘째 묶음)
import glob, os, json, re
R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"

def g(p):
    m = glob.glob(os.path.join(R, p))
    return m[0] if m else None

def ceil_half(x): return -(-x // 2)
def qr_positions(n):
    lo = ceil_half(n - 1); return max(0, (n - 3) - lo + 1)
print("(ㄹ) 5..2000 positions:", sum(qr_positions(n) for n in range(5, 2001)), "(D: 997002)")

s = open(g("rc9aee43*/evidence/peer/output/ext-443-500.json"), encoding="utf-8").read()
i = s.find('"capacity": 500')
print("ext-443-500 k=500:", s[i:i + 600].replace("\n", " ") if i >= 0 else s[:300])
s = open(g("r690be93*/evidence/producer/certificate-check.json"), encoding="utf-8").read()
for m in re.finditer(r'"maximum_float":\s*([-0-9.e]+)', s):
    print("r690be93 maximum_float:", m.group(1))
s = open(g("r690be93*/evidence/peer/window_check.json"), encoding="utf-8").read()
print("window_check.json:", s[:700].replace("\n", " "))
for f in glob.glob(g("r690be93*/evidence/peer/kernel_sample") + "/*"):
    print("kernel_sample file:", os.path.basename(f))
    try:
        t = open(f, encoding="utf-8", errors="replace").read()
        print("   ", t[:400].replace("\n", " "))
    except Exception as e:
        print("   ERR", e)
s = open(g("r690be93*/evidence/peer/tsv_crosscheck_output.txt"), encoding="utf-8", errors="replace").read()
print("r690be93 tsv_crosscheck_output:", s[:600].replace("\n", " "))
s = open(g("r13b0b8f*/evidence/peer/tsv_crosscheck.json"), encoding="utf-8").read()
print("r13b0b8f tsv_crosscheck.json:", s[:800].replace("\n", " "))
s = open(g("r13b0b8f*/evidence/peer/laurent_series_check.json"), encoding="utf-8").read()
print("laurent_series_check:", s[:500].replace("\n", " "))
s = open(g("r19de912*/evidence/peer/cert/v2run20000-summary.json"), encoding="utf-8").read()
print("v2run20000-summary:", s[:1200].replace("\n", " "))
# 출처 절 번호 존재 확인
checks = {
    "rc9aee43": ["## 5", "## 6"], "r15df76b": ["## 3", "## 4", "## 5", "## 7"], "r19de912": ["## 3", "## 9"],
    "r6373c70": ["### 3.1"], "r59c82d7": ["## 4", "## 5", "## 6"], "r708d99c": ["### 5.1", "### 5.2", "### 5.3"],
    "r0dc57fa": ["### 10.2"], "r690be93": ["### 7.4", "## 11"], "r13b0b8f": ["## 7", "## 8"],
    "ra4c01fc": ["## 5", "### 7.1", "### 7.2", "### 8.1", "### 8.5"],
}
for rid, heads in checks.items():
    p = g(rid + "*/exposition.md")
    if not p:
        print(rid, "no exposition.md"); continue
    txt = open(p, encoding="utf-8").read()
    hs = re.findall(r"^(#{2,3} [0-9.]+)", txt, flags=re.M)
    missing = [h for h in heads if not any(x.startswith(h + " ") or x == h or x.startswith(h + ".") for x in hs)]
    print(rid, "headers:", [h for h in hs][:30], "missing:", missing)
