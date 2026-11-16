# H12 검산 8: 부록 D 5A 항목의 세부 수치를 기록·자료 묶음의 요약 파일과 대조
import glob, os, json, re
R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
art = r"원고_자료\세션_재계산"

def g(p):
    m = glob.glob(os.path.join(R, p))
    return m[0] if m else None

print("=== r13b0b8f producer tree (missing files?)")
for root, dirs, files in os.walk(g("r13b0b8f*/evidence/producer")):
    for f in files:
        print("  ", os.path.relpath(os.path.join(root, f), g("r13b0b8f*")))
print("=== r13b0b8f review tree")
for root, dirs, files in os.walk(g("r13b0b8f*/review")):
    for f in files:
        print("  ", os.path.relpath(os.path.join(root, f), g("r13b0b8f*")))

print("=== c20_summary.json")
print(open(os.path.join(art, "c50_iv/runs/c20_summary.json"), encoding="utf-8").read()[:1200])
print("=== record ext50000_summary.json")
print(open(g("r59c82d7*/evidence/runs/ext50000_summary.json"), encoding="utf-8").read()[:1200])
tot = 0
for f in glob.glob(os.path.join(art, "c50_iv/runs/*probe*undercount*.txt")):
    s = open(f, encoding="utf-8", errors="replace").read()
    m = re.search(r'"records_checked"\s*:\s*(\d+)', s) or re.search(r'"records"\s*:\s*(\d+)', s) or re.search(r'"dump_records"\s*:\s*(\d+)', s)
    if m:
        tot += int(m.group(1))
    else:
        print("  probe file no count:", os.path.basename(f), s[:200].replace("\n", " "))
print("probe records total:", tot, "(D: 56152)")
print("=== critical window summary rows A18..end + totals")
s = open(os.path.join(art, "critical_window_rerun/summary_out.txt"), encoding="utf-8").read()
i = s.find("| A18")
print(s[i:i + 4000])
print("=== left_columns summary: k=120 entry")
j = json.load(open(os.path.join(art, "left_columns_k2_120/summary.json"), encoding="utf-8"))
for row in j["table"]:
    if row["k"] in (120, 6):
        print("  k", row["k"], "start", row["start"], "worst_n", row["worst_n"], "min_rel_margin", row["min_relative_margin"])
print("=== record certificates-121-160.json (k=121 margin)")
c = json.load(open(g("rc9aee43*/evidence/producer/output/certificates-121-160.json"), encoding="utf-8"))
sc = json.dumps(c)
for key in ("1.54", "243", "min_relative_margin", "min_margin"):
    k_ = sc.find(key)
    if k_ >= 0:
        print("  ...", sc[max(0, k_ - 200):k_ + 200].replace("\n", " "))
        break
print("=== summary-all.json")
sa = open(g("rc9aee43*/evidence/peer/output/summary-all.json"), encoding="utf-8").read()
for key in ("1.38", "2.255", "9999"):
    k_ = sa.find(key)
    print("  ", key, "->", sa[max(0, k_ - 250):k_ + 150].replace("\n", " ") if k_ >= 0 else "not found")
print("=== r15df76b compare_runs.json")
cr = open(g("r15df76b*/evidence/peer/checks/compare_runs.json"), encoding="utf-8").read()
print(cr[:1500])
for key in ("2.636", "2.638", "1.13"):
    k_ = cr.find(key)
    print("  ", key, "->", cr[max(0, k_ - 200):k_ + 120].replace("\n", " ") if k_ >= 0 else "not found")
print("=== r0dc57fa t1_check_out.json")
print(open(g("r0dc57fa*/review/evidence/t1_check_out.json"), encoding="utf-8").read()[:800])
print("=== r13b0b8f rerun_summary.json")
print(open(g("r13b0b8f*/review/reruns/rerun_summary.json"), encoding="utf-8").read()[:1200])
print("=== r708d99c cert_newton_summary.json")
print(open(g("r708d99c*/evidence/peer/cert_newton_summary.json"), encoding="utf-8").read()[:900])
print("=== r690be93 certificate-check.json")
print(open(g("r690be93*/evidence/producer/certificate-check.json"), encoding="utf-8").read()[:900])
