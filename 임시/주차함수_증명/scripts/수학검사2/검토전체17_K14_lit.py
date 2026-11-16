# -*- coding: utf-8 -*-
"""K14: 의존지도 1절의 「문헌」·「부록 D 계산」 열을 장11의 11.4·11.2 표에서 다시 만들어 대조."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
txt = open(os.path.join(ROOT, '장v2', '장11.md'), encoding='utf-8').read()
s112 = txt.split('### 11.2')[1].split('### 11.3')[0]
s114 = txt.split('### 11.4')[1]
dcalc = {}   # label -> list of 'D.{{D:..}}(등급)'
for line in s112.split('\n'):
    m = re.match(r'^\| 부록 D\.(\{\{D:[^}]+\}\}) \| (.*?) \| (.*?) \|', line)
    if m:
        item, stmts, grade = m.groups()
        for l in LAB.findall(stmts):
            dcalc.setdefault('{{%s}}' % l, []).append('D.%s(%s)' % (item, grade))
lit = {}
for line in s114.split('\n'):
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if m and not m.group(1).startswith('---') and m.group(1) != '문헌':
        who = m.group(1).split(',')[0].strip()
        # 저자 이름들(첫 ,로 자르면 한 명만) — 지도는 「Konheim, Weiss(…)」처럼 적으므로 제목 앞 부분을 쓴다
        auth = m.group(1).split('*')[0].strip().rstrip(',').strip()
        for l in LAB.findall(m.group(3)):
            lit.setdefault('{{%s}}' % l, []).append('%s(%s)' % (auth, m.group(2)))
dep = {}
in1 = False
for line in open(os.path.join(ROOT, '의존지도_v2.md'), encoding='utf-8'):
    if line.startswith('## 1.'):
        in1 = True
    elif line.startswith('### 1.1') or line.startswith('## 2'):
        in1 = False
    if in1:
        m = re.match(r'^\| `(\{\{[^`]+\}\})` \| ([^|]*) \| ([^|]*) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
        if m:
            dep[m.group(1)] = dict(lit=m.group(8).strip(), dcalc=m.group(9).strip())
out = []
for lab, d in dep.items():
    want_d = '; '.join(dcalc.get(lab, [])) if lab in dcalc else '없음'
    if d['dcalc'] != want_d:
        out.append(('부록D', lab, '지도=' + d['dcalc'], '11.2=' + want_d))
    want_l = '; '.join(lit.get(lab, [])) if lab in lit else '—'
    if d['lit'] != want_l:
        out.append(('문헌', lab, '지도=' + d['lit'], '11.4=' + want_l))
for lab in set(dcalc) | set(lit):
    if lab not in dep:
        out.append(('11장이 가리키나 지도에 없음', lab))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_lit_out.txt'), 'w', encoding='utf-8') as f:
    for o in out:
        f.write('\t'.join(o) + '\n')
print('diffs', len(out))
