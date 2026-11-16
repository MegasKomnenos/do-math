# -*- coding: utf-8 -*-
"""ZV14의 요청(묶음 F 4번 (c)안)을 ZV9가 받아 보조정리 old-2-45(2.47)에 걸음 수를 고정한 식을 더하는 치환.
한 번만 적용한다(두 문구가 각각 정확히 한 번 있어야 함). LF 유지, 바이트 쓰기. 실행: python -I <이 파일>
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, '장v2', '장2.md')
raw = open(p, 'rb').read()
assert b'\r\n' not in raw
s = raw.decode('utf-8')
pairs = [
    (r'마르코프 사슬이다. 초과 $1\le q<q_0$에 대해' + '\n$$\n'
     r'\Pr^y(\text{사슬이 }q\text{를 지남})=\mathrm{tilt}_{q_0}(q)\,\mathrm{Ren}(q_0-q),\qquad \mathrm{tilt}_{q_0}(q):=\frac{\mathrm{Bor}(y+q)}{\mathrm{Bor}(y+q_0)}' + '\n$$\n이다.',
     r'마르코프 사슬이다. 초과 $1\le q<q_0$와 걸음 수 $i\ge1$에 대해' + '\n$$\n'
     r'\Pr^y(q_i=q)=\mathrm{tilt}_{q_0}(q)\,\mathrm{Bor}^{*i}(q_0-q),\qquad \Pr^y(\text{사슬이 }q\text{를 지남})=\mathrm{tilt}_{q_0}(q)\,\mathrm{Ren}(q_0-q),\qquad \mathrm{tilt}_{q_0}(q):=\frac{\mathrm{Bor}(y+q)}{\mathrm{Bor}(y+q_0)}' + '\n$$\n이다.'),
    (r'곧 $\mathrm{Bor}^{*i}(q_0-q)$이고, $i$에 대해 더하면 보조정리 {{2:old-2-37}}(나)에 따라 $\mathrm{Ren}(q_0-q)$다. ∎',
     r'곧 $\mathrm{Bor}^{*i}(q_0-q)$이다. 이것이 걸음 수 $i$를 고정한 첫 식이고, $i$에 대해 더하면 보조정리 {{2:old-2-37}}(나)에 따라 $\mathrm{Ren}(q_0-q)$다. ∎'),
]
for old, new in pairs:
    c = s.count(old)
    assert c == 1, ('count', c, old[:60])
    s = s.replace(old, new)
open(p, 'wb').write(s.encode('utf-8'))
raw2 = open(p, 'rb').read()
print('ok', len(raw), '->', len(raw2), 'bytes; CRLF', raw2.count(b'\r\n'), 'LF', raw2.count(b'\n'))
