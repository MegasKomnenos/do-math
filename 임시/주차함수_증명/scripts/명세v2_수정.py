# -*- coding: utf-8 -*-
"""둘째 판 장별 명세의 확정 덧씌우기.

_draft_장v2_spec.py가 만든 파견/명세v2/장N.json 초안 위에, 세션이 확정한 출처 좌표·종류·이름·처리·입력을 덧씌워
같은 파일을 다시 쓴다. 초안은 재생성해도 되고, 이 파일이 확정값의 정본이다.

사용: python 명세v2_수정.py            (모든 장)
      python 명세v2_수정.py 6 8        (지정한 장만)
그 뒤 python _gen_장v2_파견문.py 파견/명세v2/장N.json --check 로 좌표 해소를 확인한다.
"""
import io, json, os, re, sys

ROOT = r"C:\math\임시\주차함수_증명"
SPEC = os.path.join(ROOT, "파견", "명세v2")
DRAFT = os.path.join(ROOT, "원고.md")

draft_lines = io.open(DRAFT, encoding="utf-8").read().split("\n")


def fe_sec(sec):
    """첫 판 조립본의 절(예 '4.3')의 행 범위."""
    pat = re.compile(r"^#{2,4} " + re.escape(sec) + r"(\s|$)")
    start = None
    level = None
    for i, ln in enumerate(draft_lines, 1):
        m = re.match(r"^(#{2,4}) ", ln)
        if start is None:
            if pat.match(ln):
                start = i
                level = len(m.group(1))
        else:
            if m and len(m.group(1)) <= level:
                return [start, i - 1]
    return [start, len(draft_lines)] if start else None


def S(record, sec=None, file="exposition.md", range=None, note=""):
    d = {"record": record, "file": file, "note": note}
    if range:
        d["range"] = list(range)
    else:
        d["sec"] = sec
    return d


EV_LL = "evidence/producer/output/critical-local-limit.md"
EV_CC = "evidence/producer/output/critical-concavity.md"
EV_EC = "evidence/producer/effective-concavity-proof.md"
EV_KP = "evidence/producer/kernel-proof.md"
EV_RC = "evidence/producer/output/resume-central-analysis.md"
EV_FB = "evidence/producer/output/fixed-bound.md"
EV_GC = "evidence/producer/output/green-connection.md"
EV_RP030 = "evidence/producer/report.md"

# 라벨 → 덧씌울 필드. sources는 통째로 바꾼다. 적지 않은 필드는 초안의 값을 둔다.
FIX = {
    # ---------------- 2장 ----------------
    "{{2:J-egf}}": dict(kind="보조정리", name="$J_n(c)$의 지수 생성함수 표현", record_name="기록 [rba2ecf]의 Green 표현 재구성, 기록 [r37c204b]의 보조정리 3.3",
        process="전개", cls="새로운 것",
        sources=[S("rba2ecf", "2", note="상속한 Green 표현과 그 짧은 유도(마지막 차 분해→선형화→EGF의 선형 ODE→적분인자)"),
                 S("r37c204b", "3.3", note="보조정리 3.3의 재귀 (3.4)와 그 뒤 두 문장")],
        inputs=["{{2:old-2-6}}", "{{2:old-2-27}}", "{{2:old-2-28}}"],
        special="hermite-integral이 아니라 §2의 green-reconstruction이 출처다(조사 4). 적분인자 $Pe^{cU}$의 유도를 모든 단계로 적는다."),
    "{{2:ratio-e}}": dict(kind="따름정리", name="생존 확률 비의 상계 $a_{m+1}\\le e\\,a_m$", record_name="기록 [r60a6f55]의 식 (8)",
        process="전개", cls="표준",
        sources=[S("r60a6f55", "4", note="§4 방문 하계와 증폭식; 식 (8)")],
        inputs=["{{2:old-2-31}}"], special="2.31(나)의 두 줄 따름. 7.2의 `{{7:self-consistent-S}}`가 쓴다."),
    "{{2:chain-expansion}}": dict(kind="정리", name="지정 사슬의 쌍 공식과 사슬 전개", record_name="기록 [r42d9a17]의 식 (8)–(11)",
        process="전개", cls="새로운 것",
        sources=[S("r42d9a17", "2", note="지정된 중첩 부분나무 사슬의 정확한 개수; (8) 쌍 공식, (9)–(11) 사슬 전개")],
        inputs=["{{2:old-2-9}}", "{{2:old-2-10}}", "{{2:old-2-13}}"], special="5.2(셋째 묶음)와 6.6(다섯 조각)이 함께 쓴다."),
    "{{2:moving-tail}}": dict(kind="정리", name="이동 꼬리의 균일 추정", record_name="기록 [r42d9a17]의 uniform-moving-tail (2)·(19)",
        process="전개", cls="고비",
        sources=[S("r42d9a17", "3–4", note="Peer의 포함배제 상·하한(§3)과 균등 추정·세 부분나무 오차(§4); Bonferroni·볼록성")],
        inputs=["{{2:chain-expansion}}", "{{2:old-2-21}}"], special="6.6의 $v_m<0$ 논증([r29c10cd] 명제 W(가))의 전제."),
    "{{2:chain-normalization}}": dict(kind="보조정리", name="사슬 가중치의 정규화와 그 경계", record_name="기록 [r1aa0be6]의 chain-normalization",
        process="전개", cls="새로운 것",
        sources=[S("r1aa0be6", "2", note="원 개수를 정확한 사슬 합으로 옮긴다: $W_n$, $\\mathcal R(n,d)$, 경계 $1\\le W_n\\le(1-r/n)^{-k-2}$"),
                 S("r1aa0be6", "2", file=EV_LL, note="증거 문서 §2의 경계 사례")],
        inputs=["{{2:chain-expansion}}"], special="5.2의 `{{5:third-group}}`과 `{{5:marked-recursion}}`의 전제."),
    # ---------------- 4장 ----------------
    "{{4:e-integral}}": dict(kind="보조정리", name="$e_n$의 적분 표현", record_name="",
        process="작성자 증명", cls="고비",
        sources=[S("r37c204b", "3.3", note="재귀 (3.4)와 $J_n(c)$ 표현의 출발점"),
                 S("rce3dc75", "3", note="명제 3.1 $J$의 보조 분해(첫 판 4.6)")],
        inputs=["{{2:J-egf}}", "{{4:old-4-6}}"],
        special="기록은 「적분 인자 해」라고만 적는다(조사 3 상신 1). $F_*$·$K$·$Q_k$의 정의에서 ODE를 적분인자로 풀어 (R7)(R8)을 유도하고 「작성자 판단」을 붙인다. 5.6의 `{{5:old-5-40}}`(전제 (I5))이 쓴다."),
    "{{4:gauss-coeff}}": dict(kind="보조정리", name="Gauss 계수의 경계(Hermite 점화식)", record_name="",
        process="옮김+재조직", cls="새로운 것",
        sources=[S("r37c204b", "4", file=EV_RC, note="증거 문서 §4(조사 3이 본문을 읽음)"),
                 S("rce3dc75", "4", note="Gauss 계수 단계")],
        inputs=["{{4:old-4-6}}", "{{4:old-4-7}}"], special="첫 판 4.3절의 전사 문단을 보조정리와 번호 단계로 다시 조직한다(지침 6절 규칙 13)."),
    "{{4:two-corrections}}": dict(kind="보조정리", name="두 보정의 수직선 적분", record_name="",
        process="옮김+재조직", cls="새로운 것",
        sources=[S("r37c204b", "4", file=EV_RC, note="증거 문서 §4"), S("rce3dc75", "5", note="두 보정")],
        inputs=["{{4:gauss-coeff}}"], special="첫 판 4.3절의 전사 문단에서 재조직."),
    # ---------------- 5장 5.2 ----------------
    "{{5:tail-poly}}": dict(kind="보조정리", name="계수 다항식의 전개", record_name="기록 [ra88ba51] §3",
        process="전개", cls="새로운 것", sources=[S("ra88ba51", "3", note="정확한 계수 다항식")], inputs=["{{2:old-2-6}}"], special="정리 5.3의 전제."),
    "{{5:rational-cert}}": dict(kind="보조정리", name="유리 상·하한 (8)(9)", record_name="기록 [ra88ba51] §4",
        process="전개", cls="새로운 것", sources=[S("ra88ba51", "4", note="무한 범위를 유한 유리 인증으로 바꾸기")], inputs=["{{5:tail-poly}}"], special=""),
    "{{5:sharp-546}}": dict(kind="보조정리", name="정밀 경계 (10)의 손 부분", record_name="기록 [ra88ba51] §6",
        process="전개", cls="새로운 것", sources=[S("ra88ba51", "6", note="문턱 546과 두 볼록 구간; 네 줄 증명")], inputs=["{{5:rational-cert}}"],
        special="546은 100개 인증서 재실행(정확 정수·유리수)의 결과로 부록 D. 「최적 시작점」 주장과 §7 종료 논증은 쓰지 않는다."),
    "{{5:green-connection}}": dict(kind="보조정리", name="$\\mathcal G_{c,h}$의 계수식과 (18)(19)", record_name="기록 [rda45d0e] §7",
        process="전개", cls="새로운 것",
        sources=[S("rda45d0e", "7", note="경계 다항식의 Green 응답과 원 b의 양의 합"), S("rda45d0e", "1", file=EV_GC, note="증거 문서 green-connection.md 전문(머리부터)")],
        inputs=["{{2:J-egf}}", "{{2:old-2-6}}"],
        special="입력 재귀 (17)은 출처 [r4daca3d]를 적고 계수 비교 한 줄로 재유도해 「작성자 판단」으로 둔다(조사 4)."),
    "{{5:source-rep}}": dict(kind="정리", name="양의 원천 표현 (P)와 원천별 비교 (G)", record_name="기록 [r708d99c]의 정리 C",
        process="전개", cls="고비", sources=[S("r708d99c", "4.1–4.2", note="표현 (P)와 원천별 비교 (G)")], inputs=["{{5:green-connection}}"],
        special="(G)의 진술을 $p_k/p_{k-1}$이 든 꼴로 적는다(첫 판의 다항식 부등식 꼴은 부정확; 조사 2). D1과 $e_-$ 유리 끼움을 적는다."),
    "{{5:cayley-ratio}}": dict(kind="보조정리", name="Cayley 비율 하계", record_name="기록 [r708d99c]의 보조정리 D1",
        process="전개", cls="표준", sources=[S("r708d99c", "5.1", note="Cayley 비율 하계")], inputs=[], special=""),
    "{{5:marked-riccati}}": dict(kind="보조정리", name="세 표시 Riccati 식과 네 용량의 회복", record_name="기록 [rbeae3a3] §3",
        process="전개", cls="새로운 것", sources=[S("rbeae3a3", "3")], inputs=["{{2:old-2-6}}"], special="타일 모형 사슬의 첫 고리(정리 5.5의 전제)."),
    "{{5:response-kernel}}": dict(kind="보조정리", name="단일 표시 응답의 양의 Hausdorff 핵", record_name="기록 [rbeae3a3] §4",
        process="전개", cls="새로운 것", sources=[S("rbeae3a3", "4")], inputs=["{{5:marked-riccati}}"], special=""),
    "{{5:fixed-size-response}}": dict(kind="보조정리", name="고정 크기 갱신 응답의 재귀", record_name="기록 [rbeae3a3] §5.1",
        process="전개", cls="새로운 것", sources=[S("rbeae3a3", "5.1")], inputs=["{{5:response-kernel}}"], special="모든 $n$의 유효성은 peer가 세움(기록 §5.1 머리)."),
    "{{5:inverse-renewal}}": dict(kind="보조정리", name="역수 형태", record_name="기록 [rbeae3a3] §5.3",
        process="전개", cls="새로운 것", sources=[S("rbeae3a3", "5.3")], inputs=["{{5:fixed-size-response}}"], special=""),
    "{{5:renewal-fkg}}": dict(kind="보조정리", name="갱신 분할점 측도의 양의 연관", record_name="기록 [rbeae3a3] §6.1",
        process="전개", cls="표준", sources=[S("rbeae3a3", "6.1", note="로그볼록 간격의 격자 조건; 8행")], inputs=["{{5:inverse-renewal}}"],
        special="FKG 부등식은 문헌 인용(Fortuin–Kasteleyn–Ginibre 1971)으로 진술만 적는다."),
    "{{5:suff-cond}}": dict(kind="정리", name="정리 5.5의 충분조건 (3.2)/(10.1)", record_name="기록 [r5ddf8a8]의 정리 2와 기록 [r0dc57fa]의 (10.1)",
        process="전개", cls="고비",
        sources=[S("r5ddf8a8", "2–3.3", note="생산자 정리 1과 peer 정리 2(경계 이득, 기울인 생일 평균의 초등 하계, 정리 2); FKG·Jensen 손 증명"),
                 S("r0dc57fa", "10.1", note="정리 꼴 (10.1)")],
        inputs=["{{5:renewal-fkg}}", "{{5:inverse-renewal}}"], special="Part A($171\\le m\\le9999$ 9829점 구간 산술)와 Part B 상수는 부록 D."),
    "{{5:lemma-L}}": dict(kind="보조정리", name="보조정리 L과 환원 단계", record_name="기록 [r0dc57fa] §10.2",
        process="전개", cls="새로운 것", sources=[S("r0dc57fa", "10.2", note="정리 T1")], inputs=["{{5:suff-cond}}"], special=""),
    "{{5:kernel-C-bound}}": dict(kind="보조정리", name="$C$·$E$의 양측 경계", record_name="기록 [r7798355]의 증거 문서 §3",
        process="전개", cls="새로운 것", sources=[S("r7798355", "3", file=EV_EC, note="effective-concavity-proof.md §3 (52행)")], inputs=["{{2:chain-normalization}}"],
        special="증거 파일에서 옮기며 출처를 적는다(지침 4.5(ㄷ)의 출처 표시 규칙)."),
    "{{5:kernel-bounds}}": dict(kind="보조정리", name="핵 계수 경계 (K1)(K2)", record_name="기록 [r690be93] §4",
        process="전개", cls="새로운 것", sources=[S("r690be93", "4", note="갱신 핵 도함수의 새 계수 경계"), S("r690be93", None, file=EV_KP, range=[1, 80], note="kernel-proof.md 전문(128행 가운데 증명 부분)")],
        inputs=["{{2:old-2-37}}"], special=""),
    "{{5:third-group}}": dict(kind="보조정리", name="셋째 묶음 비교 $\\nabla^3h_w$", record_name="기록 [r1aa0be6]의 third-group-comparison",
        process="전개", cls="고비", sources=[S("r1aa0be6", "4", note="3차 차분은 마지막 간격부터 합한다"), S("r1aa0be6", "2", file=EV_CC, note="critical-concavity.md §2 (104행)")],
        inputs=["{{2:chain-normalization}}", "{{2:chain-expansion}}"], special=""),
    "{{5:last-gap}}": dict(kind="보조정리", name="마지막 간격 비교의 인자 6/5", record_name="기록 [r690be93] §5",
        process="전개", cls="새로운 것", sources=[S("r690be93", "5")], inputs=["{{5:kernel-bounds}}"], special=""),
    "{{5:sign-sandwich}}": dict(kind="보조정리", name="부호 보존 감싸기와 꼬리", record_name="기록 [r690be93] §6",
        process="전개", cls="새로운 것", sources=[S("r690be93", "6", note="정리 TC")], inputs=["{{5:last-gap}}"], special="Bernstein 계수 부호 검사(76구간 192차; 정확 산술)는 부록 D."),
    "{{5:first-moment-weight}}": dict(kind="보조정리", name="일차 가중치의 균일 부등식 (7.1)", record_name="기록 [r690be93] §7.2",
        process="전개", cls="새로운 것", sources=[S("r690be93", "7.2")], inputs=[], special="$O(\\eta^2)$ 표기를 폐지하고 명시 나머지 $\\varepsilon_k(\\eta)$를 적는다(조사 2)."),
    "{{5:marked-recursion}}": dict(kind="보조정리", name="표시 사슬 재귀 (7.2)의 일반 $j$판", record_name="기록 [r1aa0be6]의 renewal-bounds(증거 문서 §3 식 (15))",
        process="전개", cls="새로운 것", sources=[S("r1aa0be6", "3", file=EV_LL, note="critical-local-limit.md §3 (15); 69행"), S("r690be93", "7.3", note="(7.2)의 진술 자리")],
        inputs=["{{2:chain-normalization}}"], special="출처는 [r7798355]가 아니라 [r1aa0be6]이고 주장 ID는 renewal-bounds다(조사 4 상신 3, 의존지도 v2 상신 2)."),
    "{{5:parity-tail}}": dict(kind="보조정리", name="홀짝 정규화와 꼬리", record_name="기록 [r690be93] §7.4",
        process="전개", cls="새로운 것", sources=[S("r690be93", "7.4")], inputs=["{{5:marked-recursion}}"], special="96차 Bernstein은 부록 D."),
    # ---------------- 5장 5.4 ----------------
    "{{5:weight-envelope}}": dict(kind="보조정리", name="가중치의 계수별 포락선 (3.1)–(3.5)", record_name="기록 [r13b0b8f] §3",
        process="전개", cls="새로운 것", sources=[S("r13b0b8f", "3")], inputs=["{{2:chain-expansion}}"], special="둘째 보정 (3.5)와 평균값 정리 형식을 포함한다(첫 판에 (3.5) 진술 없음)."),
    "{{5:marked-chain-rec}}": dict(kind="보조정리", name="표시 사슬 합의 생성함수 재귀 (4.1)(4.2)", record_name="기록 [r13b0b8f] §4",
        process="전개", cls="새로운 것", sources=[S("r13b0b8f", "4")], inputs=["{{5:weight-envelope}}"], special=""),
    "{{5:kernel-sandwich}}": dict(kind="보조정리", name="방문 핵의 대수적 포락선 (5.1)", record_name="기록 [r13b0b8f] §5",
        process="전개", cls="새로운 것", sources=[S("r13b0b8f", "5")], inputs=["{{2:old-2-37}}"], special="Wallis 부등식은 문헌 인용."),
    "{{5:omitted-tail}}": dict(kind="보조정리", name="생략한 사슬 길이의 꼬리 $T_j$", record_name="기록 [r13b0b8f] §6",
        process="전개", cls="새로운 것", sources=[S("r13b0b8f", "6")], inputs=["{{5:marked-chain-rec}}"], special="전제 $D_k$ 재귀를 함께 적는다."),
    "{{5:cover-edge}}": dict(kind="보조정리", name="덮개 끝 $r_*$의 엄격 증가", record_name="기록 [r13b0b8f] §9.1",
        process="전개", cls="새로운 것", sources=[S("r13b0b8f", "9.1")], inputs=["{{5:old-5-12}}"], special=""),
    "{{5:unit-circle}}": dict(kind="보조정리", name="단위원 위의 표현과 지배 A·B", record_name="기록 [ra4c01fc] §4",
        process="전개", cls="새로운 것", sources=[S("ra4c01fc", "4")], inputs=["{{2:old-2-8}}"], special=""),
    "{{5:cut-rep}}": dict(kind="보조정리", name="호 위 Borel 유한합의 절단 표현과 반직선 꼴", record_name="기록 [ra4c01fc] §5",
        process="전개", cls="새로운 것", sources=[S("ra4c01fc", "5")], inputs=["{{5:unit-circle}}"], special="구간 검증 상수(§8.4)는 부록 D."),
    "{{5:hat-normalization}}": dict(kind="보조정리", name="정규화 범함수 $\\hat{\\mathcal E}$, $\\hat{\\mathcal B}$", record_name="기록 [ra4c01fc] §6",
        process="전개", cls="새로운 것", sources=[S("ra4c01fc", "6")], inputs=["{{5:cut-rep}}"], special="§7.1의 둘러싸기 설계 상수는 부록 D 항목의 명세로."),
    # ---------------- 5장 5.6 ----------------
    "{{5:arc-leading}}": dict(kind="보조정리", name="호 위 선도 항등식 $D(\\eta)$", record_name="기록 [ra4c01fc] §8의 bulk-arc-leading-identities",
        process="전개", cls="새로운 것", sources=[S("ra4c01fc", None, range=[394, 414], note="§8 396–400행 진술과 「$D(\\eta)$의 증명」 약 10행")],
        inputs=["{{5:unit-circle}}"], special="5.40 전개의 전제(의존지도 v2 열린 입력 2)."),
    # ---------------- 6장 ----------------
    "{{6:old-7-13}}": dict(process="전개", cls="고비", sources=[S("r7e03176", "8.3", note="정리 F′: 첫 층 생존의 손 증명(85행)")], inputs=["{{2:old-2-32}}", "{{2:old-2-6}}"],
        special="첫 판에는 진술만 있다. 증명 전부를 전개한다."),
    "{{6:old-7-20}}": dict(process="전개", cls="새로운 것", sources=[S("r051bfe1", "3", note="c-sharp의 증명(109행); 정리 A, 보조정리 C·S, 결론")], inputs=["{{2:old-2-6}}"], special=""),
    "{{6:old-7-24}}": dict(process="전개", cls="새로운 것", sources=[S("r051bfe1", "5.1", note="(Hz) 위험률로 읽기(45행); 전제는 §3의 정량판")], inputs=["{{6:old-7-20}}"], special=""),
    "{{6:old-8-13}}": dict(process="전개", cls="고비", sources=[S("r98fb348", "4.2–4.6", note="체류 법칙의 증명(153행): 보조정리 C, 명제 D·E, 정리 S⁰, 정리 S")], inputs=["{{2:old-2-13}}", "{{2:old-2-43}}"], special=""),
    "{{6:old-8-11}}": dict(process="옮김+전개", cls="새로운 것", sources=[S("r7e03176", "8.2", note="평균 보조정리 A와 행 2k의 증가(한 줄)")], inputs=["{{6:old-7-13}}"],
        special="첫 판의 논증(첫 판 6.7절 2003행 부근)에 §8.2 보조정리 A 한 줄을 더해 증명을 완성한다."),
    "{{6:old-8-12}}": dict(process="옮김", cls="새로운 것", sources=[S("r7e03176", "8.5", note="같은 논증의 일반판(p-bulk-point-mass) 한 문단")], inputs=["{{6:old-8-11}}", "{{6:old-7-13}}"],
        special="첫 판 3390행에 증명이 있다(의존지도 v2 3절 (ㄴ)). 옮기면 된다."),
    "{{6:pair-rearrange}}": dict(kind="보조정리", name="짝 재배열 $\\varphi^\\flat_k=\\Pi_k-\\Upsilon_k$", record_name="기록 [r29b01e8]의 식 (4.1)",
        process="전개", cls="새로운 것", sources=[S("r29b01e8", "4.1", note="정확한 항등식(24행)")], inputs=["{{2:old-2-40}}"], special=""),
    "{{6:diag-first-layer}}": dict(kind="정리", name="(Diag) 첫 층 정리", record_name="기록 [r696d62c]의 정리 P6",
        process="전개", cls="고비",
        sources=[S("r696d62c", "2.1–2.2", note="결손의 사슬 공식, 깊이 분해"), S("r696d62c", "3", note="깊이 부류를 여는 두 항등식"), S("r696d62c", "4.1–4.6", note="한 점 삽입과 점별 지배, 모든 부류의 증가와 (Diag)")],
        inputs=["{{6:pair-rearrange}}", "{{2:old-2-13}}", "{{2:chain-expansion}}"], special="보조정리 N의 범위를 그대로 적는다."),
    "{{6:cor-L}}": dict(kind="따름정리", name="보조정리 D의 날카로운 판", record_name="기록 [r696d62c]의 따름정리 L",
        process="전개", cls="새로운 것", sources=[S("r696d62c", "5.2", note="보조정리 D의 날카로운 판과 띠 판정 경로(26행)")], inputs=["{{6:diag-first-layer}}"], special=""),
    "{{6:D-bound}}": dict(kind="정리", name="(D) 첫 층 기저의 하계 $kD_k\\ge-1-\\Upsilon_k$와 $\\hat\\Upsilon_k$", record_name="기록 [r696d62c]의 p-lemmaD-sharp, 기록 [r29b01e8]의 p-ups-bound",
        process="옮김+전개", cls="새로운 것",
        sources=[S("r696d62c", "5.2"), S("r29b01e8", "4.4", note="엄밀한 몫: 평평한 핵은 음이 아닌 합 ≥ 0.198")],
        inputs=["{{6:cor-L}}", "{{6:old-8-11}}"], special="첫 판 6.8절 2075–2081행($\\Upsilon_k$, $\\hat\\Upsilon_k$ 상계)과 7.3절 2630행의 (D)·(Υ) 서술을 여기로 옮긴다."),
    "{{6:theorem-U}}": dict(kind="정리", name="정리 U와 보조정리 ℓ·B·A·O·F·E·N", record_name="기록 [r845b205]의 정리 U",
        process="전개", cls="고비", sources=[S("r845b205", "7", note="$T_V$의 증명: 경로별 곡률 부등식에서 닫힌 꼴의 상계까지(94행)"), S("r845b205", None, range=[295, 310], note="부록 A. 정리 U의 적분 상수")],
        inputs=["{{2:old-2-43}}", "{{2:old-2-46}}"], special="Borel–Tanner 공식은 문헌 인용 또는 2.11의 보조정리로. 상수 50.6의 위합은 부록 D."),
    "{{6:path-shift}}": dict(kind="정리", name="경로 이동 항등식과 경로별 하계", record_name="기록 [r29c10cd]의 정리 1·보조정리 2",
        process="전개", cls="새로운 것", sources=[S("r29c10cd", "3.1–3.2")], inputs=["{{2:old-2-13}}"], special=""),
    "{{6:theorem-D}}": dict(kind="정리", name="정리 D·(DR)·보조정리 K", record_name="기록 [r5bbc534]의 정리 D",
        process="전개", cls="새로운 것", sources=[S("r5bbc534", "4.1–4.2", note="결손 갱신 항등식 (DR)과 정리 D(49행)")], inputs=["{{2:old-2-43}}"], special="기저 $L\\le700$은 부록 D."),
    "{{6:prop-W}}": dict(kind="명제", name="명제 W (나)(다)(라)", record_name="기록 [r29c10cd]의 명제 W",
        process="전개", cls="새로운 것", sources=[S("r29c10cd", "7.5")], inputs=["{{6:path-shift}}", "{{2:moving-tail}}"], special="(가)의 13개 검사는 부록 D."),
    "{{6:prop-R}}": dict(kind="명제", name="환원 명제 R", record_name="기록 [r9bf2dc6]의 명제 R",
        process="전개", cls="새로운 것", sources=[S("r9bf2dc6", "3")], inputs=["{{6:path-shift}}"], special=""),
    "{{6:lemma-H}}": dict(kind="보조정리", name="망원 하계와 쌍 공식: 보조정리 H", record_name="기록 [r9bf2dc6]의 보조정리 H",
        process="전개", cls="새로운 것", sources=[S("r9bf2dc6", "4.1", note="무거운 꼭짓점은 사슬이고 점확률은 두 곱의 차다"), S("r9bf2dc6", "4.3")], inputs=["{{2:old-2-45}}"], special=""),
    "{{6:lemma-Hprime}}": dict(kind="보조정리", name="닫힌 꼴: 보조정리 H′", record_name="기록 [r9bf2dc6]의 보조정리 H′",
        process="전개", cls="새로운 것", sources=[S("r9bf2dc6", "4.4")], inputs=["{{6:lemma-H}}"], special=""),
    "{{6:lemma-M}}": dict(kind="보조정리", name="단조성: 보조정리 M", record_name="기록 [r9bf2dc6]의 보조정리 M",
        process="전개", cls="새로운 것", sources=[S("r9bf2dc6", "4.5")], inputs=["{{6:lemma-Hprime}}"], special=""),
    "{{6:critical-front}}": dict(kind="명제", name="임계 창 앞쪽 조각", record_name="기록 [r7e03176] §8.5의 따름정리, 기록 [r29c10cd] §7.5",
        process="전개", cls="새로운 것", sources=[S("r7e03176", "8.5", note="E_3의 균일 상계와 창 앞쪽의 닫힘"), S("r29c10cd", "7.5")], inputs=["{{6:old-7-13}}", "{{6:prop-W}}"], special=""),
    "{{6:far-window}}": dict(kind="명제", name="먼 창 N2", record_name="기록 [r9bf2dc6] §5.1",
        process="전개", cls="새로운 것", sources=[S("r9bf2dc6", "5.1")], inputs=["{{6:prop-R}}", "{{6:lemma-M}}"], special=""),
    "{{6:small-k-bulk}}": dict(kind="명제", name="작은 $k$의 벌크 N3", record_name="기록 [r9bf2dc6] §5.2",
        process="전개", cls="새로운 것", sources=[S("r9bf2dc6", "5.2")], inputs=["{{6:prop-R}}", "{{5:old-5-1}}"], special="인증 [r19de912]는 5.1의 정리 5.1을 가리킨다."),
    "{{6:first-layer-end}}": dict(kind="명제", name="첫 층 끝 조각(명제 E (가))", record_name="기록 [r29c10cd]의 명제 E (가)",
        process="전개", cls="새로운 것", sources=[S("r29c10cd", "7.2", note="공표 결과로 닫히는 부분")], inputs=["{{6:old-7-13}}"], special=""),
    "{{6:above-window}}": dict(kind="명제", name="창 위 조각(명제 E (나))", record_name="기록 [r29c10cd]의 명제 E (나)",
        process="전개", cls="새로운 것", sources=[S("r29c10cd", "7.2")], inputs=["{{6:old-7-13}}"], special=""),
    "{{6:v-negative}}": dict(kind="명제", name="$v_m<0$ ($k\\ge3131$, $k\\le m\\le k+13$)", record_name="기록 [r29c10cd]의 명제 W (가)",
        process="전개", cls="새로운 것", sources=[S("r29c10cd", "7.5"), S("r29c10cd", "6.3", note="정리 14: k=3131의 부등식 사슬")], inputs=["{{2:moving-tail}}"],
        special="7문장 손 논증을 전개하고, $k=3131$, $d\\le13$의 부등식 13개는 값과 함께 적어 부록 D(2차 대조가 방향 반올림 구간으로 재계산)."),
    # ---------------- 7장 ----------------
    "{{7:old-6-7}}": dict(process="옮김+전개", cls="고비", sources=[S("r39ba7c1", None, range=[101, 134], note="§4.1a 두 비율을 함께 보존한다(결합 부등식의 증명)"), S("r39ba7c1", "5.1", note="방향 평균 항등식")],
        inputs=["{{7:old-6-6}}", "{{2:old-2-6}}"], special="첫 판에는 진술만 있다. 증명이 기록에만 있던 자리(116행)를 전개한다."),
    "{{7:factorial-moment}}": dict(kind="따름정리", name="계승 모멘트 하계", record_name="기록 [rb6423c6]의 factorial-moment-bound",
        process="전개", cls="새로운 것", sources=[S("rb6423c6", "10′.1", note="계승 모멘트 하계(12행)")], inputs=["{{7:old-6-6}}"], special="의존지도 v2 열린 입력 3."),
    "{{7:band-propagation}}": dict(kind="보조정리", name="띠 전파", record_name="기록 [r39ba7c1]의 band-propagation",
        process="전개", cls="표준", sources=[S("r39ba7c1", "6.1", note="유한 인증의 무한 전파: 원리(8행)")], inputs=["{{7:old-6-8}}"], special=""),
    "{{7:column-lemma}}": dict(kind="보조정리", name="열 인증 보조정리 4.1·4.2", record_name="기록 [rc9aee43]의 보조정리 4.1·4.2",
        process="전개", cls="기계적", sources=[S("rc9aee43", "4", note="열 인증 보조정리(175–203행)")], inputs=["{{7:band-propagation}}"], special="380열 144비트 정수 구간 계산(peer 160비트 재인증)은 부록 D."),
    "{{7:seed-transfer}}": dict(kind="정리", name="유한 전파 정리와 그 설정", record_name="기록 [r9e782]의 certified-left-prefix",
        process="전개", cls="새로운 것", sources=[S("r9e782", "2–3", note="부호 있는 원 차분을 여덟 비음수 급수로 옮기고 작은 음수 계수를 흡수하는 유한 전파 정리(79행)")], inputs=["{{2:old-2-6}}"],
        special="$k\\le120$, $n\\ge16$의 119개 정확 유리수 인증서는 부록 D(`producer/certificate-k*.json`). $n\\le15$의 정확 행은 5.1의 정리 5.1을 가리킨다."),
    "{{7:self-consistent-S}}": dict(kind="정리", name="골격 수준의 자기일관 상계(정리 S)", record_name="기록 [rad00a59]의 정리 S",
        process="전개", cls="고비", sources=[S("rad00a59", "2", note="조상 경로 사슬과 마지막 이탈 분해"), S("rad00a59", "5.1–5.5", note="착상, 상수, 네 전이 부등식, 정리 S와 증명, 인증한 상수")],
        inputs=["{{7:lemma-R-sc}}", "{{2:ratio-e}}", "{{7:factorial-moment}}"], special="상수 세 층(정확 유리수+mpmath 구간)은 부록 D."),
    "{{7:cor-S-prime}}": dict(kind="따름정리", name="따름정리 S′", record_name="기록 [rad00a59]의 따름정리 S′",
        process="전개", cls="새로운 것", sources=[S("rad00a59", "5.6")], inputs=["{{7:self-consistent-S}}"], special=""),
    "{{7:S-infinity}}": dict(kind="정리", name="정리 S∞", record_name="기록 [rad00a59]의 정리 S∞",
        process="전개", cls="새로운 것", sources=[S("rad00a59", "5.9")], inputs=["{{7:self-consistent-S}}"], special="$k=6098$ 한 점은 부록 D."),
    "{{7:lemma-R-sc}}": dict(kind="보조정리", name="막힌 비의 하계(보조정리 R)", record_name="기록 [rad00a59]의 보조정리 R",
        process="전개", cls="새로운 것", sources=[S("rad00a59", "3")], inputs=["{{2:old-2-6}}"], special=""),
    "{{7:old-6-11}}": dict(process="옮김+전개", cls="고비", sources=[S("rb7effe0", "3.3", note="도함수 항등식과 유한 크기 공식(정리 C; 50행)")], inputs=["{{7:riccati}}", "{{7:pole-unique}}", "{{7:pole-monotone}}", "{{7:supermultiplicative}}"], special=""),
    "{{7:riccati}}": dict(kind="명제", name="표시 생성함수와 Riccati 식(명제 3.1)", record_name="기록 [rb7effe0]의 명제 3.1",
        process="전개", cls="새로운 것", sources=[S("rb7effe0", "1.2", note="기호"), S("rb7effe0", "3.1", note="H_z 표시 생성함수; 범위는 peer 정정 $z\\ge k-1$")], inputs=["{{2:old-2-6}}"], special="peer 정정 $z\\ge k-1$을 쓴다."),
    "{{7:supermultiplicative}}": dict(kind="보조정리", name="초승법성과 $u_l\\le1$", record_name="기록 [r7c26b8b]의 보조정리 4.1",
        process="전개", cls="표준", sources=[S("r7c26b8b", "4", note="정리 1의 증명 안의 보조정리 4.1(3행)")], inputs=[], special="Fekete 보조정리는 문헌 인용."),
    "{{7:pole-unique}}": dict(kind="보조정리", name="극의 유일성과 단순성", record_name="기록 [r7c079be] §2",
        process="전개", cls="새로운 것", sources=[S("r7c079be", "2", note="원 주차 과정에서 전해석 분모까지(42행)")], inputs=["{{7:riccati}}"], special=""),
    "{{7:pole-monotone}}": dict(kind="보조정리", name="극의 단조성 $\\rho_{\\ell+1}<\\rho_\\ell$", record_name="기록 [rf09e7ef]의 fixed-bound-pole",
        process="전개", cls="새로운 것", sources=[S("rf09e7ef", None, file=EV_FB, range=[1, 40], note="fixed-bound.md §1–2(36행)"), S("rf09e7ef", "4", note="해설 §4의 극 부분")], inputs=["{{7:pole-unique}}"],
        special="증명 전문은 증거 문서에만 있다(조사 3 9a)."),
    "{{7:old-6-12}}": dict(process="옮김+전개", cls="고비", sources=[S("rf451d83", "4", note="단위원 위의 인증 부등식")], inputs=["{{7:fourier-lemmas}}", "{{7:X-cert}}"],
        special="미지지 주장 넷(c-scope, c-envelope-lemmas, c-peer-audit-Aint, c-peer-audit-envelope)은 쓰지 않는다. Part A·B 인증은 부록 D. 「X′의 귀결」 문장은 뺀다."),
    "{{7:fourier-lemmas}}": dict(kind="보조정리", name="보조정리 2–6(해석성, Faà di Bruno)", record_name="기록 [rf451d83] §4.1–4.2",
        process="전개", cls="새로운 것", sources=[S("rf451d83", "4.1–4.2")], inputs=["{{7:old-6-11}}"], special="Faà di Bruno 공식은 문헌 인용."),
    "{{7:X-cert}}": dict(kind="정리", name="정리 X-cert", record_name="기록 [rf451d83]의 정리 X-cert",
        process="전개", cls="새로운 것", sources=[S("rf451d83", "4.3")], inputs=["{{7:fourier-lemmas}}"], special=""),
    "{{7:transfer-F}}": dict(kind="정리", name="조건부 전달 정리 F와 둘째 식", record_name="기록 [rb7effe0]의 정리 F(p-transfer-R)",
        process="전개", cls="새로운 것", sources=[S("rb7effe0", "6.1", note="조건부 전달 정리(15행)")], inputs=["{{7:old-6-11}}"], special=""),
    "{{7:lemma-P-pole}}": dict(kind="보조정리", name="고정된 열의 단일 극 경계(보조정리 P)", record_name="기록 [rb7effe0]의 보조정리 P(p-lemma-P)",
        process="전개", cls="새로운 것", sources=[S("rb7effe0", "6.4", note="복소해석 손 증명(26행; 「비형식」 표지 없음)")], inputs=["{{7:pole-unique}}"], special="지위는 「증명됨」."),
    "{{7:polar-R}}": dict(kind="명제", name="극 영역 판정 사슬(명제 R)", record_name="기록 [r89eb039]의 명제 R",
        process="전개", cls="새로운 것", sources=[S("r89eb039", "3.1")], inputs=["{{7:transfer-F}}", "{{7:lemma-P-pole}}"], special="488블록·L15 인증은 부록 D(가장 빠듯한 상대 여유 $4.8\\times10^{-6}$)."),
    "{{7:polar-N}}": dict(kind="보조정리", name="보조정리 N ($\\lceil2k^{3/2}\\rceil<N^\\flat_k$)", record_name="기록 [r89eb039]의 보조정리 N",
        process="전개", cls="새로운 것", sources=[S("r89eb039", "7.2")], inputs=[], special=""),
    "{{7:polar-W}}": dict(kind="명제", name="극 영역의 왼쪽 증가(명제 W)", record_name="기록 [r89eb039] §7.3",
        process="전개", cls="고비", sources=[S("r89eb039", "7.3")], inputs=["{{7:polar-R}}", "{{7:polar-N}}"], special="극 영역은 이 명제로만 닫는다(첫 판 1885행의 「X′의 귀결」 문장은 뺌)."),
    "{{7:old-6-13}}": dict(process="옮김+전개", cls="고비", sources=[S("r475ada3", "3–6", note="구조(블록 지수 공식·사슬 초과 항등식·쌍별 볼록성), 해석적 사슬, 정수 전용 인증, 정리 S(210행)"), S("r6b37c7e", "3", note="띠 n−2k≤102의 증명(169행): 재귀, 보조정리 T1·T·P♯, 정리 4.A·4.B")],
        inputs=["{{7:old-6-2}}", "{{2:old-2-40}}"], special="판정 항 $q_j$의 정의·값·유도(§3.5, 8행)를 적는다. 정수 인증·유리수 감사는 부록 D. 기호 충돌 셋($A_s$, $\\rho_s$, $\\delta_s$)은 장부 v2의 글자로."),
    "{{7:moment-recursion}}": dict(kind="보조정리", name="최대 원소 분해와 모멘트 재귀", record_name="기록 [r10ff8c2] §2.1",
        process="전개", cls="새로운 것", sources=[S("r10ff8c2", "2.1")], inputs=["{{2:old-2-6}}"], special=""),
    "{{7:variance-formula}}": dict(kind="보조정리", name="전분산 공식(마디별 분산–포화 분해)", record_name="기록 [r10ff8c2] §2.2",
        process="전개", cls="새로운 것", sources=[S("r10ff8c2", "2.2")], inputs=["{{7:moment-recursion}}"], special=""),
    "{{7:error-induction}}": dict(kind="보조정리", name="사전 오차 상계의 귀납", record_name="기록 [r10ff8c2] §3.1의 손 부분",
        process="전개", cls="새로운 것", sources=[S("r10ff8c2", "3.1")], inputs=["{{7:variance-formula}}"], special="(A1)–(A5) 7,700열 binary64는 부록 D."),
    "{{7:theorem-C-moment}}": dict(kind="정리", name="정리 C(공표 인증서와의 결합)", record_name="기록 [r10ff8c2]의 정리 C",
        process="전개", cls="새로운 것", sources=[S("r10ff8c2", "3.2")], inputs=["{{7:error-induction}}", "{{7:factorial-moment}}"], special="정리 D 1160열 정확 유리수 재계산은 부록 D."),
    "{{7:fold-A}}": dict(kind="명제", name="원천의 세 조각(명제 A)", record_name="기록 [r207f124] §2",
        process="전개", cls="새로운 것", sources=[S("r207f124", "2")], inputs=["{{2:old-2-40}}"], special=""),
    "{{7:fold-R}}": dict(kind="명제", name="대각선 접기(명제 R)", record_name="기록 [r207f124] §3",
        process="전개", cls="고비", sources=[S("r207f124", "3")], inputs=["{{7:fold-A}}"], special=""),
    "{{7:fold-T}}": dict(kind="보조정리", name="이동 부등식(명제 T)", record_name="기록 [r207f124] §5.4",
        process="전개", cls="새로운 것", sources=[S("r207f124", "5.4")], inputs=["{{2:old-2-31}}"], special=""),
    "{{7:fold-L1}}": dict(kind="정리", name="모든 $n$의 원천 하계(정리 L1*)", record_name="기록 [r207f124]의 정리 L1*",
        process="전개", cls="새로운 것", sources=[S("r207f124", "6.1")], inputs=["{{7:fold-R}}", "{{7:fold-T}}"], special=""),
    "{{7:fold-DIP}}": dict(kind="따름정리", name="생존 감소 판정 DIP", record_name="기록 [r207f124]의 따름정리 DIP",
        process="전개", cls="새로운 것", sources=[S("r207f124", "6.2")], inputs=["{{7:fold-L1}}"], special=""),
    "{{7:polar-PD}}": dict(kind="정리", name="정리 PD(극 영역의 공급)", record_name="기록 [r207f124]의 정리 PD",
        process="전개", cls="새로운 것", sources=[S("r207f124", "6.8", note="극 영역: 공표 갱신 인증서가 생존 감소를 공급한다")], inputs=["{{7:X-cert}}", "{{7:fold-DIP}}"], special="입력 X-cert와 $\\sigma>4.57$ 하계는 7.3. 정리 Q-fin(1130열)은 부록 D(오기 $e^{3/25370}$은 바른 하계 25233)."),
    "{{7:prop-PF}}": dict(kind="명제", name="첫 층 쪽 판정(명제 PF)", record_name="기록 [r207f124]의 명제 PF",
        process="전개", cls="새로운 것", sources=[S("r207f124", "6.8")], inputs=["{{7:polar-PD}}"], special=""),
    "{{7:old-6-17}}": dict(process="옮김+전개", cls="고비",
        sources=[S("r79ee9e0", "2.2–2.3", note="뿌리 법칙의 정확한 대칭, 정리 T"), S("r79ee9e0", "3", note="한 걸음 결합과 두 단조성의 초등 증명"), S("r79ee9e0", "4", note="크기 방향 위험률의 하계: 바닥, 위험률 항등식, 명시 경계들, 정리 H*"), S("r79ee9e0", "5.1–5.3", note="원천 쪽의 완결: 여러 꼭대기 뿌리 판, 정리 W, 결론")],
        inputs=["{{2:old-2-32}}", "{{2:old-2-33}}", "{{7:polar-PD}}"], special="(가) 위험률 항등식·정리 H*와 전제 사슬 약 210행 전개(기록 오기 3.8267→3.8249, 0.99988→0.999875는 바른 값으로). (나) 정리 PD는 7.5를 가리킴. 손 증명은 $k\\ge3131$에 한함을 진술에."),
    "{{7:src-plus}}": dict(kind="명제", name="SRC⁺", record_name="기록 [r79ee9e0] §6.1",
        process="전개", cls="새로운 것", sources=[S("r79ee9e0", "6.1", note="원천 쪽 증명이 쓰는 조각(21행)")], inputs=["{{7:old-6-17}}"], special=""),
    # ---------------- 8장 ----------------
    "{{8:jensen-lower}}": dict(kind="보조정리", name="Jensen 하계(보조정리 W)", record_name="기록 [r8456f59]의 보조정리 W",
        process="전개", cls="새로운 것", sources=[S("r8456f59", "4.1", note="heavy path 초과 면적의 평균(9행)")], inputs=["{{2:old-2-13}}"], special=""),
    "{{8:escape-lower}}": dict(kind="정리", name="기하 탈출 하계(정리 G)", record_name="기록 [r8456f59]의 정리 G",
        process="전개", cls="새로운 것", sources=[S("r8456f59", "4.2", note="기하 탈출 하계(7행)")], inputs=["{{8:jensen-lower}}"], special=""),
    "{{8:lowest-violation}}": dict(kind="명제", name="가장 낮은 위반 (V)", record_name="기록 [r8456f59] §4.7",
        process="전개", cls="새로운 것", sources=[S("r8456f59", "4.7", note="창 극한 방정식의 정확한 유한판(22행)")], inputs=["{{8:old-6-23}}"], special=""),
    "{{8:prop-U-apriori}}": dict(kind="명제", name="명제 U(사전 상계)", record_name="기록 [r8456f59]의 명제 U",
        process="전개", cls="새로운 것", sources=[S("r8456f59", "4.7")], inputs=["{{8:lowest-violation}}"], special=""),
    "{{8:envelope-H}}": dict(kind="보조정리", name="원천 봉투의 보조정리 H", record_name="기록 [r030ffae]의 보조정리 H",
        process="전개", cls="고비", sources=[S("r030ffae", "3.5", note="원천 봉투 Q^env"), S("r030ffae", "3.9.2", file=EV_RP030, note="보고서 §3.9.2 k에 무관한 원천 봉투")],
        inputs=["{{8:old-6-23}}", "{{8:escape-lower}}"], special="식 4·정의 3·증명 1문단. 보고서 §3.9.2에서 옮기고 출처를 적는다."),
    "{{8:envelope-HG}}": dict(kind="보조정리", name="원천 봉투의 보조정리 H-G(여섯 조각)", record_name="기록 [r030ffae]의 보조정리 H-G",
        process="전개", cls="고비", sources=[S("r030ffae", "3.5"), S("r030ffae", "3.9.2", file=EV_RP030), S("r030ffae", None, file="evidence/peer/rerun/work/window_lib.py", range=[140, 205], note="`G_pieces`·`E_envG_rigorous`의 docstring(여섯 조각의 식); 기록 폴더 바로 아래의 파일")],
        inputs=["{{8:envelope-H}}"], special="여섯 조각 $P,R_1,R_2,D_1,D_2,D_3$의 식 전부를 적는다. 그 뒤의 $y$-감소성·$k$-단조성은 자리 표시자(지침 4.7)."),
    "{{8:old-6-28}}": dict(process="옮김+전개", cls="고비", sources=[S("r030ffae", "3.6–3.7", note="큰 b의 단조 경계와 셀 경계, 시험 함수와 인증 결과, 정리 W")], inputs=["{{8:envelope-H}}", "{{8:envelope-HG}}", "{{8:lowest-violation}}"],
        special="(가)·(나) 셀 검사와 12001점 표는 부록 D(binary64 평가, 인증 아님). 증명의 둘째 단계에 `[todo]` 자리 표시자."),
    "{{8:hazard-H1}}": dict(kind="보조정리", name="첫 층 위험률의 명시 하계(정리 H1(a))", record_name="기록 [r5bbc534]의 정리 H1",
        process="전개", cls="새로운 것", sources=[S("r5bbc534", "5.2", note="정리 H1과 보조정리 𝔇(약 20행)")], inputs=["{{6:old-7-24}}"], special="6.33 증명의 위험률 다듬기($0.44k<\\nu\\le0.48k$)가 쓴다(의존지도 v2 열린 입력 1)."),
    # ---------------- 9장 ----------------
    "{{9:F5-upper}}": dict(kind="보조정리", name="$F_5\\le v/(v+1)$", record_name="기록 [r23f10e9] §5.8",
        process="전개", cls="표준", sources=[S("r23f10e9", None, range=[394, 402], note="§5.8 398행의 이항 전개 한 줄")], inputs=["{{5:old-5-28}}"], special="정리 5.28의 증명이 하계 방향만 적으므로 상계 한 줄을 더한다."),
    "{{9:theorem-A-plus}}": dict(kind="정리", name="정리 A⁺(경로마다의 위쪽 대각 판)", record_name="기록 [rc391829]의 정리 A⁺",
        process="전개", cls="새로운 것", sources=[S("rc391829", "6.5", note="경로마다의 위쪽 대각 판과 머리 합 조건(17행)")], inputs=["{{5:old-5-28}}", "{{9:F5-upper}}"], special="그 밖의 전제 셋은 정리 5.28 증명에 있다(조사 4)."),
    "{{9:prop-H}}": dict(kind="명제", name="명제 H와 명제 HC(기준점 족)", record_name="기록 [rc391829]의 명제 H·HC",
        process="전개", cls="새로운 것", sources=[S("rc391829", "4", note="기준점 족과 머리 합 판정(6행)")], inputs=["{{9:theorem-A-plus}}"], special=""),
    "{{9:head-sum-1}}": dict(kind="정리", name="머리 합의 부호: 정리 1", record_name="기록 [r2ec875c]의 정리 1",
        process="전개", cls="고비", sources=[S("r2ec875c", "4.1–4.4", note="정리 A⁺로 대각 몫을 막기, 무거운 사슬, 명시적 양측 경계, 창 안의 최종 부등식(136행)")], inputs=["{{9:theorem-A-plus}}", "{{9:prop-H}}", "{{2:old-2-40}}", "{{2:old-2-43}}"],
        special="Ψ 상수는 peer 정정값 $0.7978\\sqrt D-0.8848$, 끝점 0.83102."),
    "{{9:head-sum-2}}": dict(kind="정리", name="$m_1(k)$의 두 상계: 정리 2", record_name="기록 [r2ec875c]의 정리 2",
        process="전개", cls="새로운 것", sources=[S("r2ec875c", "4.5", note="m₁(k)의 상계; M0·M2 손 12행")], inputs=["{{9:head-sum-1}}", "{{5:old-5-1}}"], special="M1($3132\\le k\\le19403$)은 정리 5.1 인증 파일의 열 판독(위반 0, 최대 0.7095)으로 부록 D."),
    "{{9:H-star}}": dict(kind="따름정리", name="머리 합 조건 $H^*$", record_name="기록 [r2ec875c]의 따름정리 H*, 기록 [rc391829]의 머리 합 조건",
        process="전개", cls="새로운 것", sources=[S("r2ec875c", "2", note="결과(29–45행)")], inputs=["{{9:head-sum-1}}", "{{9:head-sum-2}}"], special="첫 판 6.8절 2071행의 머리 합·출발 빚·빚 뺀 머리 합·증가 시작점 $m_1(k)$ 정의를 이 절 머리로 옮긴다."),
    "{{9:H-star-plus}}": dict(kind="정리", name="정량판 $H^*_+$(머리 합 여유 정리)", record_name="기록 [r33475a7]의 머리 합 여유 정리",
        process="전개", cls="새로운 것", sources=[S("r33475a7", "5.4", note="머리 합 여유 정리; s=k+1 손 6행")], inputs=["{{9:H-star}}"], special="$s\\ge k+2$는 충분조건 $G(X,w)\\le\\Theta$의 식과 세 영역을 적고 방향 반올림 구간 산술을 부록 D."),
    "{{9:centroid-stop}}": dict(kind="보조정리", name="무게중심 정지 확률", record_name="기록 [r2fe0259] §3.3",
        process="전개", cls="새로운 것", sources=[S("r2fe0259", "3.3", note="사슬은 무게중심에서만 멈춘다(36행)")], inputs=["{{2:old-2-13}}", "{{2:old-2-44}}"], special="9.2의 보조정리 7.2와 9.3의 정리 7.16이 쓴다."),
    "{{9:regeneration-S}}": dict(kind="명제", name="재생 항등식 (S)와 $\\mathcal X_n\\ge0$", record_name="기록 [r05cf8c9]의 명제 4",
        process="전개", cls="새로운 것", sources=[S("r05cf8c9", "1.2–1.3", note="지수 공식과 한 나무 둘째 차분, 첫 차수 항과 교차항"), S("r05cf8c9", "2.1", note="숲–나무 재생 항등식과 충분조건 (FS)")], inputs=["{{2:old-2-40}}"], special=""),
    "{{9:old-7-10}}": dict(process="작성자 증명", cls="고비", sources=[S("r77e234e", "7", note="쌍 항: 보조정리 P, F, L(두 문장 근거)")], inputs=["{{2:old-2-40}}", "{{2:old-2-41}}"],
        special="기록의 두 문장 근거를 2.10절의 생성함수로 펼쳐 증명을 쓰고 「작성자 판단」을 붙인다(K5)."),
    "{{9:old-7-12}}": dict(process="옮김+전개", cls="새로운 것", sources=[S("r77e234e", "7", note="보조정리 F")], inputs=["{{6:old-7-13}}"], special=""),
    # ---------------- 5장 옮김+전개 ----------------
    "{{5:old-5-3}}": dict(process="옮김+전개", cls="고비", sources=[S("ra88ba51", "3"), S("ra88ba51", "4"), S("ra88ba51", "6")], inputs=["{{5:tail-poly}}", "{{5:rational-cert}}", "{{5:sharp-546}}"], special="첫 판에는 결과식만 있다."),
    "{{5:old-5-4}}": dict(process="옮김+전개", cls="고비", sources=[S("r708d99c", "4.1–4.2"), S("r708d99c", "5.1")], inputs=["{{5:source-rep}}", "{{5:cayley-ratio}}", "{{5:green-connection}}"], special=""),
    "{{5:old-5-5}}": dict(process="옮김+전개", cls="고비", sources=[S("r5ddf8a8", "2–3.3"), S("r0dc57fa", "10.1–10.2")], inputs=["{{5:suff-cond}}", "{{5:lemma-L}}", "{{5:marked-riccati}}", "{{5:renewal-fkg}}"], special="Part A·B 계산은 부록 D."),
    "{{5:old-5-6}}": dict(process="옮김+전개", cls="고비", sources=[S("r690be93", "6")], inputs=["{{5:kernel-C-bound}}", "{{5:kernel-bounds}}", "{{5:third-group}}", "{{5:last-gap}}", "{{5:sign-sandwich}}"], special=""),
    "{{5:old-5-7}}": dict(process="옮김+전개", cls="고비", sources=[S("r690be93", "7.2"), S("r690be93", "7.3"), S("r690be93", "7.4")], inputs=["{{5:first-moment-weight}}", "{{5:marked-recursion}}", "{{5:parity-tail}}"], special="96차 Bernstein은 부록 D."),
    "{{5:old-5-12}}": dict(process="옮김+전개", cls="고비", sources=[S("r13b0b8f", "3"), S("r13b0b8f", "4"), S("r13b0b8f", "5"), S("r13b0b8f", "6"), S("r13b0b8f", "7"), S("r13b0b8f", "8")], inputs=["{{5:weight-envelope}}", "{{5:marked-chain-rec}}", "{{5:kernel-sandwich}}", "{{5:omitted-tail}}"], special="정리 A·A⁺의 인증은 부록 D."),
    "{{5:old-5-13}}": dict(process="옮김+전개", cls="고비", sources=[S("ra4c01fc", "4"), S("ra4c01fc", "5"), S("ra4c01fc", "6"), S("ra4c01fc", "7")], inputs=["{{5:unit-circle}}", "{{5:cut-rep}}", "{{5:hat-normalization}}"], special="§7.1 설계 상수와 덮개 결과는 부록 D."),
    "{{5:old-5-40}}": dict(process="옮김+전개", cls="고비", sources=[S("r5f5cf73", "5", note="보조정리 H(η)"), S("r5f5cf73", "3.1", note="공표 분해")], inputs=["{{5:old-5-39}}", "{{4:e-integral}}", "{{5:arc-leading}}"], special="전 영역 구간 산술은 부록 D."),
    "{{5:old-5-41}}": dict(process="옮김+전개", cls="고비", sources=[S("r5f5cf73", "6.1–6.5", note="수직선 표현, Borel 꼬리의 균일 전개, Dawson 세 사실, D 부분, J 부분")], inputs=["{{5:old-5-40}}"],
        special="단항식 계수표는 존재하지 않는다. 알고리즘(전개·세 기법·닫힌 꼴 모멘트)과 산술 층·덮개 결과(잎 193, 최소 0.0466)를 부록 D에 명세. notes-lemmaV.md의 중간값은 쓰지 않고 최종판($c_I=2.04$, 앞인자 3)만."),
    # ---------------- 3장 ----------------
    "{{3:old-3-1}}": dict(process="옮김", cls="표준", sources=[], inputs=[], special="극한 진술은 Petersson의 정리를 저자·논문·Theorem 번호로 인용(지침 4.3). 대응은 증명."),
    "{{3:old-3-2}}": dict(process="옮김", cls="새로운 것", sources=[S("r81e7051", None, file="limiting-shape.md", range=[20, 50], note="곱 표현의 증명(§2 26–46행); 기록 폴더 바로 아래의 파일")], inputs=["{{3:old-3-1}}"],
        special="멜린 변환은 Janson arXiv:1002.4135 Theorem 1.12를 문헌 인용하고, 곱 표현의 증명은 첫 판 873행의 논증을 옮긴다(의존지도 v2 3절 (ㄹ))."),
}


def apply(ch):
    path = os.path.join(SPEC, f"장{ch}.json")
    spec = json.load(io.open(path, encoding="utf-8"))
    n = 0
    for sec in spec["sections"]:
        for it in sec["items"]:
            f = FIX.get(it["label"])
            if not f:
                continue
            n += 1
            for k, v in f.items():
                if k == "cls":
                    it["class"] = v
                else:
                    it[k] = v
            it.pop("cell", None)
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(spec, ensure_ascii=False, indent=1))
    unfixed = [it["label"] for sec in spec["sections"] for it in sec["items"] if it.get("process") == "전개" and it["label"] not in FIX]
    print(f"장{ch}: 덧씌움 {n}; 확정 안 된 새 진술 {len(unfixed)} {unfixed}")


if __name__ == "__main__":
    chs = [int(a) for a in sys.argv[1:]] or list(range(1, 12))
    for ch in chs:
        apply(ch)
