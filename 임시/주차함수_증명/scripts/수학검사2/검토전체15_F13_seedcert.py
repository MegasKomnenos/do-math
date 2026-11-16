# F13: D.seed-certificates-k120 의 수치(대표값·개수) 검산 — 기록 인증서 JSON 판독
import json, glob, gzip, os
base = '원고_자료/r9e782f5/producer'
fs = sorted(glob.glob(base + '/certificate-k*.json'), key=lambda p: int(p.split('-k')[1].split('.')[0]))
print('certs', len(fs))
tot_q = tot_init = tot_coef = 0
reps = {}
bad = []
for f in fs:
    d = json.load(open(f))
    k, cut, r = d['k'], d['cut'], d['r']
    lo, hi = cut, r + k + 1  # check interval [cut, r+k+1)
    tot_q += hi - lo
    tot_init += len(d['smoothed_initial'])
    if len(d['smoothed_initial']) != r + k + 2: bad.append(('init_len', k, len(d['smoothed_initial']), r+k+2))
    if not d['all_lower_bound_coefficients_nonnegative'] or not d['finite_seed_ok']: bad.append(('flag', k))
    # count lower-bound coefficients from degrees? use gz file
    gz = os.path.join(base, d['polynomials_gzip'])
    if os.path.exists(gz):
        P = json.load(gzip.open(gz))
        if isinstance(P, dict):
            # try to find coefficient lists
            n = 0
            def walk(o):
                global n
                if isinstance(o, dict):
                    for v in o.values(): walk(v)
                elif isinstance(o, list):
                    if o and all(isinstance(x,(str,int,float)) for x in o): n += len(o)
                    else:
                        for v in o: walk(v)
            walk(P)
            tot_coef += n
    if k in (2, 8, 34, 120): reps[k] = (cut, r, lo, hi-1)
    # direct comparisons: full_differences_initial length cut; positivity from max(16,2k-1)
    fd = d['full_differences_initial']
    if len(fd) != cut: bad.append(('fd_len', k, len(fd), cut))
    start = max(16, 2*k-1)
    for n in range(start, cut):
        if int(fd[n]) <= 0: bad.append(('fd_nonpos', k, n))
    if k == 120:
        neg = [n for n in range(cut) if int(fd[n]) < 0]
        print('k=120 negative n:', neg[:3], '...', neg[-3:], 'count', len(neg))
        print('k=120 smoothed_initial at cut:', d['smoothed_initial'][cut][:40] if isinstance(d['smoothed_initial'][cut], str) else d['smoothed_initial'][cut])
print('reps', reps)
print('total Q~ values in check intervals', tot_q)
print('total stored initial', tot_init)
print('total lower-bound coefficients (gz walk)', tot_coef)
print('bad', bad[:10], len(bad))
