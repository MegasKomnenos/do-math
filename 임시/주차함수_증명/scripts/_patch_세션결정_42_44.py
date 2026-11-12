# -*- coding: utf-8 -*-
"""7A 2차 대조 회수에 따른 세션 결정 42–44를 세션 결정 파일에 적고, 작업 장부에 회수·재개 항목을 더한다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


D42 = (
    "42. **7B가 7A에 전제한 세 진술의 소재(2026-11-12 밤; 7A 2차 대조 #5–#7).** (ㄱ) 극 영역의 중간 결론 「$n\\ge n^\\circ_k$에서 $\\mathfrak P_k(n)\\le1.445/\\sqrt k$」는 `{{7:polar-R}}`의 진술 (나)로 올린다([r89eb039] §3.1; 부록 D polar-blocks-488). "
    "(ㄴ) 열 $841$–$2000$의 열별 인증 $(n^{\\mathrm{bis}}_0,\\Gamma_k,P_{U,k})$를 정당화하는 손 진술([rb7effe0] §6.5 보조정리 P′·정리 G′)은 7.3에 새 라벨 `{{7:lemma-P-prime}}`·`{{7:theorem-G-prime}}`로 전개한다(7A). 인증 자료는 7B의 부록 D moment-certification에 둔다. "
    "(ㄷ) $\\mathsf W_L^\\flat\\Leftrightarrow$「$\\mathcal W^{(>40)}$의 모든 위치」의 결합(⇐에 드는 정리 5.1·`{{7:old-6-13}}`·열 $501$–$2000$)은 7B의 따름정리 `{{7:qstar-implies-wlflat}}`(가)가 맡고, `{{7:polar-W}}`는 (가)+(나)로 둔다. 7B 394행의 `{{7:old-6-9}}` 인용은 7B 재개 때 고친다.\n"
)
D43 = (
    "43. **binary64 부풀림 계산의 산술 등급 이름(2026-11-12 밤).** 기록이 「binary64 바깥 부풀림, 라이브러리 4 ulp 가정, 오차 예산」으로 적은 계산([r89eb039] §6.2의 488블록, [r10ff8c2]·[r475ada3]의 모멘트 인증 일부)은 네 등급 가운데 「binary64 사전 오차 해석」이다. "
    "바닥·천장 반올림의 고정소수점·정수 구간([rc9aee43] 열 인증)은 「방향 반올림 구간」이다. 지위 괄호 안에는 등급 이름만 적고 설명은 부록 D에 둔다. 7A·7B에 적용한다.\n"
)
D44 = (
    "44. **Lagrange 역변환의 음의 거듭제곱(2026-11-12 밤; 7A 2차 대조 #34).** 2.5절의 진술(실수 $\\upsilon>0$)은 바꾸지 않는다. 7A가 $[x^n]T(x)^{-1}$을 쓰는 자리는 Lagrange–Bürmann 공식의 정수 거듭제곱 판(Stanley, *Enumerative Combinatorics* vol. 2, Theorem 5.4.2; $k\\in\\mathbb Z$)을 표준 결과로 들어 그 자리에서 쓴다. 지위는 바뀌지 않는다(결정 38).\n"
)


def patch_decisions(s):
    if "42. **7B가 7A에 전제한" in s:
        return s
    assert "41. **섬유 부호식의 인수 글자" in s
    return s.rstrip("\n") + "\n" + D42 + D43 + D44


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


ENTRY = (
    "- 2026-11-12 23:3x **7A 2차 대조 회수와 집필자 재개**: 2차 대조(fable-high, 26분; `대조v2/장7A_2차대조.md`) — 상 9(factorial-moment 지지 가정 누락, prime-decomposition (가) 논거 오류, seed-transfer (라) 범위 과장·𝔨_k≥16 거짓, polar-N 중간 부등식 0.368→0.3683, 7B 전제 셋의 부재(#5–#7), 부록 D xcert-partAB 결과 누락·식 누락), 중 26(지위 되돌림 9, 식별자 5자리, 정정 이력, 사전 밖 낱말 9, 글자 충돌 다수, 1.3과 다른 글자), 하 11; 증명 32개 재유도(전 단계 확인 28; 작성자 판단 7곳 전부 성립; 표시 없이 메운 20곳 중 결함 3). "
    "세션 결정 42(7B 전제 셋의 소재: polar-R (나)·7.3 새 라벨 P′·G′·결합은 7B), 43(binary64 부풀림은 「binary64 사전 오차 해석」), 44($q=-1$ Lagrange는 Stanley Thm 5.4.2 인용; 2장 불변). 7A 집필자(a1148e6467d84da2c) 재개: 보고서 전부 + 결정 A–E + 세션 발견(정정 이력 둘, 예약 글자 9곳, 부록 D 4곳, r9e782f5 유지, 𝔞°_m 정의 자리 확인, 사전 밖 낱말 표). 완료 판정은 장7A.md·부록D_장7A.md 갱신과 집필대조 「2차 대조 반영」 절. "
    "**7B 재개는 7A 회수 뒤**(7A 최종 글자 표·새 라벨에 맞춤; 394행 old-6-9 인용, 등급 이름, ς_k·L_1·m 글자). 사전 최종 정리에 더할 것: $C_k$ 정의 절 7.3→7.2, 3절 극·소인 주차함수 7.3→7.2, 7A 「장부에 없는 낱말」 표, 7A 최종 국소 글자(1.3 7.2·7.3 묶음 재배정)."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "7A 2차 대조 회수와 집필자 재개" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·4·8·9·10장 완료, 6·5B·7B·7A·5A 2차 대조 중)", "1·2·3·4·8·9·10장 완료, 7A 수정 중, 6·5B·7B·5A 2차 대조 중)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)
