"""E7 보조 도구(읽기 전용): 장 파일의 수식 안에서 글꼴 명령 없이 쓰인 라틴 대문자(이탤릭 바탕 글자)를 센다.
사용: python -I 이_파일.py <md 파일들>
"""
import re
import sys
from collections import defaultdict

FONT = re.compile(
    r'\\(mathrm|mathcal|mathfrak|mathsf|mathbb|mathbf|operatorname|text|hat|tilde|bar|'
    r'underline|widetilde|overline|mathscr)\s*\{?\s*$'
)
CAP = re.compile(r'(?<![A-Za-z\\])([A-Z])(?![A-Za-z])')
MATH = re.compile(r'\$\$(.+?)\$\$|\$(.+?)\$')


def main(files):
    for f in files:
        lines = open(f, encoding='utf-8').read().split('\n')
        found = defaultdict(list)
        for ln, line in enumerate(lines, 1):
            for m in MATH.finditer(line):
                seg = m.group(1) or m.group(2)
                for mm in CAP.finditer(seg):
                    pre = seg[max(0, mm.start() - 16):mm.start()]
                    if FONT.search(pre):
                        continue
                    found[mm.group(1)].append(ln)
        print('==', f)
        for L in sorted(found):
            v = found[L]
            print(f'  {L}: {len(v)}회, 행 {sorted(set(v))[:15]}')


if __name__ == '__main__':
    main(sys.argv[1:])
