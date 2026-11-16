# -*- coding: utf-8 -*-
"""수학 검사 둘째(태그 10) 수정 스크립트. 멱등. 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.

python -I scripts/수학검사2/10_fix.py

수정 1건(두 토큰): 명제 {{10:old-8-23}} 증명 5단계(부호 보조정리)의 하계 상수.
  본문이 적은 두 전제 ⌊d♮⌋^{3/2}/k ≥ 2^{3/2}(1-1/d♮)^{3/2}(k=6667에서 로그 1.037602)와 q(ρ0) ≤ 1.0722(로그 0.069713)에서
  괄호의 하계는 2.528571 + 1.037602 - 0.069713 = 3.49646…이다. 적힌 ι0 = 3.4966은 이 하계를 위로 반올림한 값이라
  하계로 쓸 수 없다(scripts/수학검사2/10_검산_상수.py 출력 「iota_0 from stated bounds」). 아래로 반올림한 3.4964로 고치고,
  그에 따라 대괄호 값 2ι0-6-0.0288·6·sqrt(σ0) = 0.938925…도 아래로 반올림한 0.938로 고친다(여전히 양수, 결론 불변).
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(ROOT, '장v2', '장10.md')

EDITS = [
    (r"이상이다($\iota_0=3.4966$). 이 값은 $\sigma^\sharp<\sigma^\sharp_0:=e^{-\iota_0/1.5}=0.0972$에서만 음이다.",
     r"이상이다($\iota_0=3.4964$). 이 값은 $\sigma^\sharp<\sigma^\sharp_0:=e^{-\iota_0/1.5}=0.0972$에서만 음이다."),
    (r"=0.70836\sqrt{\rho_0}\cdot0.939>0$ 이상이다.",
     r"=0.70836\sqrt{\rho_0}\cdot0.938>0$ 이상이다."),
    # 수정 2: 보조정리 {{10:bulk-majorants}} 증명. 대괄호 (0.48)^{-1/2}-1+(1-sqrt0.48)/3 = 0.5457689…의 상계 「0.5458」로는
    # 132.32·0.5458 = 72.2203 > 72.217이라 적힌 d̄(k)=72.217/√k가 따라 나오지 않는다. 한 자리 더 적은 상계 0.54577
    # (132.32·0.54577 = 72.2163 ≤ 72.217)로 고친다. d̄의 값 72.217 자체는 옳으므로 그대로 둔다.
    (r"$\nu/k>0.48$에서 $0.5458$ 이하다. 그래서 $\bar{\mathfrak d}(k)$다.",
     r"$\nu/k>0.48$에서 $0.54577$ 이하다. 그래서 $\bar{\mathfrak d}(k)$다."),
]


def main():
    text = io.open(TARGET, encoding='utf-8').read()
    changed = 0
    for old, new in EDITS:
        n_old, n_new = text.count(old), text.count(new)
        if n_old == 0 and n_new == 1:
            print("이미 적용됨:", old[:40])
            continue
        if n_old != 1:
            raise SystemExit("앵커가 정확히 한 번이 아님(%d): %s" % (n_old, old[:60]))
        text = text.replace(old, new)
        changed += 1
        print("치환:", old[:50], "->", new[:50])
    if changed:
        io.open(TARGET, 'w', encoding='utf-8', newline='\n').write(text)
    print("치환 수:", changed)


if __name__ == '__main__':
    main()
