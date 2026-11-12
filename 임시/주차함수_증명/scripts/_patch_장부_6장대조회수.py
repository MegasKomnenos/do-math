# -*- coding: utf-8 -*-
"""작업 장부: 6장 2차 대조 회수와 집필자 재개 항목; 최종 정리 지시에 6장 사전 항목을 더한다."""
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


ENTRY = (
    "- 2026-11-13 00:0x **6장 2차 대조 회수와 집필자 재개**: 2차 대조(fable-high, 재개 포함 약 90분; `대조v2/장6_2차대조.md`, 조각으로 이어 붙임) — 상 3(합 지표 $R$/피합수 $T$·$J$ 불일치, 치환 잔재 8자리, `\\mathsf \\mathfrak o(k)`), 중 16, 하 9; 수학적 오류 없음; 증명 29행 전 단계 확인, 작성자 판단 12단계 전부 성립, V-핵심 [r317d678] 경로·`{{6:V-all}}` 조립 닫힘, 명제 W (가) 열세 부등식 40자리 재계산 성립; 부록 D 자료 10개 실재·값 일치. "
    "세션 결정 7항: 지위는 결정 38(열하나 「증명됨(, X에 의존)」, 계산 단계 있는 셋은 「비형식 증명, 계산 보조」, small-k-bulk는 witness-position-bound 의존), 증인 위치 경계 세 곳 라벨화, 6.3의 $\\xi:=z/t$는 창 좌표와 다른 양이라 교체(장부 「$\\xi$ 6.3」 되돌림), 전역 겹침 7종 교체·조화수는 로마체, 두 뜻 약 40종은 결정 47, 낱말은 진술문·두 절 이상이면 표로(「최빈 위치」→「증인」), 부록 D v-negative-k3131을 prop-W-thirteen에 합침, old-5-13 범위는 장5A.md로 확인, $\\mathfrak m(n)$은 5.2 정의를 가리킴. 6장 집필자(acafd99850c74a3fb) 재개. "
    "사전 최종 정리에 더할 것: $\\theta_t(k)$ 쓰이는 장 +6; $\\xi$ 정의 절 6.3 반영 취소(창 좌표의 원래 정의 절로); $R_j$·$Z_k(F)$·$H_k(F)$·$\\Pi_j(y)$ 쓰이는 장 +6; 6장 「장부에 없는 낱말」 표; 명세 장6.json의 D_items에서 v-negative-k3131 제거."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "6장 2차 대조 회수와 집필자 재개" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·4·8·9·10장 완료, 7A·7B·5B 수정 중, 6·5A 2차 대조 중)", "1·2·3·4·8·9·10장 완료, 6·7A·7B·5B 수정 중, 5A 2차 대조 중)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)


def patch_final(s):
    a = "## 3. 1.3 국소 기호 합치기(결정 25)"
    assert s.count(a) == 1
    add = ("- 6장 2차 대조가 찾은 것: $\\theta_t(k)$ 쓰이는 장에 6; $\\xi$의 정의 절을 6.3으로 옮긴 반영은 취소(6.3의 $\\xi:=z/t$는 창 좌표가 아니며 6장 집필자가 다른 글자로 바꿈; 창 좌표 $\\xi$의 정의 절은 원래대로); $R_j$·$Z_k(F)$·$H_k(F)$·$\\Pi_j(y)$ 쓰이는 장에 6.\n\n")
    if "6장 2차 대조가 찾은 것" not in s:
        s = s.replace(a, add + a)
    return s


rw(os.path.join(ROOT, "파견", "장부v2_최종정리_지시.md"), patch_final)
