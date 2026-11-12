# -*- coding: utf-8 -*-
"""세션 결정 40(부록 D의 코드 변수 대응 문장)·41(섬유 부호식의 인수 글자 Z·H)을 세션 결정 파일에 적고,
지침 7.6에 결정 40의 한 문장을 더하며, 작업 장부에 설계 에이전트 7A 후속 반영 회수 항목을 더한다."""
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


D40 = (
    "40. **부록 D의 코드 변수 대응(2026-11-12 밤).** 부록 D 항목이 자료 묶음의 코드·출력을 가리킬 때 코드의 변수 이름이 이 글의 글자와 다르면, "
    "그 항목의 「자료」 줄 뒤에 「코드의 변수 `B`는 이 글의 $\\mathfrak b-1$이다」 꼴로 대응을 적는다. 이는 독자가 부록 D만으로 계산을 다시 돌리게 하려는 부록 D의 본래 몫이지 R4(기록의 기호는 부록에만)의 예외가 아니며, "
    "본문에는 두지 않는다. 2장 부록 D 조각의 「기록의 $B$는 $\\mathfrak b-1$」 문장은 이 꼴로 고친다. 지침 7.6에 한 문장을 더했다.\n"
)
D41 = (
    "41. **섬유 부호식의 인수 글자(2026-11-12 밤).** 2장 보조정리 2.14의 섬유 부호식 $\\mathfrak v_k(Z,H)=(1+\\frac1k)^Z+(1-\\frac1k)^{Z+H}-2$의 두 인수는 무거운 자리 수 $Z_k$와 문턱 자리 수 $H_k$의 값 변수이며, "
    "2장과 7장(7A의 정리 6.2·보조정리 6.3·따름정리 flat-threshold)이 첨자 없는 $Z$, $H$로 적는다. 같은 양의 값 변수이므로 R1′의 「첨자·인수만 다른 같은 양의 변형은 한 기호」에 들고 국소 글자가 아니다. "
    "1.2의 $Z_k$·$H_k$ 행 비고에 「섬유 부호식의 인수는 첨자 없이 $Z$, $H$」를 적고, 1.3 7.2 묶음에 설계 에이전트가 「첫 판 $\\zeta$」로 더한 $Z$의 (ㄱ) 표시는 뺀다(설계 에이전트의 확인 요에 대한 답; 최종 정리 때 반영).\n"
)


def patch_decisions(s):
    anchor = "39. **식별자 자릿수.**"
    assert s.count(anchor) == 1
    if "40. **부록 D의 코드 변수 대응" in s:
        return s
    s = s.rstrip("\n") + "\n" + D40 + D41
    return s


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


def patch_guide(s):
    a = "조립 스크립트 `scripts/조립_v2.py`가 머리 `### D.{{D:이름}}`과 참조 `부록 D.{{D:이름}}`을 번호로 바꾼다."
    assert s.count(a) == 1
    add = (" 항목이 가리키는 코드의 변수 이름이 이 글의 글자와 다르면 「자료」 줄 뒤에 「코드의 변수 `B`는 이 글의 $\\mathfrak b-1$이다」 꼴로 대응을 적는다(세션 결정 40). "
           "이 대응은 부록 D에만 두고 본문에는 두지 않는다.")
    if "코드의 변수 `B`는 이 글의" not in s:
        s = s.replace(a, a + add)
    return s


rw(os.path.join(ROOT, "파견", "집필_공통지침_v2.md"), patch_guide)


ENTRY = (
    "- 2026-11-12 23:1x 사전 7A 후속 반영 회수(설계 에이전트, 6분; 처리표 「9. 추가 반영」에 네 행): $n^\\varphi_k$·$\\mathsf q_k$·$\\check n_k$·$n^\\ast_k$ 삭제(구조표·장7A·7B·9에 쓰임 0 확인), 정의 절 다섯($\\mathsf t_k$·$\\tilde n_k$ 7.1, $n^\\natural_k$·$\\mathsf{LM}^{\\flat\\flat}$ 7.2, $\\mathfrak P_k(\\infty)$ 7.3), $T(x)$ 쓰이는 장에 5·7, "
    "7.3 묶음 글자를 집필자 선택에 맞춤($\\eta\\to\\mathfrak h$, $\\mathcal Y\\to\\mathfrak H$, $L_{j,i}\\to\\mathfrak l_{j,i}$, $m^\\sharp_0\\to\\mathfrak b_0$, $\\gamma_\\delta\\to\\mathfrak z$), 7.2 old-6-7 묶음에 $\\mathfrak U$·$\\mathfrak l$·$\\mathcal C_y$·$\\mathcal F$·$Z$ 추가. 검산: 1.2 중복 예외 2뿐, 1.3 R1′ 0/710, 7절 68/68·204행. "
    "확인 요 하나(7.2 묶음 $Z$가 7장 전역 $Z_k$와 겹침)는 세션이 가름: 장7A.md의 $Z$는 2장 보조정리 2.14의 섬유 부호식 $\\mathfrak v_k(Z,H)$의 첫 인수(무거운 자리 수의 값 변수)로 2장과 같은 글자이고 $Z_k$와 같은 양이므로 국소 글자가 아니다 → 결정 41(1.2 $Z_k$·$H_k$ 행 비고에 값 변수, 7.2 묶음의 (ㄱ) 표시 제거; 설계 에이전트 최종 정리 때 반영). "
    "결정 40(부록 D 「코드의 변수 …」 대응 문장)을 함께 적고 지침 7.6에 한 문장 더함. 10장 2차 대조 #19(10.7 넷째·다섯째·여섯째 고리의 절 참조 「7.5절에서 보았듯 …」)는 7B의 `{{7:qstar-columns}}`·`{{7:qstar-implies-wlflat}}`와 7A의 `{{7:flat-threshold}}`(라)로 조립 전에 세션이 치환한다."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "사전 7A 후속 반영 회수" in s:
        return s
    return s.replace(old, "\n" + ENTRY + "\n" + old)


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)
