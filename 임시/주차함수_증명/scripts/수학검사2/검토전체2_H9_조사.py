# -*- coding: utf-8 -*-
"""검토전체2 H9: 장9에서 라벨 바로 뒤에 붙은 조사가 조립 번호의 끝 숫자 받침과 맞는지 본다."""
import re, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
num = {}
for ln in open(os.path.join(ROOT, '대조v2', '라벨_번호_대응표_1114.md'), encoding='utf-8'):
    m = re.match(r'\| `\{\{([^}]+)\}\}` \| [^|]* \| [^|]* \| ([0-9.]+) \| ([0-9.]+) \|', ln)
    if m: num[m.group(1)] = m.group(3)
batchim = {'0': True, '1': True, '2': False, '3': True, '4': False, '5': False, '6': True, '7': True, '8': True, '9': False}
need_b = {'을', '이', '은', '과'}; need_nb = {'를', '가', '는', '와', '다', '로'}
src = open(os.path.join(ROOT, '장v2', '장9.md'), encoding='utf-8').read().split('\n')
for i, ln in enumerate(src, 1):
    for m in re.finditer(r'\{\{([^}]+)\}\}([을를이가은는과와다로])', ln):
        lab, p = m.group(1), m.group(2)
        if lab not in num: print(i, lab, p, '번호 없음'); continue
        n = num[lab]; b = batchim[n[-1]]
        ok = (p in need_b and b) or (p in need_nb and not b)
        if p == '이' and ln[m.end():m.end()+1] != '다':
            pass
        print(f'{i}: {{{{{lab}}}}} -> {n} + "{p}" ' + ('OK' if ok else '** 불일치') + '   …' + ln[max(0, m.start()-40):m.end()+6].replace('\n', ' '))
