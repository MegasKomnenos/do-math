import json, glob, os
d = "C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/r9e782f504fc44462b7d8c10988216622/producer"
tot_init = 0; seeds = 0; coefs = 0; n = 0; reps = {}
for k in range(2, 121):
    c = json.load(open(os.path.join(d, f"certificate-k{k}.json")))
    assert c['k'] == k
    cut, r = c['cut'], c['r']
    assert r >= cut, k
    n += 1
    tot_init += len(c['raw_initial'])
    assert len(c['raw_initial']) == r + k + 2, (k, len(c['raw_initial']), r+k+2)
    assert len(c['smoothed_initial']) == r + k + 2
    assert len(c['full_differences_initial']) == cut
    seeds += (r + k + 1) - cut
    coefs += sum(v + 1 for v in c['degrees'].values())
    assert c['all_lower_bound_coefficients_nonnegative'] and c['finite_seed_ok']
    if k in (2, 8, 34, 120): reps[k] = (cut, r)
print("n", n, "init", tot_init, "seeds", seeds, "coefs", coefs, reps)
print("lower-cone files", len(glob.glob(os.path.join(d, "lower-cone-k*-cut*.json.gz"))))
print("certificates", len(glob.glob(os.path.join(d, "certificate-k*.json"))))
