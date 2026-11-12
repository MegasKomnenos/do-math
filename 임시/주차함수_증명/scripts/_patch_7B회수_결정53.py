# -*- coding: utf-8 -*-
"""7B 수정 회수: 세션 결정 53(다른 장이 인용하는 진술의 글자는 전역 전체와 겹치지 않게)을 적고, 작업 장부와 최종 정리 지시를 갱신한다."""
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


D53 = (
    "53. **다른 장이 인용하는 진술의 국소 글자(2026-11-13 새벽; 7B 수정 회수).** 7B가 4장 보조정리 `{{4:gauss-contraction}}`의 글자($\\mathfrak a$, $\\mathfrak u$, $\\mathfrak v$)를 진술에 그대로 가져오자 7장 전역 $\\mathfrak a_n$·$\\mathfrak u_n$·$\\mathfrak v_k$와 겹쳤고, `{{4:borel-tail-arc}}`의 $\\varepsilon=k^{-1/2}$·$S_k$도 5A의 $\\varepsilon_k(\\eta)$·7장의 $\\varepsilon_m$·1.2의 $S_i$와 겹친다. "
    "규칙을 더한다: 다른 장이 진술로 인용하는 진술(새 보조정리 포함)의 진술문에 나오는 국소 글자는 1.2 전역 전체(어느 장이든)·1.1 변수·6절 예약과 (바탕 글자, 글자체)가 겹치지 않게 고른다. 4장 집필자가 두 보조정리의 글자를 바꾸고, 5B·7B가 그에 맞춘다(짧은 재개). 0절 R1′에 세션이 더한다(최종 정리 때).\n"
)


def patch_decisions(s):
    if "53. **다른 장이 인용하는 진술의 국소 글자" in s:
        return s
    assert "52. **5장의 낱말" in s
    return s.rstrip("\n") + "\n" + D53


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


ENTRY = (
    "- 2026-11-13 00:5x **7B 수정 회수**(fable-high, 약 65분; 1차·2차 지시를 한 번에): 결함 1–41 전부 반영(미룬 것 없음) — `장v2/장7B.md`(174KB, 896행, 진술 46), `부록D_장7B.md`(30KB; band102 (ㄹ)에 audit_band.py의 식 전부), 집필대조 「2차 대조 반영」 절(처리/지위/7A 맞춤 표 11+28행/장부에 없는 낱말/4장·7A에 요구하는 것/세션이 장부에 반영할 것). "
    "결정 42(theorem-C-moment (가)→polar-W (가) 둘째 문장, (나)·moment-window·부록 D→theorem-G-prime의 $(n^{\\mathrm{bis}}_0,\\Gamma,\\mathfrak P^{\\mathrm U}_k)$; qstar-implies-wlflat (가) ⇐ 다섯 입력으로 완결; 394행 정정; old-6-22 사슬에 flat-threshold(라)), 45(hermite-nu 전면 재작성: 4장 글자·$1\\le\\nu\\le600$·$\\mathcal H_2$ 기호 검산·「비형식 증명, 계산 보조, gauss-contraction에 의존」), 43·38(등급 넷, 지위 재판정 10), 산술 정정 7, 사족·계획 문장 11곳 삭제, 7A 글자 맞춤(같은 양 11, 다른 양 28 — 로마체 이름 다수). "
    "남은 겹침(세션 판정): 4장 보조정리 글자 $\\mathfrak a$·$\\mathfrak u$·$\\mathfrak v$ 대 7장 전역, $\\varepsilon$·$S_k$ 대 5A·7장·1.2 → **세션 결정 53**(인용되는 진술의 글자는 전역 전체와 겹치지 않게) → 4장 집필자 재개(두 보조정리 글자 교체 + gauss-coeff 다섯째 단계의 $\\kappa^2$ 계수 문구를 $n\\in\\{2k-1,2k\\}$로 한정; 7B의 sympy 검산: 일반식은 $506+97\\nu+5\\nu^2+\\cdots$). 7A 집필자 재개(flat-threshold $\\upsilon,\\upsilon'$ 교체; xcert-partAB 결과에 층별 $\\varsigma\\ge5.3146$; $\\mathfrak m_\\Pi=k\\rho_k$를 pole-unique (나)로; X-cert 적분 변수 $\\theta$는 묶인 변수라 유지). 4장 회수 뒤 7B·5B에 새 글자 전달(짧은 재개). "
    "7B 「세션이 장부에 반영할 것」은 최종 정리 지시에 포인터로 추가. 완료: 1·2·3·6·7A·8·9·10장(4장 글자 교체 중; 5B·7B는 4장 글자 맞춤 대기); 수정 중: 5A."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "**7B 수정 회수**" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·4·6·7A·8·9·10장 완료, 5B 수정 끝(5A 충돌 결과 대기), 5A·7B 수정 중)", "1·2·3·6·8·9·10장 완료, 4장 보조정리 글자 교체 중, 7A 소수정 중, 5A 수정 중, 5B·7B는 4장 글자 맞춤 대기)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)


def patch_final(s):
    a = "## 3. 1.3 국소 기호 합치기(결정 25)"
    assert s.count(a) == 1
    add = ("- 0절 R1′에 세션 결정 53 조항을 더한다: 「다른 장이 진술로 인용하는 진술의 진술문에 나오는 국소 글자는 1.2 전역 전체·1.1 변수·6절 예약과 겹치지 않게 고른다」.\n"
           "- 7B 집필대조 「2차 대조 반영」의 「세션이 장부에 반영할 것」 절과 「장부에 없는 낱말」 표를 그대로 반영한다(껍질·삼중·쌍별 도달·Green 원자 등; 뿌리 자리 법칙 정의 절 7.4; 「줄기」 두 뜻 처리 결과).\n\n")
    if "세션 결정 53 조항" not in s:
        s = s.replace(a, add + a)
    return s


rw(os.path.join(ROOT, "파견", "장부v2_최종정리_지시.md"), patch_final)
