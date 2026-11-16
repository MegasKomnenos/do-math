"""부록 D 열 인증 17-25행의 수치를 기록 JSON·이 글의 res JSON·로그에서 다시 읽는다."""
import json, math, glob, time
from fractions import Fraction as F
from pathlib import Path

REC = Path(r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records\rc9aee436a1c34c438719b6c5d5ed79b5\evidence")
IV = Path(r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\column_k500_iv")


def B(k):
    return (k * k + 3) // 4


def main():
    # 19행 비교 수 (직접 세기)
    d1 = sum(2 * B(k) - 2 * k for k in range(121, 161)); d2 = sum(2 * B(k) - 2 * k for k in range(161, 501))
    b1 = sum(B(k) + 1 for k in range(121, 161)); b2 = sum(B(k) + 1 for k in range(161, 501))
    print(f"직접 차분 비교 수: {d1:,} + {d2:,} (부록: 386,260 + 19,982,310) -> {d1==386260 and d2==19982310}")
    print(f"띠 비교 수: {b1:,} + {b2:,} (부록: 198,790 + 10,103,865) -> {b1==198790 and b2==10103865}")
    print("B(k)=ceil(k^2/4) == (k^2+3)//4 for k<=1000:", all(B(k) == -(-k * k // 4) for k in range(1, 1001)))
    # 기록 작성자 인증서
    cs = json.load(open(REC / 'producer/output/certificates-121-160.json'))
    print("producer: count", len(cs), "bits", {c['bits'] for c in cs}, "failures", sum(c['uncertified_count'] + c['band']['failed_count'] for c in cs))
    print("producer: worst_n==2k+1 all", all(c['worst_n'] == 2 * c['capacity'] + 1 for c in cs), "; band worst==B all", all(c['band']['worst_n'] == B(c['capacity']) for c in cs))
    bs = json.load(open(REC / 'producer/output/batch-summary.json')); print("batch-summary:", bs)
    r121 = cs[0]['radius']; x = F(*r121)
    print("k=121 radius", r121, "x=%.6f" % float(x), "c=(x*e-1)*121 = %.4f" % ((float(x) * math.e - 1) * 121))
    # 기록 검토 확장
    ext = []
    for f in ('ext-161-360.json', 'ext-361-442.json', 'ext-443-500.json'):
        ext += json.load(open(REC / 'peer/output' / f))
    print("peer ext: count", len(ext), "bits", {r['bits'] for r in ext}, "failures", sum(r['direct_failures'] + r['band_failures'] for r in ext),
          "worst==2k+1", all(r['min_relative_margin_n'] == 2 * r['capacity'] + 1 for r in ext), "band worst==B", all(r['band_min_n'] == B(r['capacity']) for r in ext))
    chunks = sorted({tuple(r['chunk']) for r in ext}); print("peer chunks:", chunks[:2], "...", chunks[-2:], "count", len(chunks), "sizes", sorted({c[1] - c[0] + 1 for c in chunks}))
    for k in (161, 500):
        r = [e for e in ext if e['capacity'] == k][0]; x = F(*r['radius'])
        print(f"k={k}: chunk {r['chunk']} radius {r['radius']} c at k = {(float(x)*math.e-1)*k:.4f}, c at kmid = {(float(x)*math.e-1)*((r['chunk'][0]+r['chunk'][1])//2):.4f}, min rel {r['min_relative_margin_float']:.4e} at n={r['min_relative_margin_n']}, R(B)-1.7={r['band_min_relative_margin_float']:.4f} -> R(B)={r['band_min_relative_margin_float']+1.7:.4f}")
    # 기록 검토 독립 재계산
    for f in ('indep-lastcar-121-140-160.json', 'indep-lastcar-128.json', 'indep-lastcar-161.json'):
        d = json.load(open(REC / 'peer/output' / f))
        for r in d['results']:
            print(f"indep {f}: k={r['k']} nmax={r['nmax']} band={r['band_start']} bits={r['bits']} radius={r['radius']} fails={r['direct_failures']}+{r['band_failures']} sec={r['seconds']:.0f}")
        print("  self_test_enclosures", d.get('self_test_enclosures'), "success", d.get('success'))
    pv = json.load(open(REC / 'producer/output/positive-columns-verification.json')); print("producer verification:", pv)
    print("6969 == 23*3*101:", 23 * 3 * 101, "; 21 == sum_{n=1..6} n:", sum(range(1, 7)))
    # 이 글의 재계산
    res = {}
    for p in glob.glob(str(IV / 'res' / 'k*.json')):
        r = json.load(open(p)); res[r['k']] = r
    ks = sorted(res)
    print("iv: columns", len(ks), ks[0], ks[-1], "bits", {res[k]['bits'] for k in ks}, "failures", sum(res[k]['direct_failures'] + res[k]['band_failures'] for k in ks))
    print("iv: worst n==2k+1 all", all(res[k]['min_rel_margin_n'] == 2 * k + 1 for k in ks), "; distinct radii", len({tuple(res[k]['radius']) for k in ks}), "; chunks", sorted({tuple(res[k]['chunk']) for k in ks})[-1])
    mr = {k: F(int(res[k]['min_rel_margin_lower'][0]), int(res[k]['min_rel_margin_lower'][1])) for k in ks}
    kmin = min(ks, key=lambda k: mr[k]); print(f"iv: min rel margin over all k: {float(mr[kmin]):.5e} at k={kmin}, n={res[kmin]['min_rel_margin_n']}")
    print("iv: ratio_lower_at_B k=151..160:", [round(res[k]['ratio_lower_at_B'], 4) for k in range(151, 161)], "k=500:", round(res[500]['ratio_lower_at_B'], 4), "k=161:", round(res[161]['ratio_lower_at_B'], 4))
    for k in (121, 495, 500):
        x = F(*res[k]['radius']); km = res[k]['kmid']
        print(f"iv: k={k} kmid={km} radius={res[k]['radius']} c formula 0.34+0.65 ln kmid = {0.34+0.65*math.log(km):.4f}; c from radius at kmid = {(float(x)*math.e-1)*km:.4f}; 2^-40 denominator: {res[k]['radius'][1]==1<<40}")
    # 기록 값과의 상대 차
    rec = {}
    for c in cs:
        a, b = c['minimum_relative_margin_interval_lower']; rec[c['capacity']] = (F(int(a), int(b)), c['worst_n'])
    for r in ext:
        a, b = r['min_relative_margin_lower']; rec[r['capacity']] = (F(int(a), int(b)), r['min_relative_margin_n'])
    diffs = {k: abs(mr[k] - rec[k][0]) / rec[k][0] for k in ks}
    kd = max(ks, key=lambda k: diffs[k])
    print(f"iv vs record: max relative difference {float(diffs[kd]):.3e} at k={kd}; same worst n: {all(res[k]['min_rel_margin_n']==rec[k][1] for k in ks)}")
    # 벽시계
    for w in (0, 1):
        lines = [json.loads(s) for s in (IV / f'run_w{w}.log').read_text(encoding='utf-8').splitlines() if s.strip()]
        st = [l for l in lines if l.get('start')][0]; fin = [l for l in lines if l.get('finished')][-1]
        print(f"worker {w}: {st['t']} -> {fin['t']}, elapsed {fin['worker_elapsed']} s = {fin['worker_elapsed']/3600:.2f} h, bits {st['bits']}, nchunks {len(st['chunks'])}")
    t0 = time.mktime(time.strptime('2026-11-13 17:55:38', '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime('2026-11-13 20:35:15', '%Y-%m-%d %H:%M:%S'))
    print(f"wall clock first start -> last finish: {(t1-t0)/3600:.2f} h")


if __name__ == '__main__':
    main()
