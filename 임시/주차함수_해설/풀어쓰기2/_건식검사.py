# -*- coding: utf-8 -*-
"""풀어쓰기2 패치들의 건식 적용 검사.

패치 파일들을 주어진 순서로 읽어 각 파일의 R 목록을 뽑고(파일을 쓰지 않음),
원고 사본(메모리) 위에 차례로 적용하면서 원래 문면이 정확히 한 번 나타나는지 확인한다.
결과 본문을 --출력 경로에 쓴다(불변식 검사용). 원고 파일 자체는 건드리지 않는다.

사용: python _건식검사.py --출력 <경로> 패치_A.py 패치_B1.py ...
"""
import sys, io, argparse, os

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('--출력', required=True)
ap.add_argument('--원고', default=r'임시/주차함수_해설/원고.md')
ap.add_argument('패치', nargs='+')
a = ap.parse_args()

text = io.open(a.원고, encoding='utf-8').read()
total = 0
bad = 0
for path in a.패치:
    src = io.open(path, encoding='utf-8').read()
    cut = src.index('for i, (old, new) in enumerate(R, 1):')
    head = src[:cut]
    ns = {}
    exec(compile(head, path, 'exec'), ns)
    R = ns['R']
    name = os.path.basename(path)
    for i, (old, new) in enumerate(R, 1):
        c = text.count(old)
        if c != 1:
            bad += 1
            print(f'{name} [{i}] 일치 {c}회: {old[:70]!r}')
            continue
        text = text.replace(old, new)
        total += 1
    print(f'{name}: 항목 {len(R)}건')
io.open(a.출력, 'w', encoding='utf-8', newline='\n').write(text)
print(f'적용 가능 {total}건, 어긋남 {bad}건, 결과 {len(text.splitlines())}행 -> {a.출력}')
sys.exit(1 if bad else 0)
