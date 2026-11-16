# -*- coding: utf-8 -*-
"""외부 피드백 넷째 묶음 · 묶음 D(장7) — ZV12의 자리 확인 스크립트(읽기 전용).

묶음 D 여섯 항목이 가리키는 문구가 현행 `장v2/장7A.md`·`장7B.md`에 실제로 있는지, 몇 행에
몇 번 있는지를 고정 문자열(정규식 아님)로 센다. 첫째 단계에서는 사실 확인에, 둘째 단계에서는
고친 뒤 「전」 문구가 0건·「후」 문구가 1건임을 확인하는 데 쓴다. 파일은 바이트로 읽어 줄 끝(CRLF/LF)도 센다.

실행: python -I scripts/수학검사2/검토_외부피드백_1116_ZV12_자리확인.py [--after]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "장v2" / "장7A.md"
B = ROOT / "장v2" / "장7B.md"
D = ROOT / "장v2" / "부록D_장7A.md"

# (항목, 파일, 고정 문자열, 기대 건수[첫째 단계])
CHECKS = [
    # 항목 1 — 7.28(old-6-12)의 증명과 준비 문단 713, 부록 D (1)
    ("1", A, "이 보조정리가 정리 {{7:old-6-12}}의 다섯 범위가 모두 쓰는 인증 부등식을 준다. 인증의 절차는 다음과 같다.", 1),
    ("1", A, "**증명.** 정리 {{7:X-cert}}를 $k$의 다섯 범위", 1),
    ("1", A, "첫 범위에서는 열마다 입력을 만든다.", 1),
    ("1", A, "다섯 범위 각각에서 입력을 만드는 식과 $R_U\\le2-2/(n_{\\mathrm X}+1)$은 부록 D.{{D:xcert-partAB}}의 계산으로 확인된다. ∎", 1),
    ("1", D, "$I_{\\mathfrak c}$는 보조정리 {{7:fourier-lemmas}}(바)(사)로 만든다.", 1),
    ("1", D, "(보조정리 {{7:fourier-lemmas}}(라)(사)의 몫", 1),
    # 항목 2 — 7.67(root-symmetry) 준비 문단 562와 증명 566
    ("2", B, "보조정리 {{2:old-2-26}}의 $g$의 정의에서 $(1+1/x)^{x-1}=e^{g(x)}$이고, 그 (가)에서 $g$는 $x\\ge1$에서 증가한다.", 1),
    ("2", B, "비가 $1$ 이상인 것은 $k+1+q\\ge k+\\nu-1-q$, 곧 $q\\ge\\nu/2-1$일 때이므로", 1),   # 전(둘째 단계 뒤 0)
    ("2", B, "비가 $1$ 이상인 것은 $g$가 증가하므로 $k+1+q\\ge k+\\nu-1-q$, 곧 $q\\ge\\nu/2-1$일 때이므로", 0),  # 후(둘째 단계 뒤 1)
    ("2", B, "$g$가 증가하므로(보조정리 {{2:old-2-26}}(가))", 1),   # 7.60 fold-T 증명의 관행(468행)
    # 항목 3 — 7.71(theorem-W)의 「(7.23)의 첫 대괄호」와 7.70(top-roots)의 같은 말
    ("3", B, "첫 대괄호는 (7.23)의 첫 대괄호와 같다.", 1),
    ("3", B, "더 정확히 (7.23)의 첫 대괄호는 $s_n(k)\\bigl(\\mathfrak G_k(n)-1\\bigr)$ 이상이다.", 1),
    ("3", B, "그 정리의 부등식 연쇄로 (7.23)의 첫 대괄호는", 1),
    ("3", B, "정리 {{7:top-roots}}를 $U_0=300$으로 쓴다.", 1),
    # 항목 4 — 7.72(src-plus) 증명의 증명 재사용 셋
    ("4", B, "정리 {{7:old-6-16}}의 증명에서 보았듯 $k\\,s_n(k)\\,\\mathrm{apex}^{\\mathrm H}_k(n)$은 (7.23)의 첫 대괄호에 $\\mathcal P_n(k)$를 곱한 것이다.", 1),
    ("4", B, "명제 {{7:fold-A}}의 셈으로", 1),
    ("4", B, "정리 {{7:fold-L1}}의 증명은 $\\mathrm{heavy}_n$ 가운데 정확히 이 항들만 남겨 (7.15)의 우변을 얻었으므로", 1),
    ("4", B, "따름정리 {{7:fold-DIP}}의 증명($\\mathrm{up}_n(\\mathfrak l)<\\mathrm{ed}^{(1)}_n$)에 따라", 1),
    # 항목 5 — 7.66(qstar-columns)·7.64(polar-PD)의 (7.18) 인용과 준비 문단의 라벨
    ("5", B, "(7.18)의 오른쪽을 $y=k+1$의 열별 인증값으로 쓰고", 1),
    ("5", B, "(7.18)의 왼쪽에서 두 값", 1),
    ("5", B, "**극과 갱신열의 공급.**", 1),
    ("5", B, "정리 {{7:old-6-12}}의 증명은 인증 조건 $R_U\\le2-2/(n_{\\mathrm X}(y)+1)$을 모든 $y\\ge501$에서 확인하고", 1),
    # 항목 6 — 7.68(old-6-16)·7.70(top-roots) 증명의 2.31 라벨
    ("6", B, "과 정리 {{2:old-2-31}}의 (DM0)에서 나온다.", 1),
    ("6", B, "(정리 {{2:old-2-31}}의 (DM0))다.", 1),
]


def main() -> int:
    after = "--after" in sys.argv[1:]
    bad = 0
    texts = {}
    for p in (A, B, D):
        raw = p.read_bytes()
        crlf = raw.count(b"\r\n")
        lf = raw.count(b"\n") - crlf
        print(f"{p.name}: CRLF {crlf} · LF {lf} · 바이트 {len(raw)}")
        texts[p] = raw.decode("utf-8")
    for item, p, s, expect in CHECKS:
        if after and item == "2" and "비가 $1$ 이상인 것은" in s:
            expect = 1 - expect  # 둘째 단계 뒤에는 전 0·후 1
        lines = [i + 1 for i, ln in enumerate(texts[p].split("\n")) if s in ln]
        n = len(lines)
        mark = "OK" if n == expect else "!!"
        if n != expect:
            bad += 1
        print(f"[{mark}] 항목 {item} {p.name} {n}건(기대 {expect}) 행 {lines} :: {s[:60]}")
    print("불일치", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
