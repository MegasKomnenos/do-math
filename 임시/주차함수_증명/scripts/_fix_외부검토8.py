# -*- coding: utf-8 -*-
"""외부 피드백 여덟째 묶음 가운데 세션이 직접 고치는 것: 본문·부록 D의 글자를 사전 설계에 맞춤(C̃→pr, 𝔧_∞→𝗃_∞), 사전 행의 Σ_hz 문구,
조판 셋(pt′ 분모, S_- 분모), 보조정리 10.32(ii)의 범위 조건, 부록 생성기의 작업 메모 정리 규칙. 멱등. 사용: python scripts/_fix_외부검토8.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv

# (파일, old, new, 기대 횟수; None이면 1 이상 모두)
EDITS = [
    # ---- 글자: 소인 질량 pr (사전 1.2 329행·7절 1355행이 이 글의 글자로 정한 것)
    ("장v2/장7A.md", r"\tilde C", r"\mathrm{pr}", None),
    ("장v2/부록D_장7A.md", r"\tilde C", r"\mathrm{pr}", None),
    ("장v2/부록D_장7B.md", r"\tilde C", r"\mathrm{pr}", None),
    # ---- 글자: Jensen 봉투 지수의 극한 𝗃_∞ (사전 1.2 255행)
    ("장v2/장8.md", r"\mathfrak j_\infty", r"\mathsf j_\infty", None),
    ("장v2/부록D_장8.md", r"\mathfrak j_\infty", r"\mathsf j_\infty", None),
    # ---- 사전: 위험률 합의 적는 법(1196행의 결정과 맞춤)
    ("장부_v2.md",
     r"위험률 합은 $\Sigma_{\mathrm{hz}}$(7장도 씀 — 7B 집필 회수)",
     r"위험률 합은 $\sum_N\mathrm{hz}_k(N)$으로 적고 8장의 인증 꼴 하계는 $\mathfrak h(k,\nu)$", 1),
    # ---- 조판
    ("장v2/장5A.md", r"\frac1{\mathrm {pt}}'", r"\frac1{\mathrm{pt}'}", 1),
    ("장v2/장5A.md", r"\log\frac{\xi^{k+1}}{\mathrm {pt}}'", r"\log\frac{\xi^{k+1}}{\mathrm{pt}'}", 1),
    ("장v2/부록D_장5A.md", r"\frac{1+3/\mathrm S_-^2}{\mathrm S}_-", r"\frac{1+3/\mathrm S_-^2}{\mathrm S_-}", 1),
    # ---- 보조정리 10.32(ii): 증명이 닿는 범위를 진술에 적음
    ("장v2/장10.md",
     r"(ii) (눈금 고정 단조성) $\xi$를 고정하면 $\mathfrak Q(y,\xi)$는 $y$에 대해 증가하고, $\mathfrak s^{\mathrm{low}}_{\xi(k+1)^{2/3}+1}(k)$는 $k$에 대해 증가한다.",
     r"(ii) (눈금 고정 단조성) $\xi$를 고정하면 $\xi y^{2/3}>3$인 범위에서 $\mathfrak Q(y,\xi)$는 $y$에 대해 증가하고, $\mathfrak s^{\mathrm{low}}_{\xi(k+1)^{2/3}+1}(k)$는 $k$에 대해 증가한다.", 1),
    ("장v2/장10.md",
     r"그러므로 $\xi$를 고정하면 $\mathfrak Q(y,\xi)$의 모든 인자는 $y$에 대해 증가한다($1+\xi y^{-1/3}-1/y$의 감소는 $\xi y^{2/3}>3$에서 나온다).",
     r"그러므로 $\xi$를 고정하면 $\xi y^{2/3}>3$인 범위에서 $\mathfrak Q(y,\xi)$의 모든 인자는 양수이고 $y$에 대해 증가한다. $1+\xi y^{-1/3}-1/y$의 감소는 $\xi y^{2/3}>3$에서 나오고, 두 대괄호가 양수인 것은 $\xi y^{2/3}>2$에서 나온다($\mathfrak c_{\mathrm R}\xi^{3/2}/\sqrt2$와 $\mathfrak c_{\mathrm R}q_0^{3/2}/y=\mathfrak c_{\mathrm R}\xi^{3/2}$는 $y$에 무관하다).", 1),
    # ---- 부록 생성기: 사전 행의 작업 메모(절 번호 지침) 정리
    ("scripts/부록_v2.py",
     '    text = text.replace("(확인)", "")\n    return text\n',
     '    text = text.replace("(확인)", "")\n'
     '    # 사전 작업 메모의 절 번호 지침(1.1·1.2·1.3 묶음 표지)\n'
     '    text = re.sub(r"\\(1\\.3 \\d+\\.\\d+ 묶음\\)", "", text)\n'
     '    text = re.sub(r"1\\.3 (\\d+\\.\\d+) 묶음의 ", r"\\1절 국소 ", text)\n'
     '    text = re.sub(r"국소\\((\\d+\\.\\d+) 묶음\\)", r"\\1절 국소", text)\n'
     '    text = text.replace("1.2 글자로 풀어 적음", "글자 없이 풀어 적음")\n'
     '    text = re.sub(r"1\\.2 설명을 기록대로 고침(\\([^)]*\\))?;\\s*", "", text)\n'
     '    text = text.replace("(1.1 용량)", "(용량)")\n'
     '    return text\n', 1),
]


def main():
    texts = {}
    bad = 0
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel)
        if s is None:
            s = io.open(p, encoding="utf-8").read()
        n = s.count(old)
        if n == 0:
            if new in s:
                print(f"{rel}: 이미 — {old[:40]!r}")
            else:
                print(f"{rel}: 원문 없음 — {old[:60]!r}"); bad += 1
            texts[rel] = s; continue
        if expect is not None and n != expect:
            print(f"{rel}: 횟수 {n}≠{expect} — {old[:50]!r}"); bad += 1; texts[rel] = s; continue
        texts[rel] = s.replace(old, new); print(f"{rel}: {n}곳 — {old[:40]!r}")
    if bad:
        print(f"문제 {bad}건. 쓰지 않음."); sys.exit(1)
    if DRY:
        print("(dry)"); return
    for rel, t in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(t)
    print("기록함:", ", ".join(sorted(texts)))


if __name__ == "__main__":
    main()
