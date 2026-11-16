# -*- coding: utf-8 -*-
"""부록 D 조각의 산문에서 연구 체계의 운영 낱말(peer·검토자·생산자·재개 세션·2차 대조·집필자·심사)을
11.1의 어휘(기록의 검토·기록의 작성자·기록의 이어진 계산·이 글을 쓰며 한 독립 재계산)로 바꾼다(지침 8절; 11장 집필자 지적).
백틱 안(파일 경로·코드)과 「**자료.**」 줄은 건드리지 않는다. `--dry`로 미리 본다."""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv

RULES = [
    ("의 검토 보조 세션이", "의 검토가"),
    ("기록의 계산은 검토자(peer)의 것이다", "기록의 계산은 기록의 검토가 한 것이다"),
    ("정리 S를 세웠고", "정리 {{7:self-consistent-S}}를 세웠고"),
    ("검토자(peer)", "기록의 검토"),
    ("기록의 peer가", "기록의 검토가"),
    ("같은 기록의 peer가", "같은 기록의 검토가"),
    ("기록의 심사가", "기록의 검토가"),
    ("(검토자, 정확)", "(기록의 검토, 정확)"),
    ("(생산자, 유리수 상계)", "(기록의 작성자, 유리수 상계)"),
    ("생산자 감사 스크립트", "기록 작성자의 감사 스크립트"),
    ("검토자가", "기록의 검토가"),
    ("검토자(", "기록의 검토("),
    ("생산자(", "기록의 작성자("),
    ("생산자는", "기록의 작성자는"),
    ("생산자의", "기록 작성자의"),
    ("생산자:", "기록의 작성자:"),
    ("peer:", "기록의 검토:"),
    ("peer는", "기록의 검토는"),
    ("peer가", "기록의 검토가"),
    ("인증은 재개 세션의 단독 계산이다", "인증은 기록의 이어진 계산 하나뿐이다"),
    ("재개 세션의 계산이고", "기록의 이어진 계산이고"),
    ("재개 세션의", "기록의 이어진 계산의"),
    ("2차 대조가", "이 글을 쓰며 한 독립 재계산이"),
    ("집필자가 같은 식을", "이 글을 쓰며 같은 식을"),
    ("검토 보조 세션이", "기록의 검토가"),
    ("세션 재계산", "이 글의 재계산"),
    ("세션의 재계산은 없다", "이 글의 재계산은 없다"),
    ("세션이 2026-11-13에", "이 글을 쓰며 2026-11-13에"),
    ("세션이 ", "이 글을 쓰며 "),
]


def fix_prose(seg):
    for a, b in RULES:
        seg = seg.replace(a, b)
    return seg


def fix_line(ln):
    if ln.startswith("**자료.**") or ln.startswith("**출처.**"):
        return ln
    parts = re.split(r"(`[^`]*`)", ln)
    return "".join(p if p.startswith("`") else fix_prose(p) for p in parts)


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "부록D_장*.md"))):
        s = io.open(p, encoding="utf-8").read()
        lines = s.split("\n")
        n = 0
        for i, ln in enumerate(lines):
            new = fix_line(ln)
            if new != ln:
                n += 1
                print(f"{os.path.basename(p)}:{i+1}")
                print("  -", ln[:220])
                print("  +", new[:220])
                lines[i] = new
        if n and not DRY:
            io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        total += n
    # 남은 운영 낱말(산문) 보고
    for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "부록D_장*.md"))):
        for i, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n")):
            if ln.startswith("**자료.**") or ln.startswith("**출처.**"):
                continue
            prose = "".join(x for x in re.split(r"(`[^`]*`)", ln) if not x.startswith("`"))
            for w in ("peer", "생산자", "재개 세션", "2차 대조", "검토자", "집필자", "심사"):
                if w in prose:
                    print(f"[남음] {os.path.basename(p)}:{i+1} 「{w}」 … {prose[:120]}")
    print(f"{'(dry) ' if DRY else ''}고친 줄 {total}")


if __name__ == "__main__":
    main()
