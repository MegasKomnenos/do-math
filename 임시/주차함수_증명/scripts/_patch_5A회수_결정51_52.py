# -*- coding: utf-8 -*-
"""5A 2차 대조 회수: 세션 결정 51·52를 적고, 구조표 5.4 제목을 「꼬리 띠」로 고치며, 작업 장부에 회수·재개 항목을 더하고, 최종 정리 지시에 5A 항목을 더한다."""
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


D = (
    "51. **지위 괄호의 꼴과 소절 머리(2026-11-13 새벽; 5A 2차 대조 #35·#38).** 계산만으로 선 진술은 「계산 증거(등급); r…」로 적고 「계산 보조」를 함께 적지 않는다. 등급이 둘이면 괄호 안에 쉼표로 나열한다(「계산 보조(정확 정수·유리수, 방향 반올림 구간)」). 괄호 안에 설명을 두지 않는다. `####` 소절 머리는 허용한다(조립은 `##`·`###`만 번호에 쓴다). 지침 7.3·7.5에 세션이 한 문장씩 더한다(최종 정리 때).\n"
    "52. **5장의 낱말(2026-11-13 새벽; 5A 2차 대조 #25·#26).** 「띠」는 3절대로 중앙 띠·둘째 층 띠·꼬리 띠 셋뿐이므로 5.4의 「명시적 띠」는 「꼬리 띠」로 하고 절 제목을 「5.4 꼬리 띠, 임계 창, 잔여 $W^\\sharp$」로 바꾼다(구조표 수정). 「덮개」·「덮개 칸」은 5.6의 뜻(3절)만 가지며 5.2·5.4의 다른 개념은 다른 낱말로. 진술문에 나타나거나 두 절 이상에서 쓰는 조어는 「장부에 없는 낱말」 표로 3절에 등록한다(6장 결정 4와 같은 기준).\n"
)


def patch_decisions(s):
    if "51. **지위 괄호의 꼴과 소절 머리" in s:
        return s
    assert "50. **낱말 「h-변환」" in s
    return s.rstrip("\n") + "\n" + D


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


def patch_struct(s):
    a = "| 5.4 명시적 띠, 임계 창, 잔여 $W^\\sharp$ |"
    print("anchor 5.4:", s.count(a))
    if s.count(a) == 1:
        s = s.replace(a, "| 5.4 꼬리 띠, 임계 창, 잔여 $W^\\sharp$(첫 판 「명시적 띠」; 3절의 띠 셋 가운데 꼬리 띠 — 세션 결정 52) |")
    return s


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


ENTRY = (
    "- 2026-11-13 00:2x **5A 2차 대조 회수와 집필자 재개; 2장 후속**: 2차 대조(fable-high, 54분; `대조v2/장5A_2차대조.md`) — 상 13(parity-tail 상수 오산 9/32·63/32(결론 유지), old-5-5 「<0.004」 거짓(0.004069; 결론 유지), 지위 표지 8(결정 38 미적용·계산 보조 누락), D.newton-m170 $\\chi_k$ 오기, D.bernstein-signs 식 누락, omitted-tail (라) 표지 누락), 중 21, 하 9; 증명 45개 전부 재유도(전 단계 확인 41; 작성자 판단 17(+1) 가운데 기록에 없는 것은 둘뿐, 나머지는 기록에 있거나 표준); 접합: 2장 chain-normalization 전제는 5A 사용 전부 덮음(ι=3 좌변 구절 보충 권고), 4장 4.2 정의 일치($\\Gamma_d$ 인수 글자만 다름), 6장은 라벨 미참조(6장 재개에 포함됨), 5A는 5B 라벨을 앞당겨 부르지 않음. "
    "세션 결정 51(계산 증거 괄호 꼴·등급 둘 나열·`####` 허용), 52(「명시적 띠」→「꼬리 띠」, 덮개는 5.6 뜻만, 조어 등록). 5A 집필자(a25a6ba133fe1200a) 재개: 보고서 전부 + 결정 38·40·47·51·52 + 전역 겹침 국소($S$·$T$·$\\hat J$·$\\hat Z$·$V_m$·$\\Pi_{r,d}$ 등) 교체 + 예약 글자 12곳 + 정정 이력·수치 관찰 5곳 삭제; 5B의 「5A에 요구하는 것」은 짧은 2차 재개로. 2장 집필자(a8f572e5f436cfa00) 짧은 재개: chain-normalization (다)에 ι=3 좌변 구절(기록 확인 뒤). "
    "사전 최종 정리에 더할 것: 1.2 쓰이는 장에 5 추가($J_n(z)$, $Z_k$·$H_k$, $V(x)$, $\\mathfrak b_j(\\varsigma)$, $\\Phi$, $\\Lambda$, $\\mathcal G_{z,i,n}$, $T^{\\mathrm G}$, $\\Pi$); 5장 여유에서 $J$·$Z$·$V$·$\\Pi$ 제거; 1.3 묶음 385/387($\\mathfrak d$)·386/388($\\epsilon$) 충돌을 5A 최종 글자로; 3절 「덮개」·「덮개 칸」 5.6 한정 확인, 「명시적 띠」 제거; 5A 「장부에 없는 낱말」 표."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "5A 2차 대조 회수와 집필자 재개" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·4·7A·8·9·10장 완료, 6·7B·5B 수정 중, 5A 2차 대조 중)", "1·3·4·7A·8·9·10장 완료, 2장 후속(ι=3) 중, 5A·5B·6·7B 수정 중; 7A 부록 D5 식 보충 중)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)


def patch_final(s):
    a = "## 3. 1.3 국소 기호 합치기(결정 25)"
    assert s.count(a) == 1
    add = ("- 5A 2차 대조가 찾은 것: 1.2 「쓰이는 장」에 5를 더할 글자 — $J_n(z)$, $Z_k(\\sigma)$·$H_k(\\sigma)$, $V(x)$, $\\mathfrak b_j(\\varsigma)$, $\\Phi$, $\\Lambda$(4.3의 것), $\\mathcal G_{z,i,n}$·$T^{\\mathrm G}$(2.7), $\\Pi$(5B의 $\\Pi(Y)$); 그에 따라 5장 여유 글자에서 $J$·$Z$·$V$·$\\Pi$를 뺀다. 1.3 묶음 385/387($\\mathfrak d$ 부분합/상수)과 386/388($\\epsilon_l$/$\\epsilon_1$)의 충돌은 5A 집필자의 최종 글자로. 3절 「덮개」·「덮개 칸」은 5.6 뜻만(5A가 다른 낱말로 바꿈); 「명시적 띠」는 어디에도 두지 않는다(결정 52). 지침 7.3·7.5에 결정 51의 문장(계산 증거 괄호 꼴, 등급 둘 쉼표 나열, `####` 허용)은 세션이 더한다.\n\n")
    if "5A 2차 대조가 찾은 것" not in s:
        s = s.replace(a, add + a)
    return s


rw(os.path.join(ROOT, "파견", "장부v2_최종정리_지시.md"), patch_final)
