# -*- coding: utf-8 -*-
"""장 파일의 수식 안에서 6절 예약 바탕 글자의 잔존을 센다(세션 일관성 검토용).
대상: 맨 이탤릭 글자 h·a·b·c·l(글자체 명령 뒤, 첨자·위첨자가 붙은 꼴, 뒤에 글자가 이어지는 꼴은 제외),
      \\delta(\\delta_t·\\delta_{t'}·\\delta_k 같은 나무 크기 첨자 꼴은 제외), 구간 끝점 [a,b].
사용: python _scan_예약글자.py [--all] [장v2/장N.md ...]  (없으면 장v2/장*.md 전부; --all이면 예를 전부 적는다)
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
show_all = "--all" in sys.argv
files = args or sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md")))
MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)
FONT = r"(?<!\\mathfrak )(?<!\\mathcal )(?<!\\mathsf )(?<!\\mathrm )(?<!\\mathbf )(?<!\\mathbb )(?<!\\hat )(?<!\\tilde )(?<!\\bar )(?<!\\check )(?<!\\dot )(?<!\\vec )(?<!\\widehat )(?<!\\widetilde )(?<!\\operatorname )"
BARE = r"(?<![A-Za-z\\{_^])" + FONT + r"%s(?![A-Za-z_^])"
PATS = {
    "h": re.compile(BARE % "h"),
    "a": re.compile(BARE % "a"),
    "b": re.compile(BARE % "b"),
    "c": re.compile(BARE % "c"),
    "l": re.compile(BARE % "l"),
    "delta": re.compile(r"\\delta(?!_t\b|_\{t|_k\b|_\{k|_t'|_\{m|_m\b|_\{N|_N\b)(?![A-Za-z])"),
    "[a,b]": re.compile(r"\[a,\s*b\]"),
}
for p in files:
    text = io.open(p, encoding="utf-8").read()
    counts = {k: 0 for k in PATS}
    examples = {k: [] for k in PATS}
    for ln_no, ln in enumerate(text.split("\n"), 1):
        for m in MATH.finditer(ln):
            seg = m.group(1) or m.group(2)
            for k, pat in PATS.items():
                for mm in pat.finditer(seg):
                    counts[k] += 1
                    if show_all or len(examples[k]) < 4:
                        examples[k].append(f"{ln_no}: {seg[max(0, mm.start()-22): mm.end()+22]}")
    print("==", os.path.basename(p), {k: v for k, v in counts.items() if v})
    for k in PATS:
        for e in examples[k]:
            print(f"   {k}  {e}")
