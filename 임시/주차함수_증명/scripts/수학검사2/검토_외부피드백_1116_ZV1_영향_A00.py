# -*- coding: utf-8 -*-
"""F6 수정의 영향(상자 A00): 고치기 전(rig_ray4_v1_bug)과 고친 뒤(rig_ray4)의 RayTable4 를 같은 상자에서 만들어
중점값 q_u, 상자 크기 상계 |q_u|,|q_uu|,|q_u'| 와 hatZ 도함수 포위, 그리고 eval_sig 가 주는 I 의 포위를 견준다. python -I 로 실행(수 분)."""
import sys, time
HERE = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\critical_window_rerun"
sys.path.insert(0, HERE)
import mpmath
from rig_common import iv
import rig_ray4_v1_bug as OLD
import rig_ray4 as NEW
from boxes import all_boxes
name, ua, ub_ = all_boxes()[0]
U = iv.mpf([ua, ub_])
print('box', name, 'u in', mpmath.nstr(ua, 10), mpmath.nstr(ub_, 10))
def mid(c): return complex(float(mpmath.mpf(c.real.mid)), float(mpmath.mpf(c.imag.mid)))
def wid(c): return float(mpmath.mpf(c.real.delta.a)) + float(mpmath.mpf(c.imag.delta.a))
# hatZ derivatives at the midpoint and over the box
um = (U.a + U.b) / 2; Um = iv.mpf([um, um])
print('\nhatZ_derivs: midpoint values (new - old) and box magnitude bounds (new/old)')
for sig in (0.5, 1, 2, 3, 4, 5, 6):
    s = iv.mpf(sig)
    Zo, Zuo, Zuuo = OLD.hatZ_derivs(s, Um); Zn, Zun, Zuun = NEW.hatZ_derivs(s, Um)
    _, Zub_o, Zuub_o = OLD.hatZ_derivs(s, U); _, Zub_n, Zuub_n = NEW.hatZ_derivs(s, U)
    print(f"  sig'={sig}: |Zu| {abs(mid(Zun)):.4g}  dZu {abs(mid(Zun)-mid(Zuo)):.3e} (rel {abs(mid(Zun)-mid(Zuo))/abs(mid(Zun)):.2e});  |Zuu| {abs(mid(Zuun)):.4g}  dZuu {abs(mid(Zuun)-mid(Zuuo)):.3e} (rel {abs(mid(Zuun)-mid(Zuuo))/abs(mid(Zuun)):.2e});"
          f"  aZu new/old {float(mpmath.mpf(abs(Zub_n).b))/float(mpmath.mpf(abs(Zub_o).b)):.6f}  aZuu new/old {float(mpmath.mpf(abs(Zuub_n).b))/float(mpmath.mpf(abs(Zuub_o).b)):.6f}")
t0 = time.time(); rto = OLD.RayTable4(U); print('\nold table built %.0fs' % (time.time() - t0), flush=True)
t0 = time.time(); rtn = NEW.RayTable4(U); print('new table built %.0fs' % (time.time() - t0), flush=True)
import math
mx = [0.0] * 4; rat = {'aqu': (1e9, 0), 'aquu': (1e9, 0), 'aqu1': (1e9, 0)}
for k in range(rtn.n):
    d = abs(mid(rtn.qum[k]) - mid(rto.qum[k])); mx[0] = max(mx[0], d); mx[1] = max(mx[1], d / max(abs(mid(rtn.qum[k])), 1e-300))
    for nm in rat:
        a = float(mpmath.mpf(getattr(rtn, nm)[k])); b = float(mpmath.mpf(getattr(rto, nm)[k]))
        r = a / b if b > 0 else 1.0
        rat[nm] = (min(rat[nm][0], r), max(rat[nm][1], r))
print('midpoint q_u: max |new-old| %.3e, max relative %.3e' % (mx[0], mx[1]))
for nm in rat: print('  %s new/old over the 300 cells: min %.6f max %.6f' % (nm, rat[nm][0], rat[nm][1]))
print('unchanged (should be identical): Nm, qm, aN, aq1:', all(mid(rtn.qm[k]) == mid(rto.qm[k]) for k in range(rtn.n)), all(float(mpmath.mpf(rtn.aN[k])) == float(mpmath.mpf(rto.aN[k])) for k in range(rtn.n)))
print('\neval_sig (regime T, D-form): enclosure of I(u; sigma\') over the box; point sigma\' and cell [sigma\', sigma\'+1/80]')
for sig in (0.5, 1, 2, 3, 4, 5, 6):
    for lab, s in (('point', iv.mpf(sig)), ('cell ', iv.mpf([sig, sig + mpmath.mpf(1) / 80]))):
        Io, I1o, I2o = rto.eval_sig(s); In, I1n, I2n = rtn.eval_sig(s)
        print(f"  sig'={sig} {lab}: |I| {abs(mid(In)):.5g}  mid shift {abs(mid(In)-mid(Io)):.3e}  width old {wid(Io):.3e} new {wid(In):.3e}  (rel shift {abs(mid(In)-mid(Io))/abs(mid(In)):.2e}, rel width change {(wid(In)-wid(Io))/wid(Io):+.2e});"
              f"  I1 new/old {float(mpmath.mpf(I1n))/float(mpmath.mpf(I1o)):.6f}  I2 new/old {float(mpmath.mpf(I2n))/float(mpmath.mpf(I2o)):.6f}")
    if hasattr(rtn, 'diag'):
        dn = rtn.diag; do = rto.diag
        ub = lambda x: float(mpmath.mpf(x.b)) if hasattr(x, 'b') else float(mpmath.mpf(x))
        print(f"      diag(point): rem old {ub(do['rem']):.3e} new {ub(dn['rem']):.3e};  err1 old {ub(do['err1']):.3e} new {ub(dn['err1']):.3e};  |Fp| mid shift {abs(mid(dn['Fp'])-mid(do['Fp'])):.3e} of {abs(mid(dn['Fp'])):.4g}")
