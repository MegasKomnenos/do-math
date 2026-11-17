# -*- coding: utf-8 -*-
r"""R13b 검산 보조: 장 파일에서 장식 붙은 라틴 글자(x_\ast, x^\ast, x^\circ, x^\sharp, x_{\max}, x_0 …)와
정의 꼴 `글자:=`를 모아, 장부 1절(22–358행) 어디에도 글자 그대로 나오지 않는 것을 찍는다.
자리를 찾는 용도일 뿐이고, 찍힌 것은 원문을 열어 확인한 뒤에만 판단한다.
사용: python -I 검토전체25_R13b_decor.py <장 파일 이름(쉼표로 여럿)>
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'C:/math/임시/주차함수_증명/'
L = io.open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')


def norm(s):
    return s.replace('{', '').replace('}', '').replace(' ', '')


led = norm('\n'.join(L[21:358]))
pat = re.compile(r'(?<![A-Za-z\\])([A-Za-z])(_\\ast|\^\\ast|\^\\circ|\^\\sharp|\^\\flat|_\\star|\^\\star|_\{\\max\}|_\{\\min\}|_\\max|_\\min|\^\\dagger)')
defpat = re.compile(r'(?<![A-Za-z\\])((?:\\[A-Za-z]+\s*\{?[A-Za-z]+\}?|[A-Za-z])(?:[_^](?:\{[^{}$]{1,12}\}|[A-Za-z0-9]|\\[A-Za-z]+))*(?:\([^()$]{0,12}\))?)\s*:=')
for ch in sys.argv[1].split(','):
    T = io.open(BASE + '장v2/%s.md' % ch, encoding='utf-8').read().split('\n')
    seen = {}
    for i, l in enumerate(T):
        for m in pat.finditer(l):
            seen.setdefault(m.group(0), []).append(i + 1)
    print('==', ch, '장식 글자')
    for k, v in sorted(seen.items()):
        if norm(k) not in led:
            print('  %-14s %d건 첫 행 %s  장부 1절: 없음' % (k, len(v), v[:4]))
    seen = {}
    for i, l in enumerate(T):
        for m in defpat.finditer(l):
            seen.setdefault(m.group(1), []).append(i + 1)
    print('==', ch, '정의 꼴(:=) 좌변')
    for k, v in sorted(seen.items()):
        if norm(k) not in led:
            print('  %-28s 행 %s  장부 1절: 없음' % (k, v[:4]))
