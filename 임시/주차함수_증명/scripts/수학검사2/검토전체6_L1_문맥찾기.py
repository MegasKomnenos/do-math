# -*- coding: utf-8 -*-
"""검토전체6 L1: 다른 장의 진술을 문자열로 찾아 앞뒤 문맥을 출력한다 (자리 찾기 전용). 인자: 파일이름 검색문자열 [앞폭 뒤폭 최대건수]"""
import sys, glob, os
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
def load(name):
    return open(os.path.join(base, name + '.md'), encoding='utf-8').read()
def show(name, needle, before=200, after=700, maxn=5):
    txt = load(name); i = 0; n = 0
    while True:
        j = txt.find(needle, i)
        if j < 0: break
        ln = txt.count('\n', 0, j) + 1
        print(f'--[{name}:{ln}] ' + txt[max(0, j-before):j+after].replace('\n', ' ⏎ '))
        print()
        n += 1; i = j + len(needle)
        if n >= maxn: break
    if n == 0: print(f'--[{name}] 없음: {needle!r}')
if __name__ == '__main__':
    a = sys.argv[1:]
    name, needle = a[0], a[1]
    before = int(a[2]) if len(a) > 2 else 200
    after = int(a[3]) if len(a) > 3 else 700
    maxn = int(a[4]) if len(a) > 4 else 5
    show(name, needle, before, after, maxn)
