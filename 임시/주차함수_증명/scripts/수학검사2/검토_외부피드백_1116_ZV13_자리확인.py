# -*- coding: utf-8 -*-
"""ZV13 — 외부 피드백 넷째 묶음 E(장9) 아홉 항목의 자리·머리·수치 확인.

읽기 전용. 현행 장v2/장9.md·장6.md·장11.md에서 문구로 자리를 찾아 행 번호를 적고,
지적이 가리키는 머리의 덧붙임(결정 60의 X 범위)과 696행의 산술을 다시 센다.
둘째 단계 뒤에는 1절의 바늘 1–4를 고친 뒤 구절로 바꾸었다(둘째 단계 2026-11-16 16:5x).
실행: python -I scripts/수학검사2/검토_외부피드백_1116_ZV13_자리확인.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
J9 = (ROOT / "장v2" / "장9.md").read_text(encoding="utf-8").split("\n")
J6 = (ROOT / "장v2" / "장6.md").read_text(encoding="utf-8").split("\n")
J11 = (ROOT / "장v2" / "장11.md").read_text(encoding="utf-8").split("\n")


def find(lines, needle, start=0):
    hits = [i + 1 for i, s in enumerate(lines) if needle in s and i >= start]
    return hits


def head(lines, label):
    pat = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{" + re.escape(label) + r"\}\}")
    for i, s in enumerate(lines):
        if pat.match(s):
            m = re.search(r"\[([^\]]*)\]\.\*\*", s)
            return i + 1, (m.group(1) if m else "(표지 없음)")
    return None, None


print("# 1. 아홉 항목의 현행 자리(문구로 찾음)")
items = [
    ("1 9.37 증명의 괄호(뒤 상태)", "정리 {{9:old-7-32}}, 명제 {{9:old-7-18}})으로"),
    ("2 9.27 증명 g의 증가(뒤 상태)", "$g$의 증가(보조정리 {{2:old-2-26}}(가))로 $e^{g(k)-g(N)}\\le1$"),
    ("3 9.34 증명 이 하계는 t에 증가(뒤 상태)", "이 하계는 $g$의 증가(보조정리 {{2:old-2-26}}(가))로 $t$에 증가한다"),
    ("4 9.32 증명 (2) 𝗏(6668)(뒤 상태)", "\\mathsf v(k)\\ge\\mathsf v(6668)>0.7654$; 정리 {{6:old-6-19}})"),
    ("추가 9.4 병합 항등식 증명 문단(뒤 상태)", "**증명.** 보조정리 {{9:old-7-3}}을 $\\varkappa=0$에 쓴다."),
    ("5 9.29 머리", "**정리 {{9:old-7-25}}"),
    ("5 9.34 머리", "**정리 {{9:old-7-30}}"),
    ("5 9.36 머리", "**정리 {{9:old-7-32}}"),
    ("6 9.48(가) 증명", "$\\mathfrak F$의 모든 인자가 $k$에 대해 같은 방향"),
    ("7 9.19 증명 2.10절의 두 꼴", "2.10절의 두 꼴에서"),
    ("7′ 9.41 증명 2.10절의 꼴", "**증명.** 2.10절의 꼴"),
    ("8 9.25 증명 (가) 𝒩_ℓ 식", "\\mathcal N_\\ell(t)=\\min(t,\\ell+1)A_{t-1,\\ell}$이다. $t\\ge k+2$"),
    ("8 9.25 증명 (나) 2.10절의 지수 생성함수", "(나) 2.10절의 지수 생성함수"),
    ("9 (9.4) 준비 문단", "이제 왼쪽을 줄인다. 명제 {{2:old-2-41}}의 정수 꼴"),
    ("9 (9.5) 준비 문단", "\\tag{9.5}"),
    ("9 9.39 증명 출발점", "**정리 {{9:old-7-35}}의 증명.** 명제 {{2:old-2-41}}의 정수 꼴에서"),
]
for name, needle in items:
    print(f"- {name}: 장9.md 행 {find(J9, needle)}")

print("\n# 2. 머리의 덧붙임(결정 60: X는 계산 증거·계산 보조·의존 덧붙임을 가진 진술뿐)")
for lines, lab in [
    (J9, "9:old-7-18"), (J9, "9:old-7-33"), (J9, "9:old-7-28"), (J9, "9:old-7-25"),
    (J9, "9:old-7-30"), (J9, "9:old-7-32"), (J9, "9:old-7-23"), (J9, "9:old-7-22"),
    (J6, "6:D-bound"), (J6, "6:increment-bounds"), (J6, "6:old-6-19"),
]:
    ln, tag = head(lines, lab)
    print(f"- {lab} (행 {ln}): [{tag}]")

print("\n# 3. 장9 안에서 g의 증가·Bor 감소를 부르는 자리")
for needle in ["$g$의 증가", "$g$가 엄격히 증가", "$g$가 증가", "이 하계는 $t$에 증가", "$\\mathrm{Bor}$가 감소"]:
    print(f"- 「{needle}」: 행 {find(J9, needle)}")
print(f"- {{{{2:old-2-26}}}} 라벨: 행 {find(J9, '{{2:old-2-26}}')}")
print(f"- {{{{6:old-6-19}}}} 라벨: 행 {find(J9, '{{6:old-6-19}}')}")
print(f"- {{{{6:D-bound}}}} 라벨: 행 {find(J9, '{{6:D-bound}}')}")

print("\n# 4. 696행 산술의 재계산")
k = 6668.0
v = 0.7654
lhs = 1.5 * (1 - 1.2 / k) * v / 1.2366          # k·dϱ^L/dν·k𝗏(k)/k 의 하계 ×k
print(f"- (k+ν)^2 ≤ (1.112k)^2 = {1.112**2:.6f} k^2 ≤ 1.2366 k^2: {1.112**2 <= 1.2366}")
print(f"- k·d𝒴_k/dν ≥ 1.5(1−1.2/k)𝗏(6668)/1.2366 = {lhs:.5f} ≥ 0.928: {lhs >= 0.928}")
print(f"- k·(1/20)/(k−1) = {k/20/(k-1):.6f} ≤ 0.0501: {k/20/(k-1) <= 0.0501}")
print(f"- 합의 하계 0.928−0.0501 = {0.928-0.0501:.4f} > 0")
# dϱ^L/dν 의 식: ϱ^L = (3/2)(1−1.2/k)·ν/(k(k+ν)) → d/dν = (3/2)(1−1.2/k)/(k+ν)^2
nu = 500.0
h = 1e-6
rhoL = lambda n: 1.5 * (1 - 1.2 / k) * n / (k * (k + n))
num = (rhoL(nu + h) - rhoL(nu - h)) / (2 * h)
ana = 1.5 * (1 - 1.2 / k) / (k + nu) ** 2
print(f"- dϱ^L/dν 수치 {num:.6e} vs 식 {ana:.6e}: 상대차 {abs(num-ana)/ana:.2e}")

print("\n# 5. 887행 𝔍_i(k)/k 의 둘째 항 도함수 부호 문턱")
thr = (1.678 / (1.678 * 0.08 / 3))
print(f"- 0.0447k^(−4/3) − 1.678k^(−2) > 0 ⇔ k^(2/3) > {thr:.1f} (본문 37.5)")

print("\n# 6. 11.3절 108·99행의 현행(세션 몫 참고)")
for needle in ["보조정리 {{9:old-7-37}}(2.10절 첫머리", "정리 {{9:theorem-A-plus}}(정리 {{2:old-2-13}}, 보조정리 {{2:old-2-26}}", "보조정리 {{9:old-7-26}}(정리 {{6:old-6-19}})"]:
    print(f"- 「{needle}」: 장11.md 행 {find(J11, needle)}")
sys.exit(0)
