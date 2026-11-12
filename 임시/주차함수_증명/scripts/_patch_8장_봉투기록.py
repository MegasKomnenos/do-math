# -*- coding: utf-8 -*-
"""봉투 단조성 기록 [rfc69320](2026-11-12 공표)으로 8장의 `[todo]` 자리를 채우는 명세·META·구조표 패치(합의 v2 결정 15).

- 명세v2_수정.py: 8.2에 새 라벨 일곱(전개)을 더하고 정리 W(`{{8:old-6-28}}`)의 입력·특별 지시를 고친다.
- 명세v2_META.py: META[8]의 weights·scope·intros 8.2·order 8.2·todo(빈 목록)·D_items(저장 표의 구간 산술 확인)를 덮어쓰는 블록을 apply() 앞에 넣는다.
- 구조표_v2.md: 8.2 행의 자리 표시자 문장을 새 라벨 목록으로, 부록 B 행에 rfc69320 추가.
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- 명세v2_수정.py
P1 = os.path.join(ROOT, "scripts", "명세v2_수정.py")
s = io.open(P1, encoding="utf-8").read()

NEW_FIX = r'''    "{{8:pieces-k-monotone}}": dict(kind="정리", name="여섯 조각의 $k$-단조성(정리 B)", record_name="기록 [rfc69320]의 정리 B",
        process="전개", cls="새로운 것", sources=[S("rfc69320", "4", note="여섯 조각 $P,R_1,R_2,D_2,D_3$의 $k$-감소와 $D_1$의 $k$-증가; 로그 도함수 여섯 개(15행)")], inputs=["{{8:envelope-HG}}"],
        special="실수 $k\\ge6600$, $y\\in[0.2,6.001]$. 검토가 다시 계산한 조건식과 상수(review/feedback.md §2.2)를 쓴다."),
    "{{8:escape-y-monotone}}": dict(kind="정리", name="탈출 봉투의 $y$-비증가(정리 A)", record_name="기록 [rfc69320]의 정리 A와 보조정리 1–3",
        process="전개", cls="고비", sources=[S("rfc69320", "3", note="연속 꼴, 정규화 $U$·$V$, 보조정리 1(초등 사실)·2($U'\\ge0.7202$)·3($k^{1/3}V'\\le-0.343$), 정리 A(80행)")], inputs=["{{8:envelope-HG}}", "{{8:pieces-k-monotone}}"],
        special="혼합 몫 $q_{k,k'}$의 정의와 $\\max(0,\\min)=\\min(\\max(0,\\cdot))$ 단계까지 모두 적는다. 보조정리 2의 최솟값은 검토 정정값 0.7202097(본문은 0.7202)."),
    "{{8:jensen-H-ii}}": dict(kind="정리", name="Jensen 쪽 보조정리 H(ii)의 점검과 정정(정리 C)", record_name="기록 [rfc69320]의 정리 C",
        process="전개", cls="새로운 것", sources=[S("rfc69320", "5", note="Bpart의 $k$-증가(기록 논증의 완결성), Corr의 합친 로그 도함수와 인자별 논증이 틀리는 분할점(20행)")], inputs=["{{8:envelope-H}}"],
        special="기록 [r030ffae]의 인자별 논증이 틀린 자리는 적지 않고(결정 10·17), 성립하는 증명(합친 로그 도함수 $19/(6k)-7/(2(k+1))$)만 적는다."),
    "{{8:table-lower-bound}}": dict(kind="정리", name="끼움 정리와 표의 하계 성질(정리 D·따름정리)", record_name="기록 [rfc69320]의 정리 D와 따름정리",
        process="전개", cls="고비", sources=[S("rfc69320", "6", note="$\\tilde Q$의 정의, (a) 비증가 (b) $Q^{\\mathrm{env}}\\le\\tilde Q$ (c) 공표 부등식과의 결합, 따름정리(표의 하계 성질)(34행)")],
        inputs=["{{8:envelope-H}}", "{{8:envelope-HG}}", "{{8:pieces-k-monotone}}", "{{8:escape-y-monotone}}", "{{8:jensen-H-ii}}"],
        special="표 호출 범위는 $[0,6]$(검토 정정; 기록의 「$[0,6)$ 안」이 아님)."),
    "{{8:envelope-code-monotone}}": dict(kind="명제", name="코드 봉투의 $y$-감소와 표 함수의 엄격 감소(명제 E·F)", record_name="기록 [rfc69320]의 명제 E·F와 7.2의 정정 비고",
        process="전개", cls="새로운 것", sources=[S("rfc69320", "7", note="명제 E(고정 분할 구간의 엄격 감소), 7.2 미끄러지는 분할의 역행과 그 경계, 명제 F(표 함수의 엄격 감소)(36행)")],
        inputs=["{{8:escape-y-monotone}}", "{{8:jensen-H-ii}}", "{{8:table-lower-bound}}"],
        special="명제 F의 이음새 경우($y_1<0.2\\le y_2$)는 기록의 부등식이 아니라 명제 E의 이음새 수치($Q_G\\le0.9234<0.9533\\le Q_W$)로 닫는다(검토 feedback §4 (d))."),
    "{{8:closed-form-envelope}}": dict(kind="정리", name="참 봉투의 닫힌 꼴(명제 W*·G*, 정리 CF, 보조정리 8.1)", record_name="기록 [rfc69320]의 명제 W*·G*·정리 CF(peer)",
        process="전개", cls="고비", sources=[S("rfc69320", "8.2–8.3", note="보조정리 8.1($V$ 하계·$U$ 상계), 명제 W*(Jensen 상한은 $k=\\infty$), 명제 G*(탈출 하한은 $k=6600$), 정리 CF(51행)")],
        inputs=["{{8:pieces-k-monotone}}", "{{8:escape-y-monotone}}", "{{8:jensen-H-ii}}", "{{8:table-lower-bound}}"],
        special="정리 CF (c)는 정리 B(`{{8:pieces-k-monotone}}`)의 $R_2$ 단조성과 미분식을 쓴다(검토 정정; 기록의 「정리 B를 쓰지 않는다」는 틀림). 반올림 방향이 틀린 수치 0.031497·0.531675·0.4696은 검토가 준 방향으로 적는다."),
    "{{8:table-tolerance}}": dict(kind="보조정리", name="저장된 binary64 표의 허용 오차(보조정리 8.2·8.3)", record_name="기록 [rfc69320]의 보조정리 8.2·8.3(peer)",
        process="전개", cls="새로운 것", sources=[S("rfc69320", "8.5–8.6", note="$\\tilde Q$의 감소 속도 $r_G$, 허용 오차 보조정리, 저장된 수의 정확 확인(37행)")],
        inputs=["{{8:closed-form-envelope}}", "{{8:table-lower-bound}}"],
        special="저장값 $v_i\\le Q^{\\mathrm{cf}}(x_{i+1})$의 구간 산술 확인(§8.4)은 부록 D `{{D:stored-table-check}}`로 보내고 본문에는 그 결과를 쓰는 한 문장만 둔다. $\\Delta=6.6439\\cdot10^{-6}$, $q\\ge0.020045$의 반올림 방향은 검토의 값으로."),
'''
anchor = '    "{{8:hazard-H1}}": dict('
assert s.count(anchor) == 1
if "{{8:pieces-k-monotone}}" not in s:
    s = s.replace(anchor, NEW_FIX + anchor)

old_w_start = s.index('    "{{8:old-6-28}}": dict(')
old_w_end = s.index('자리 표시자."),', old_w_start) + len('자리 표시자."),')
NEW_W = r'''    "{{8:old-6-28}}": dict(process="옮김+전개", cls="고비", sources=[S("r030ffae", "3.6–3.7", note="큰 b의 단조 경계와 셀 경계, 시험 함수와 인증 결과, 정리 W")],
        inputs=["{{8:envelope-H}}", "{{8:envelope-HG}}", "{{8:lowest-violation}}", "{{8:table-lower-bound}}", "{{8:envelope-code-monotone}}", "{{8:table-tolerance}}"],
        special="(가)·(나) 셀 검사와 12001점 표는 부록 D(binary64 평가, 인증 아님). 증명의 둘째 단계(표의 마디값이 하계임을 쓰는 자리)는 `{{8:table-lower-bound}}`·`{{8:table-tolerance}}`를 인용한다(자리 표시자 없음; 합의 v2 결정 15의 기록이 공표됨)."),'''
s = s[:old_w_start] + NEW_W + s[old_w_end:]
io.open(P1, "w", encoding="utf-8", newline="\n").write(s)
print("명세v2_수정.py patched")

# ---------------------------------------------------------------- 명세v2_META.py
P2 = os.path.join(ROOT, "scripts", "명세v2_META.py")
t = io.open(P2, encoding="utf-8").read()
OVERRIDE = r'''
# 2026-11-12 저녁: 봉투 단조성 기록 [rfc69320] 공표에 따른 8장 갱신(합의 v2 결정 15; 자리 표시자 소멸)
_m8 = META[8]
_m8["scope"] = _m8["scope"].replace("봉투 보조정리 H·H-G, 정리 W", "봉투 보조정리 H·H-G, 봉투의 두 단조성·끼움·닫힌 꼴·허용 오차, 정리 W")
_m8["weights"] = ("고비는 8.2의 정리 W와 봉투 정리들(탈출 봉투의 $y$-비증가, 끼움 정리, 닫힌 꼴 봉투), 8.4의 띠 정리다. "
                  "봉투 식 전부(식 4+정의 3, 여섯 조각 6)와 두 단조성·끼움·닫힌 꼴·허용 오차의 증명을 본문에 적고, (가)·(나) 셀 검사·12001점 표·저장 표의 구간 산술 확인은 부록 D.")
_m8["intros"]["8.2"] = ("순서: `{{8:jensen-lower}}` → `{{8:escape-lower}}` → `{{8:lowest-violation}}` → `{{8:prop-U-apriori}}` → `{{8:envelope-H}}` → `{{8:envelope-HG}}` → "
                        "`{{8:pieces-k-monotone}}` → `{{8:escape-y-monotone}}` → `{{8:jensen-H-ii}}` → `{{8:table-lower-bound}}` → `{{8:envelope-code-monotone}}` → `{{8:closed-form-envelope}}` → `{{8:table-tolerance}}` → 정리 W(`{{8:old-6-28}}`). "
                        "봉투 정리 일곱은 기록 [rfc69320](2026-11-12 공표; 검토가 13개 주장 전부 지지)에서 전개한다. 그 검토(`review/feedback.md` §2·§4)가 정정한 것을 따른다: 표 호출 범위 $[0,6]$, 명제 F 이음새 경우의 닫기, 정리 CF (c)의 의존(정리 B를 씀), 반올림 방향이 틀린 수치 다섯. "
                        "같은 요청의 독립 둘째 증명 기록 [r0e82912]는 쓰지 않고 인용하지 않는다(결정 10). 보조정리 H·H-G의 식은 기록 §3.5와 보고서 §3.9.2·`window_lib.py`의 docstring에서 옮기고 출처를 적는다.")
_m8["order"]["8.2"] = ["{{8:jensen-lower}}", "{{8:escape-lower}}", "{{8:lowest-violation}}", "{{8:prop-U-apriori}}", "{{8:envelope-H}}", "{{8:envelope-HG}}",
                       "{{8:pieces-k-monotone}}", "{{8:escape-y-monotone}}", "{{8:jensen-H-ii}}", "{{8:table-lower-bound}}", "{{8:envelope-code-monotone}}", "{{8:closed-form-envelope}}", "{{8:table-tolerance}}", "{{8:old-6-28}}"]
_m8["todo"] = []
_m8["D_items"].append({"label": "{{D:stored-table-check}}", "for": "{{8:table-tolerance}}",
                       "sources": [{"record": "rfc69320", "note": "§8.4 저장된 표의 엄밀한 확인(mpmath 구간 산술, 바깥쪽 반올림 30자리; 위반 0, 최소 여유 4.74e-13)과 §10.3 재현; 자료: evidence/peer/peer_table_vs_closed_form.py·.out, peer_closed_form_constants.py·.out, peer_constants.py·.out; 검토의 독립 재현 review/evidence/rv_code_exact.py·.out, rv_constants.py·.out. 산술 등급: 방향 반올림 구간(저장값은 정확 유리수)"}]})
_m8["notes"] = _m8["notes"] + ["8.2의 봉투 정리 일곱은 기록의 글자($Q^{\\mathrm{env}}_G$, $P,R_1,R_2,D_1,D_2,D_3$, $q_{k,k'}$, $U$, $V$, $\\mathrm{Bpart}$, $\\mathrm{Corr}$, $B_\\infty$, $E^*$, $\\hat E$, $\\tilde Q$, $Q^{\\mathrm{cf}}$, $\\Lambda^+$, $r_G$ 등)을 장부 v2의 글자로 옮겨 쓴다. 장부에 자리가 없는 기호는 8장 여유 글자에서 고르고 대조 파일에 적는다(사전의 기록 대조가 이 기록을 덮는다)."]

'''
anchor2 = "def apply(ch):"
assert t.count(anchor2) == 1
if "rfc69320" not in t:
    t = t.replace(anchor2, OVERRIDE + anchor2)
io.open(P2, "w", encoding="utf-8", newline="\n").write(t)
print("명세v2_META.py patched")

# ---------------------------------------------------------------- 구조표_v2.md
P3 = os.path.join(ROOT, "구조표_v2.md")
u = io.open(P3, encoding="utf-8").read()
old_cell = "**`[todo: 탈출 봉투의 $y$-감소성과 여섯 조각의 $k$-단조성]`**(합의 v2 결정 15; 인스턴스 요청의 결과로 채움), 6.28(정리 W; (가)·(나) 셀 검사와 12001점 표는 부록 D) | 첫 판 6.9, [r8456f59], [r030ffae] §3.5·보고서 §3.9.2 | 옮김+전개+자리 표시자 |"
new_cell = ("새 `{{8:pieces-k-monotone}}` 여섯 조각의 $k$-단조성(정리 B) [rfc69320] §4(15행), `{{8:escape-y-monotone}}` 탈출 봉투의 $y$-비증가(정리 A·보조정리 1–3) §3(80행), `{{8:jensen-H-ii}}` 보조정리 H(ii)의 점검·정정(정리 C) §5(20행), "
            "`{{8:table-lower-bound}}` 끼움 정리와 표의 하계 성질(정리 D·따름정리) §6(34행), `{{8:envelope-code-monotone}}` 코드 봉투·표 함수의 감소(명제 E·F) §7(36행), `{{8:closed-form-envelope}}` 닫힌 꼴 봉투(명제 W*·G*, 정리 CF, 보조정리 8.1) §8.2–8.3(51행), "
            "`{{8:table-tolerance}}` 허용 오차 보조정리 8.2·8.3 §8.5–8.6(37행); 저장 표의 구간 산술 확인 §8.4는 부록 D `{{D:stored-table-check}}`(합의 v2 결정 15의 자리를 2026-11-12 공표 기록으로 채움), "
            "6.28(정리 W; (가)·(나) 셀 검사와 12001점 표는 부록 D) | 첫 판 6.9, [r8456f59], [r030ffae] §3.5·보고서 §3.9.2, [rfc69320] | 옮김+전개 |")
assert u.count(old_cell) == 1
u = u.replace(old_cell, new_cell)
old_b = "새로 드는 기록(rba2ecf, rbeae3a3, rda45d0e, r9e782, r7798355, rc391829; 출처로만 적히면 r4daca3d, ra7615a, rb4b7771)을 더한다."
assert u.count(old_b) == 1
u = u.replace(old_b, "새로 드는 기록(rba2ecf, rbeae3a3, rda45d0e, r9e782, r7798355, rc391829, rfc69320; 출처로만 적히면 r4daca3d, ra7615a, rb4b7771)을 더한다.")
io.open(P3, "w", encoding="utf-8", newline="\n").write(u)
print("구조표_v2.md patched")
