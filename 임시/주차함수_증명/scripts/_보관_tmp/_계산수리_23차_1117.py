# -*- coding: utf-8 -*-
"""23차 세션 몫 계산 수정(2026-11-17 23:3x) — ZD2 인계 「세션」 1·2·6·7(나)·8, R12 5절 2, Z10 인계 「세션」 3.
(1) check_table_iv.py 이음새 두 줄(결정 [8-2]) + docstring 한 구절.  (2) 재계산 스크립트 머리 주석의 옛 식 번호·옛 장 번호.
(3) README 461행 Fritsch–Carlson, 477·483행 「작업자」→「프로세스」.  (4) _gen_재실행표.py CONFIG(stored-table-check expect; 「작업자」 셋), _patch_README_세션파일.py PARAS.
재실행(check_table_iv·families_iv)·README SHA·자료 묶음은 이 스크립트 뒤 셸에서."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(ROOT, "원고_자료", "세션_재계산")
def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def sub(s, a, b, n=1):
    c = s.count(a); assert c == n, (a[:60], c, n); return s.replace(a, b)

# (1) check_table_iv.py
p = os.path.join(S, "window_mass_env", "check_table_iv.py"); s = rd(p)
s = sub(s, "또 저장값의 엄격 감소와 최소 감소량을 정확한 유리수로 확인한다.",
        "또 저장값의 엄격 감소와 최소 감소량을 정확한 유리수로 확인하고, 이음새의 두 부등식(정리 closed-form-envelope (라))도 두 점 xi=2, 2.1 의 성분 구간으로 판정한다.")
seam = r'''# 이음새(정리 closed-form-envelope (라)): xi = 2 (i = 3999), xi = 2.1 (i = 4199) 에서 두 성분의 구간을 진술의 네 소수와 비교한다
def _seam(i):
    c = dict(components(i))
    return c["J"], c["G"]
def _fmt(x):
    return f"[{mp.nstr(mp.mpf(x.a), 16)}, {mp.nstr(mp.mpf(x.b), 16)}]"
J2, G2 = _seam(3999)
J21, G21 = _seam(4199)
d = iv.mpf
ok2 = bool(G2.b <= d("0.213721").a and d("0.213721").b < d("0.222127").a and d("0.222127").b <= J2.a)
ok21 = bool(G21.a >= d("0.200904").b and d("0.200904").a > d("0.198148").b and d("0.198148").a >= J21.b)
print(f"seam xi=2  : Esc_6600 in {_fmt(G2)} <= 0.213721 < 0.222127 <= exp(-j_inf) in {_fmt(J2)}: {ok2}")
print(f"seam xi=2.1: Esc_6600 in {_fmt(G21)} >= 0.200904 > 0.198148 >= exp(-j_inf) in {_fmt(J21)}: {ok21}")
'''
s = sub(s, 'print(f"time {time.time()-t0:.1f}s")', seam + 'print(f"time {time.time()-t0:.1f}s")')
wr(p, s)

# (2) 옛 식 번호·옛 장 번호
p = os.path.join(S, "window_mass_env", "cert_Cb_iv.py"); s = rd(p); s = sub(s, "(8.23)", "(8.17)", 2); wr(p, s)
p = os.path.join(S, "window_mass_env", "cert_interval_iv.py"); s = rd(p); s = sub(s, "(8.25)·(8.26)", "(8.19)·(8.20)"); wr(p, s)
p = os.path.join(S, "band_boxes", "band_iv.py"); s = rd(p); s = sub(s, "the function (8.30)", "the function (8.23)"); wr(p, s)
p = os.path.join(S, "moment_cert_iv", "mcert_iv.py"); s = rd(p)
s = sub(s, "(appendix D item moment-certification, part (A1)-(A5)).", "(appendix D item moment-certification, range (A5); (A1)-(A5) were the record's run names).")
s = sub(s, "Recursions (7.2)-(7.3) of section 7.4", "Recursions (7.1)-(7.2) of section 7.4")
s = sub(s, "three recursions of (7.3)", "three recursions of (7.2)")
wr(p, s)
p = os.path.join(S, "four_families_DDLnat", "families_iv.py"); s = rd(p)
s = sub(s, "10:old-8-33", "9:old-8-33", 1); s = sub(s, "10:old-8-32", "9:old-8-32", 2); s = sub(s, "10:old-8-23", "6:old-8-23", 1)
wr(p, s)

# (3) README
p = os.path.join(ROOT, "원고_자료", "README.md"); s = rd(p)
s = sub(s, "·절점값·Fritsch–Carlson 기울기의 구간)", "·절점값·절점 기울기의 구간)")
s = sub(s, "두 작업자 각 약 9500초", "두 프로세스 각 약 9500초")
s = sub(s, "작업자 $W$개 가운데", "프로세스 $W$개 가운데")
s = sub(s, "`launch.py W`가 작업자를 띄우고", "`launch.py W`가 프로세스를 띄우고")
wr(p, s)

# (4) 생성기·패치 도구
p = os.path.join(ROOT, "scripts", "_gen_재실행표.py"); s = rd(p)
s = sub(s, 'expect="위반 $0$; 가장 작은 여유 $4.7447\\cdot10^{-13}$($i=0$); 엄격 감소, 최소 감소 $6.643869\\cdot10^{-6}$($i=11999$)"',
        'expect="위반 $0$; 가장 작은 여유 $4.7447\\cdot10^{-13}$($i=0$); 엄격 감소, 최소 감소 $6.643869\\cdot10^{-6}$($i=11999$); 이음새 두 줄(정리 closed-form-envelope (라); $\\xi=2$, $2.1$) True"')
s = sub(s, 'time="작업자 2개 각 약 9500초', 'time="프로세스 2개 각 약 9500초')
s = sub(s, 'time="작업자 1→4→2→3개', 'time="프로세스 1→4→2→3개')
s = sub(s, "(작업자 둘; 하나면", "(프로세스 둘; 하나면")
wr(p, s)
p = os.path.join(ROOT, "scripts", "_patch_README_세션파일.py"); s = rd(p)
s = sub(s, "두 작업자 각 약 9500초", "두 프로세스 각 약 9500초"); wr(p, s)
print("edits ok")
