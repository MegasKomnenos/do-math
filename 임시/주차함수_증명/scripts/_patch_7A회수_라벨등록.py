# -*- coding: utf-8 -*-
"""7A 수정 회수: 구조표 7.2·7.3·7.5·5.5 셀에 다른 장(조각)이 가리키는 새 라벨을 등록하고(라벨 등록부 재생성용),
장7A.md의 old-6-9 머리 의존 목록에 정리 4.5(계산 보조)를 더하며, 작업 장부에 회수 항목을 적는다."""
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


def patch_struct(s):
    # 7.3 → 7.2: 초승법성 보조정리는 7A가 7.2에 두었다.
    a = "`{{7:supermultiplicative}}` 초승법성 보조정리 4.1 [r7c26b8b] §4(3행)과 Fekete 보조정리(문헌 인용)로 $u_l\\le1$, "
    print("anchor supermultiplicative:", s.count(a))
    if s.count(a) == 1:
        s = s.replace(a, "")
    b = "6.10, 새 `{{7:self-consistent-S}}`"
    assert s.count(b) == 1
    if "`{{7:flat-threshold}}` 문턱 자리 평균" not in s:
        s = s.replace(b, "6.10, `{{7:supermultiplicative}}` 초승법성 보조정리 4.1 [r7c26b8b] §4과 Fekete 보조정리(문헌 인용)로 $u_l\\le1$(7A가 7.2에 둠), `{{7:flat-threshold}}` 문턱 자리 평균의 상계가 주는 증가 경계(따름정리; [r7c26b8b] 따름정리 3·[rb6423c6] 명제 P8; (라) $\\mathsf W_L^\\flat\\Leftrightarrow\\mathsf W_L$을 10.7이 가리킴), `{{7:prime-decomposition}}`·`{{7:level-chain}}`·`{{7:lm-core}}`(7A의 내부 보조정리), 새 `{{7:self-consistent-S}}`")
    c = "`{{7:polar-W}}` [r89eb039] §3.1·§7.2·§7.3(58행; 488블록·L15 인증은 부록 D)"
    assert s.count(c) == 1
    if "{{7:theorem-G-prime}}" not in s:
        s = s.replace(c, c + "; 새 `{{7:lemma-P-prime}}` 보조정리 P′(원 위 감김수)·`{{7:theorem-G-prime}}` 정리 G′(열 $501$–$2000$ 열별 인증서 $(n^{\\mathrm{bis}}_0,\\Gamma,\\mathfrak P^{\\mathrm U}_k)$의 정당화) [rb7effe0] §6.5(세션 결정 42; 7.4·7.5가 가리킴); polar-R (나)에 극 영역 상계 $\\mathfrak P_k(n)\\le\\Gamma\\,\\mathfrak P_k(\\infty)\\le V$, polar-W (가)에 $\\mathfrak P_k(n)\\le1.445/\\sqrt k$")
    d = "정리 Q-fin(1130열)은 부록 D"
    assert s.count(d) == 1
    if "{{7:qstar-columns}}" not in s:
        s = s.replace(d, "정리 Q-fin은 `{{7:qstar-columns}}`(열 $2001$–$3130$의 한 걸음 판정; 계산 보조; 10.7이 가리킴; 1130열 인증은 부록 D); `{{7:qstar-implies-wlflat}}` 따름정리(한 걸음 판정에서 왼쪽 잔여 증가로; (가)의 ⇐ 방향 결합은 세션 결정 42; 10.7이 가리킴)")
    e = "단항식 계수의 유도는 작성자 증명(조사 2 상신 10); 정정값만 사용"
    assert s.count(e) == 1
    if "{{D:zeta-constants}}" not in s:
        s = s.replace(e, e + "; Riemann 제타 상수 $\\mathsf z_{1/2}$·$\\mathsf z_{-1/2}$·$\\mathsf z_{3/2}$의 정의(세션 결정 48)와 인증 구간은 부록 D `{{D:zeta-constants}}`; [r8a9b11e] 보조정리 U2는 5A의 `{{5:weight-envelope}}`와 다른 라벨(5B 집필자가 정함)")
    return s


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


def patch_7a(s):
    a = "[증명됨, 정리 {{5:old-5-1}}·정리 {{7:seed-transfer}}·보조정리 {{7:column-lemma}}에 의존; rb6423c6].** $\\mathsf W_L\\Leftrightarrow\\mathsf P_L$이다."
    assert s.count(a) == 1, s.count(a)
    return s.replace(a, "[증명됨, 정리 {{4:old-4-5}}·정리 {{5:old-5-1}}·정리 {{7:seed-transfer}}·보조정리 {{7:column-lemma}}에 의존; rb6423c6].** $\\mathsf W_L\\Leftrightarrow\\mathsf P_L$이다.")


rw(os.path.join(ROOT, "장v2", "장7A.md"), patch_7a)


ENTRY = (
    "- 2026-11-13 00:1x **7A 수정 회수**(fable-high, 38분): 결함 #1–#46 전부와 세션 추가(보증 문단 둘 삭제, 예약 글자 잔존, r9e782f5 유지, $\\mathfrak a^\\circ_m$은 2장에 없어 7.2에서 정의, 사전 밖 낱말 표) 반영 — `장v2/장7A.md`(186KB; 진술 37 = 35 + `{{7:lemma-P-prime}}`·`{{7:theorem-G-prime}}`), `부록D_장7A.md`(79KB; xcert-partAB·polar-blocks-488의 식 전부, self-consistent-constants (4) 확인 추가), `대조v2/장7A_집필대조.md` 「2차 대조 반영」 절(198–327행: 처리 표, polar-R (나)·polar-W (가) 진술, 7B가 맞출 최종 글자 표, 최종 국소 글자 표, 장부에 없는 낱말 표). "
    "지위: old-6-6·factorial-moment·old-6-8·flat-threshold·fourier-lemmas·X-cert·polar-R 증명됨; old-6-9 「증명됨, 정리 5.1·seed-transfer·column-lemma에 의존」(세션이 정리 4.5 — 계산 보조 — 를 더함); polar-W 「비형식 증명, 계산 보조(binary64 사전 오차 해석)」. 글자: $T\\to\\mathcal J^{\\mathrm S}$, $\\delta\\to\\varkappa$·$\\vartheta$, $\\mathfrak r\\to\\mathfrak c$, $\\mathfrak s\\to\\mathfrak f$, $Y^\\sharp_\\varrho\\to\\mathfrak V_{\\mathfrak F}$, $P\\to\\preceq$, $C\\to\\mathsf c$, $Z$ 유지. 7B 집필자에게 2차 지시(7A 글자 표·새 라벨·polar 진술에 맞춤) 전송. 구조표 7.2·7.3·7.5·5.5 셀에 다른 장이 가리키는 새 라벨 등록(supermultiplicative 7.2로 이동). "
    "**7A 완료**(세션 일관성 검토 대기). 남은 세션 몫: 부록 D3 (4)의 확인 코드 한 줄을 자료 묶음에 더함; 부록 D5의 L3–L12 닫힌 꼴 합·격자 셀 식이 코드(`sparts.py`·`bounds_ia.py`·`cert_ia2.py`)에만 있어 구성만 적힘 → 조립 전 표적 파견(gp-fable-medium)으로 식을 옮긴다(지침 4.5(ㄷ)); 1.3 합칠 때 「남은 같은 글자 두 뜻(다른 절)」 목록 처리."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "**7A 수정 회수**" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·4·8·9·10장 완료, 6·7A·7B·5B 수정 중, 5A 2차 대조 중)", "1·2·3·4·7A·8·9·10장 완료, 6·7B·5B 수정 중, 5A 2차 대조 중)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)
