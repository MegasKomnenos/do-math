# H12 검산 11: 부록 D 5B·6장 항목 자료 줄 경로와 출력값 대조
import glob, os, re, difflib
R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
art = r"원고_자료\세션_재계산"

def g(p):
    m = glob.glob(os.path.join(R, p))
    return m[0] if m else None

rec = """r8a9b11e*/evidence/peer/ul_iv.py r8a9b11e*/evidence/peer/band_iv.py r8a9b11e*/review/feedback.md
r845b205*/evidence/peer/tv_certify.py r845b205*/evidence/peer/tv_certify_out.txt r845b205*/evidence/peer/tv_stages.py r845b205*/evidence/peer/tv_stages_out.txt r845b205*/review/evidence/rv_constU.py r845b205*/review/evidence/rv_constU_out.txt
r5bbc534*/evidence/producer/code/thmD_base.py r5bbc534*/evidence/producer/out/thmD_base_L700.out r5bbc534*/evidence/peer/verify_DR_thmD.py r5bbc534*/evidence/peer/verify_DR_thmD.out
r29c10cd*/evidence/peer/code/near_window_thresholds.py r29c10cd*/evidence/peer/data/near_window_thresholds.out
r051bfe1*/evidence/peer/peer_lemmaS.py r051bfe1*/evidence/peer/peer_lemmaS.log r051bfe1*/evidence/producer/check3.py r051bfe1*/evidence/producer/check3.log""".split()
print("record missing:", [p for p in rec if not g(p)])
artp = """r8a9b11e/ul_iv_fixed.py r8a9b11e/outputs_fixed band_check/band_cells.py band_check/band_cells_CE0.tsv band_check/band_read.py band_check/band_read_out_CE0.txt band_check/band_iv.py band_check/band_iv_out_CE0.txt
theorem_U_constant/theorem_U_iv.py theorem_U_constant/theorem_U_iv_out.txt theorem_U_constant/theorem_U_iv_out_32000.txt theorem_D_base/thmD_base_iv.py theorem_D_base/thmD_base_iv_out.txt prop_W_thirteen/iv13.py prop_W_thirteen/iv13_out.txt""".split()
print("article missing:", [p for p in artp if not os.path.exists(os.path.join(art, p))])

def show(p, n=900, tail=False):
    s = open(p, encoding="utf-8", errors="replace").read()
    print("===", p, "\n", (s[-n:] if tail else s[:n]))

# ul_iv diff
a = open(g("r8a9b11e*/evidence/peer/ul_iv.py"), encoding="utf-8", errors="replace").read().splitlines()
b = open(os.path.join(art, "r8a9b11e/ul_iv_fixed.py"), encoding="utf-8", errors="replace").read().splitlines()
d = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if not l.startswith(("---", "+++"))]
print("=== ul_iv.py vs ul_iv_fixed.py diff:"); print("\n".join(d[:12]))
for f in sorted(glob.glob(os.path.join(art, "r8a9b11e/outputs_fixed/*"))):
    print("outputs_fixed:", os.path.basename(f)); show(f, 500, tail=True)
fb = open(g("r8a9b11e*/review/feedback.md"), encoding="utf-8").read()
for key in ("0.71216801", "0.70624", "1.3558", "band_iv"):
    i = fb.find(key); print("feedback.md", key, "->", fb[max(0, i - 200):i + 150].replace("\n", " ") if i >= 0 else "not found")
show(os.path.join(art, "band_check/band_read_out_CE0.txt"), 1200)
show(os.path.join(art, "band_check/band_iv_out_CE0.txt"), 900, tail=True)
show(os.path.join(art, "theorem_U_constant/theorem_U_iv_out.txt"), 1500, tail=True)
show(os.path.join(art, "theorem_U_constant/theorem_U_iv_out_32000.txt"), 700, tail=True)
show(g("r845b205*/review/evidence/rv_constU_out.txt"), 700, tail=True)
show(os.path.join(art, "theorem_D_base/thmD_base_iv_out.txt"), 1200, tail=True)
show(g("r5bbc534*/evidence/peer/verify_DR_thmD.out"), 700, tail=True)
show(os.path.join(art, "prop_W_thirteen/iv13_out.txt"), 1200, tail=True)
show(g("r29c10cd*/evidence/peer/data/near_window_thresholds.out"), 800, tail=True)
show(g("r051bfe1*/evidence/peer/peer_lemmaS.log"), 600, tail=True)
show(g("r051bfe1*/evidence/producer/check3.log"), 400, tail=True)
# 출처 절 존재
for rid, heads in {"r8a9b11e": ["### 2.6", "## 6", "### 5.1"], "r845b205": ["## 7"], "r5bbc534": ["### 4.1", "### 4.2", "## 13"], "r29c10cd": ["### 7.5"], "r051bfe1": ["### 3.5", "## 10"]}.items():
    txt = open(g(rid + "*/exposition.md"), encoding="utf-8").read()
    hs = re.findall(r"^(#{2,3} [0-9.]+)", txt, flags=re.M)
    print(rid, "missing heads:", [h for h in heads if not any(x.startswith(h + " ") or x.startswith(h + ".") or x == h for x in hs)], "| 부록 A:", "부록 A" in txt)
