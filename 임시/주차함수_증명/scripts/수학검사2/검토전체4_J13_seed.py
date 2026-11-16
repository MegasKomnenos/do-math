import json, glob, os, sys
R = r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/r9e782f504fc44462b7d8c10988216622/producer"
files = sorted(glob.glob(os.path.join(R, "certificate-k*.json")), key=lambda p: int(os.path.basename(p)[13:-5]))
print("n certs", len(files))
d0 = json.load(open(files[0]))
print("keys", list(d0.keys()))
tot_coef = 0; tot_seed = 0; tot_init = 0
for p in files:
    d = json.load(open(p)); k = d.get("k")
    cut = d.get("cut"); r = d.get("r")
    if k in (2, 8, 34, 120):
        print(k, "cut", cut, "r", r, "buffer", d.get("buffer"), "seed range", cut, r + k)
        print("   flags", d.get("all_lower_bound_coefficients_nonnegative"), d.get("finite_seed_ok"))
        for key in ("smoothed_initial", "raw_initial", "full_differences_initial", "dropped_nonnegative_tails", "lower_bound_coefficients", "lower_bound"):
            v = d.get(key)
            if v is not None:
                print("   ", key, type(v).__name__, (len(v) if hasattr(v, "__len__") else v))
    # counts
    lb = d.get("lower_bound_coefficients") or d.get("lower_bound") or d.get("final_lower_bound")
    if isinstance(lb, dict):
        tot_coef += sum(len(v) for v in lb.values())
    elif isinstance(lb, list):
        tot_coef += sum(len(v) if isinstance(v, list) else 1 for v in lb)
    si = d.get("smoothed_initial")
    if isinstance(si, list):
        tot_init += len(si)
        tot_seed += sum(1 for i, _ in enumerate(si) if cut <= i < r + k + 1)
    elif isinstance(si, dict):
        tot_init += len(si)
        tot_seed += sum(1 for i in si if cut <= int(i) < r + k + 1)
print("total lower-bound coefficients", tot_coef, "seeds in range", tot_seed, "stored initial", tot_init)
# k=120 negatives
d = json.load(open(os.path.join(R, "certificate-k120.json")))
fd = d.get("full_differences_initial")
if isinstance(fd, list):
    neg = [i for i, v in enumerate(fd) if (int(v) if not isinstance(v, (int,)) else v) < 0]
elif isinstance(fd, dict):
    neg = sorted(int(i) for i, v in fd.items() if int(v) < 0)
print("k=120 negative n:", neg[:5], "...", neg[-5:] if neg else None, "count", len(neg) if neg else 0)
