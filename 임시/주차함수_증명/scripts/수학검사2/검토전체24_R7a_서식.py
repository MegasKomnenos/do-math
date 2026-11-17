# 검토전체24 R7a: 장7B 1-241행의 수식 구분자 균형과 라벨 목록 (자리를 찾는 용도)
import io
import re

L = io.open('장v2/장7B.md', encoding='utf-8').read().split('\n')[:241]
inblock = False
for i, l in enumerate(L, 1):
    if l.strip() == '$$':
        inblock = not inblock
        continue
    if inblock:
        if l.count('{') != l.count('}'):
            print('brace(block)', i, l.count('{'), l.count('}'))
        continue
    s = l.replace('{{', '').replace('}}', '')
    d = len(re.findall(r'(?<!\\)[$]', s))
    if d % 2:
        print('odd dollar', i)
    if s.count('{') != s.count('}'):
        print('brace', i, s.count('{'), s.count('}'))
    if s.count('(') != s.count(')'):
        print('paren', i, s.count('('), s.count(')'))
    if s.count('「') != s.count('」'):
        print('quote', i)
    words = s.split(' ')
    for a, b in zip(words, words[1:]):
        if a == b and len(a) > 1 and not a.startswith('$'):
            print('dup', i, a)
print('blockstate', inblock)
labs = sorted(set(re.findall(r'\{\{([^}]+)\}\}', '\n'.join(L))))
print(len(labs), labs)
eqs = re.findall(r'\\tag\{([^}]+)\}', '\n'.join(L))
print('tags', eqs)
refs = sorted(set(re.findall(r'\((7\.\d+)\)', '\n'.join(L))))
print('refs', refs)
