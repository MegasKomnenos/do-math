# -*- coding: utf-8 -*-
"""수학 검사(태그 6) 수정 스크립트. 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다(멱등).
사용: python -I scripts/수학검사/6_fix.py"""
import io, sys
PATH = '장v2/장6.md'
EDITS = [
    # 1. 「순증가」 → 장부 낱말
    (r"이고, 이 값은 $t$에 대해 순증가하며 $t=k-1$에서",
     r"이고, 이 값은 $t$에 대해 엄격히 증가하며 $t=k-1$에서"),
    (r"이므로 비는 $t$에 순증가한다. $t=k-1$에서",
     r"이므로 비는 $t$에 엄격히 증가한다. $t=k-1$에서"),
    (r"보조정리 {{6:tilt-interval}}의 순증가에서 $\mathfrak r_N<(1+1/k)^{k-1}$이다.",
     r"보조정리 {{6:tilt-interval}}의 엄격 증가에서 $\mathfrak r_N<(1+1/k)^{k-1}$이다."),
    (r"$g$가 순증가하므로(보조정리 {{2:old-2-26}}(가))",
     r"$g$가 엄격히 증가하므로(보조정리 {{2:old-2-26}}(가))"),
    # 2. 𝔍_y(2): 반올림한 수와의 등호 → 하계
    (r"-1.545\,e^{-1}}{(y+1)(y+2)}=\frac{0.1353(2y+2)-0.5684}{(y+1)(y+2)}>0",
     r"-1.545\,e^{-1}}{(y+1)(y+2)}\ \ge\ \frac{0.1353(2y+2)-0.5684}{(y+1)(y+2)}>0"),
    # 3. tl_V^{-1} 상계: 1/(1-3/204)=1.014925… > 1.0149
    (r"$y\ge50$에서 $\mathrm{tl}_V^{-1}\le1.0149$이고",
     r"$y\ge50$에서 $\mathrm{tl}_V^{-1}\le1.0150$이고"),
    (r"$\mathfrak u\le1.0443\cdot1.0149\cdot1.01961\cdot\frac43\le1.449$",
     r"$\mathfrak u\le1.0443\cdot1.0150\cdot1.01961\cdot\frac43\le1.449$"),
    (r"네 인자가 차례로 $4/3$, $1/2$, $1.01961$, $1.0149$ 이하라",
     r"네 인자가 차례로 $4/3$, $1/2$, $1.01961$, $1.0150$ 이하라"),
    # 4. 1.35·3131=4226.85 < 4227
    (r"$K\ge1.35k\ge4227\ge4000$",
     r"$K\ge1.35k\ge4226\ge4000$"),
    # 5. (1/2)e^{-1}=0.18394… < 0.184 (하계이므로 내림)
    (r"좌변은 $\frac12e^{-1}=0.184$ 이상이다.",
     r"좌변은 $\frac12e^{-1}\ge0.183$ 이상이다."),
    # 6. 3131^{1/3}=14.6294… < 14.63; 큰 근 11.0946… > 11.09
    (r"$\mathfrak u:=k^{1/3}\ge14.63$으로 두면",
     r"$\mathfrak u:=k^{1/3}\ge14.629$로 두면"),
    (r"큰 근 $\mathfrak u=11.09$ 위에서 성립한다.",
     r"큰 근 $\mathfrak u=11.10$ 위에서 성립한다."),
]
def main():
    s = io.open(PATH, encoding='utf-8').read()
    changed = 0
    for old, new in EDITS:
        c_old, c_new = s.count(old), s.count(new)
        if c_old == 0 and c_new == 1:
            print('이미 적용:', old[:50]); continue
        if c_old != 1:
            print('앵커 수 %d (건너뜀):' % c_old, old[:60]); continue
        s = s.replace(old, new); changed += 1
        print('치환:', old[:50], '→', new[:50])
    io.open(PATH, 'w', encoding='utf-8', newline='\n').write(s)
    print('치환 수', changed)
if __name__ == '__main__':
    main()
