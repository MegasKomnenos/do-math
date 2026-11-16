# -*- coding: utf-8 -*-
"""검토 97 Q (1): 삭제된 라벨·기호·낱말·번호 참조의 잔존 전수 검색."""
import io, os, glob, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
files = sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) + [os.path.join(ROOT, f) for f in ("장부_v2.md", "의존지도_v2.md", "구조표_v2.md", "원고_자료/README.md", "원고.md")]
pats = [
    ("{{10:old-8-5}}", "라벨 old-8-5"),
    ("old-8-5", "라벨 old-8-5(괄호 포함)"),
    ("V-core-identity", "라벨 V-core-identity"),
    (r"\mathfrak L_\nu", "ℒ_ν"),
    (r"\mathfrak L_", "ℒ_(모든 첨자)"),
    (r"\mathfrak L", "ℒ(모두)"),
    (r"Bd}^{\Lambda}", "Bd^Λ (중괄호)"),
    (r"Bd}^\Lambda", "Bd^Λ"),
    (r"\mathcal X_n", "X_n"),
    (r"\mathcal Y_n", "Y_n"),
    (r"\mathcal X_", "X_(첨자 모두)"),
    (r"\mathcal Y_", "Y_(첨자 모두)"),
    (r"\mathsf s_{\mathrm{St}}", "s_St"),
    (r"s_{\mathrm{St}}", "s_St(변형)"),
    ("문턱 예산", "문턱 예산"),
    ("예산 분해", "예산 분해"),
    ("무게 성장", "무게 성장"),
    ("동률의 나머지", "동률의 나머지"),
    ("예산", "예산"),
    ("(iii)", "(iii)"),
    ("(ii)", "(ii)"),
    ("(다)", "(다)"),
    ("V-핵심의 머묾 항등식", "V-핵심의 머묾 항등식"),
    ("머묾 항등식", "머묾 항등식"),
    ("첫 세 단계", "첫 세 단계"),
    ("두 따름정리", "두 따름정리"),
    ("체류 꼴", "체류 꼴"),
    ("문턱 단위의 차", "문턱 단위의 차"),
    ("둘째 식", "둘째 식"),
    ("조건부 하계", "조건부 하계"),
]
for path, s in [(p, io.open(p, encoding="utf-8").read()) for p in files]:
    rel = os.path.relpath(path, ROOT)
    lines = s.split("\n")
    for pat, name in pats:
        hits = [(i + 1, l) for i, l in enumerate(lines) if pat in l]
        if hits:
            print("== %s | %s | %d줄" % (rel, name, len(hits)))
            if len(hits) <= 12 or name in ("예산", "(iii)", "(ii)", "(다)", "ℒ(모두)", "X_(첨자 모두)", "Y_(첨자 모두)"):
                for i, l in hits[:40]:
                    print("   %6d: %s" % (i, l[:260].replace("\n", " ")))
