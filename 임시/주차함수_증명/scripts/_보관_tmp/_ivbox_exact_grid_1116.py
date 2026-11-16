# -*- coding: utf-8 -*-
"""ivbox_lib.py: 저장된 봉투 표 hat T를 저장 binary64 좌표(qenv_fix_x.npy)가 아니라 본문의 정확한 점 xi_j = j/2000 위의
선형 보간으로 읽게 바꾼다(9차 Z8-2·S-1 (ㄱ)). 값 z_j는 그대로 qenv_fix_v.npy. 2026-11-16."""
import io
p = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\bprime_boxes\ivbox_lib.py"
s = io.open(p, encoding="utf-8").read()
a = s.index("# ---------- stored table hat T ----------")
b = s.index("# ---------- test function Omega ----------")
new_block = '''# ---------- stored table hat T ----------
# 2026-11-16 (9th review, Z8-2 / session S-1): hat T is the piecewise-linear interpolant of the stored values z_j
# (qenv_fix_v.npy) placed at the EXACT points xi_j = j/2000, j = 0..12000 (the text's definition; Lemma
# table-tolerance, D.stored-table-check), constant z_12000 for x >= 6.  Before this change the nodes were the stored
# binary64 coordinates qenv_fix_x.npy (= np.linspace(0, 6.0005, 12002)[:12001]), which differ from j/2000 by <= 1 ulp.
qv = np.load(os.path.join(WORK, 'qenv_fix_v.npy'))
_NQ = len(qv)
assert _NQ == 12001 and np.all(np.diff(qv) < 0)
_qx_stored = np.load(os.path.join(WORK, 'qenv_fix_x.npy'))
assert len(_qx_stored) == _NQ and all(abs(Fr(_qx_stored[j]) - Fr(j, 2000)) <= Fr(1, 2**40) for j in range(_NQ))
qx_lo = np.array([f_dn(Fr(j, 2000)) for j in range(_NQ)])      # binary64 <= xi_j
qx_hi = np.array([f_up(Fr(j, 2000)) for j in range(_NQ)])      # binary64 >= xi_j
qx = qx_lo                                                       # kept for callers that only need approximate nodes
# s_up[j] >= (z_j - z_{j+1}) / (xi_{j+1} - xi_j) = 2000 (z_j - z_{j+1}), exact rationals rounded up
_sT = np.array([f_up(2000 * (Fr(qv[j]) - Fr(qv[j + 1]))) for j in range(_NQ - 1)])


def T_lo(x):
    """lower bound of hat T(x') for every x' <= x  (x: float array >= 0 that is an UPPER bound of the argument);
    hat T is non-increasing, so hat T(x') >= hat T(x).  Nodes are the exact points xi_j = j/2000."""
    x = np.asarray(x, dtype=float)
    j = np.searchsorted(qx_hi, x, side='right') - 1              # qx_hi[j] <= x  =>  xi_j <= x
    j = np.clip(j, 0, _NQ - 1)
    last = j >= _NQ - 1                                           # x >= xi_12000 = 6: hat T == z_12000
    jj = np.minimum(j, _NQ - 2)
    # segment j is certain when x <= qx_lo[j+1] <= xi_{j+1}; otherwise x may already lie in segment j+1
    sure = x <= qx_lo[jj + 1]
    d = np.maximum(up(x - qx_lo[jj]), 0.0)                        # >= x - xi_j
    val = np.maximum(dn(qv[jj] - up(_sT[jj] * d)), qv[jj + 1])
    # bound valid whether x is in segment j or j+1: z_{j+1} - s_up[j+1] (x - xi_{j+1})_+
    j2 = np.minimum(jj + 1, _NQ - 2)
    d2 = np.maximum(up(x - qx_lo[j2]), 0.0)
    val2 = dn(qv[j2] - up(_sT[j2] * d2))
    val = np.where(sure, val, val2)
    return np.where(last, qv[-1], val)


'''
s = s[:a] + new_block + s[b:]
# header comment
old_hdr = ("#   * hat T (stored envelope table): the continuous piecewise-linear interpolant of (qx_i, qv_i) =\n"
           "#     (qenv_fix_x.npy, qenv_fix_v.npy), constant qv_12000 for x >= 6 (np.interp semantics).  Its lower-bound\n"
           "#     property is Lemma table-tolerance (D.stored-table-check, directed-rounding interval).")
new_hdr = ("#   * hat T (stored envelope table): the continuous piecewise-linear interpolant of the stored values qv_i\n"
           "#     (qenv_fix_v.npy) at the exact points xi_i = i/2000 (2026-11-16; before: the stored binary64 coordinates\n"
           "#     qenv_fix_x.npy), constant qv_12000 for x >= 6.  Its lower-bound property is Lemma table-tolerance\n"
           "#     (D.stored-table-check, directed-rounding interval).")
assert s.count(old_hdr) == 1
s = s.replace(old_hdr, new_hdr)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
