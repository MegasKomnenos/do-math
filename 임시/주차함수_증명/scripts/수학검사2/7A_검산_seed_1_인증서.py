"""부록 D 씨앗 인증서(31-49행)를 119개 인증서·audit.json·코드와 대조한다.

- 키 존재, cut/r/buffer 관계(r>=cut, buffer==2k, cut 공식), 배열 길이(r+k+2, cut),
- 씨앗 구간 [cut, r+k] 의 smoothed>=0, smoothed[cut]>0, 대표값·구간,
- 계수 총수 116,128(degrees 합), 씨앗 49,372(저장 배열 길이 합),
- tau_k <= max(16,2k-1) (직접 비교 범위 max(16,2k-1)<=n<cut 의 d>0),
- 갱신 재귀 Q~_n = Q_n + sum_{j<=min(n,k+1)} C(n,j)(j-1)^{j-1} Q~_{n-j} 가 raw->smoothed 를 재현하는지(119개 전부),
- k=2,8 에서 X_k 의 계수 n![x^n]X 를 정의(1-C_y = 1/A_{y-1})에서 Fraction 으로 직접 계산해 raw_initial 과 대조,
- d_{142,120}, d_{143,120} 정확 정수, 2k-1=239,
- k<=ceil(n/2) <=> n>=2k-1.
"""
import json, sys
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path

sys.set_int_max_str_digits(0)
REC = Path(r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records\r9e782f504fc44462b7d8c10988216622")


def lastcar(y, nmax):
    a = [1]
    for n in range(1, nmax + 1):
        a.append(sum(comb(n - 1, j) * min(j + 1, y) * a[j] * a[n - 1 - j] for j in range(n)))
    return a


def ser_mul(a, b, L):
    c = [F(0)] * L
    for i, x in enumerate(a[:L]):
        if x:
            for j, y in enumerate(b[:L - i]):
                c[i + j] += x * y
    return c


def ser_inv(a, L):  # a[0]=1
    b = [F(0)] * L; b[0] = F(1)
    for n in range(1, L):
        b[n] = -sum(a[j] * b[n - j] for j in range(1, min(n, len(a) - 1) + 1))
    return b


def X_coeffs(k, cut, L):
    A = {c: lastcar(c, L) for c in (k - 1, k, k + 1)}
    oneminusC = {c: ser_inv([F(A[c][n], factorial(n)) for n in range(L)], L) for c in (k - 1, k, k + 1)}  # 1-C_c = 1/A_{c-1}
    d = [A[k + 1][n] - 2 * A[k][n] + A[k - 1][n] for n in range(L)]
    Y = [F(d[n], factorial(n)) if n < cut else F(0) for n in range(L)]
    m, z, p = oneminusC[k - 1], oneminusC[k], oneminusC[k + 1]
    X = [u - 2 * v + w - t for u, v, w, t in zip(ser_mul(m, z, L), ser_mul(m, p, L), ser_mul(z, p, L), ser_mul(Y, ser_mul(ser_mul(m, z, L), p, L), L))]
    out = []
    for n in range(L):
        v = X[n] * factorial(n); assert v.denominator == 1; out.append(int(v))
    return out


def main():
    keys_needed = ['cut', 'r', 'buffer', 'dropped_nonnegative_tails', 'all_lower_bound_coefficients_nonnegative', 'finite_seed_ok', 'smoothed_initial', 'raw_initial', 'full_differences_initial']
    audit = json.load(open(REC / 'peer/audit.json'))
    tau = {row['k']: row['threshold'] for row in audit['capacities']}
    total_coef = 0; total_seed = 0; probs = []
    rec_ok = True
    for k in range(2, 121):
        c = json.load(open(REC / f'producer/certificate-k{k}.json'))
        for key in keys_needed:
            if key not in c: probs.append((k, 'missing key', key))
        cut, r, buf = c['cut'], c['r'], c['buffer']
        raw = list(map(int, c['raw_initial'])); s = list(map(int, c['smoothed_initial'])); d = list(map(int, c['full_differences_initial']))
        exp_cut = 2 * k if k >= 18 else (3 * k if k >= 8 else 3 * k + 2)
        if cut != exp_cut: probs.append((k, 'cut', cut, exp_cut))
        if not (r >= cut): probs.append((k, 'r<cut', r, cut))
        if buf != 2 * k: probs.append((k, 'buffer!=2k', buf))
        if not (len(raw) == len(s) == r + k + 2): probs.append((k, 'len', len(raw), len(s), r + k + 2))
        if len(d) != cut: probs.append((k, 'len d', len(d), cut))
        if not (all(v == 0 for v in s[:cut]) and s[cut] > 0 and all(v >= 0 for v in s[cut:r + k + 1])): probs.append((k, 'seed'))
        if not all(v == 0 for v in raw[:cut]): probs.append((k, 'raw prefix'))
        if not c['finite_seed_ok'] or not c['all_lower_bound_coefficients_nonnegative']: probs.append((k, 'flags'))
        if len(c['dropped_nonnegative_tails']) != r: probs.append((k, 'drops len'))
        tgt = max(16, 2 * k - 1)
        if not all(v > 0 for v in d[tgt:cut]): probs.append((k, 'd>0 on [max(16,2k-1),cut)'))
        if not (tau[k] <= tgt): probs.append((k, 'tau>target', tau[k], tgt))
        if not (all(v == 0 for v in d[:k]) and all(v < 0 for v in d[k:tau[k]]) and all(v > 0 for v in d[tau[k]:cut])): probs.append((k, 'sign pattern'))
        total_coef += sum(v + 1 for v in c['degrees'].values()); total_seed += len(s)
        # 갱신 재귀 재현
        V = [0] + [(j - 1) ** (j - 1) for j in range(1, k + 2)]
        st = []
        for n in range(len(raw)):
            st.append(raw[n] + sum(comb(n, j) * V[j] * st[n - j] for j in range(1, min(n, k + 1) + 1)))
        if st != s: rec_ok = False; probs.append((k, 'recurrence raw->smoothed mismatch'))
        if k in (2, 8, 34, 120):
            print(f"k={k}: cut={cut} r={r} buffer={buf} states={len(c['degrees'])} seed range checked [{cut},{r+k}] (len {r+k+1-cut}), stored len {len(s)}, tau={tau[k]}, target={tgt}, s[cut]={s[cut]}")
    print("problems:", probs if probs else "none")
    print("recurrence Q~ reproduces smoothed_initial for all 119:", rec_ok)
    print("total final coefficients (sum deg+1):", total_coef, "(부록 116,128; audit", audit['final_polynomial_coefficients'], ")")
    print("total stored seed entries (sum r+k+2):", total_seed, "(부록 49,372; audit", audit['seed_coefficients'], ")")
    print("sum over k of (r+k+1-cut) [checked seed positions]:", sum(json.load(open(REC / f'producer/certificate-k{k}.json'))['r'] + k + 1 - json.load(open(REC / f'producer/certificate-k{k}.json'))['cut'] for k in range(2, 121)))
    print("max tau:", max(tau.values()), "tau nondecreasing:", all(tau[k] <= tau[k + 1] for k in range(2, 120)))
    print("certificate files:", len(list((REC / 'producer').glob('certificate-k*.json'))), "lower-cone files:", len(list((REC / 'producer').glob('lower-cone-*.json.gz'))))
    # X_k 계수 직접 계산 vs raw_initial
    for k in (2, 8):
        c = json.load(open(REC / f'producer/certificate-k{k}.json')); raw = list(map(int, c['raw_initial']))
        X = X_coeffs(k, c['cut'], len(raw))
        print(f"k={k}: n![x^n]X_cut from definition == raw_initial ({len(raw)} entries): {X == raw}")
    # d_{142,120}, d_{143,120}
    A = {c: lastcar(c, 143) for c in (119, 120, 121)}
    for n in (142, 143, 239, ):
        if n <= 143:
            dn = A[121][n] - 2 * A[120][n] + A[119][n]
            print(f"d_{{{n},120}} sign: {'negative' if dn < 0 else 'positive'}; digits {len(str(abs(dn)))}; matches audit witness: {str(dn) == audit['witnesses'][f'{n},120']['difference']}")
    print("2k-1 for k=120:", 2 * 120 - 1, "; 142 < 239:", 142 < 239)
    print("k<=ceil(n/2) <=> n>=2k-1 for n<=400,k<=200:", all((k <= -(-n // 2)) == (n >= 2 * k - 1) for n in range(1, 401) for k in range(1, 201)))
    print("(n-1)/2 > 1 <=> n>=4 for n<=100:", all(((n - 1) / 2 > 1) == (n >= 4) for n in range(1, 101)))


if __name__ == '__main__':
    main()
