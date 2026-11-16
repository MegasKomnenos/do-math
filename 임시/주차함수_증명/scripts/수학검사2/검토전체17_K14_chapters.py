# -*- coding: utf-8 -*-
"""K14: 장부 1.2 전역 기호의 「쓰이는 장」 열을 장 파일에서 고정 문자열로 다시 세어 대조(후보 표시; 판단은 손으로)."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH = {'1':['장1'],'2':['장2'],'3':['장3'],'4':['장4'],'5':['장5A','장5B'],'6':['장6'],'7':['장7A','장7B'],'8':['장8'],'9':['장9'],'10':['장10'],'11':['장11']}
texts = {}
for ch, files in CH.items():
    texts[ch] = '\n'.join(open(os.path.join(ROOT, '장v2', f + '.md'), encoding='utf-8').read() for f in files)
lines = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('### 1.2'))
end = next(i for i, l in enumerate(lines) if l.startswith('### 1.3'))
def variants(tok):
    v = {tok}
    # 중괄호 한 글자 풀기/묶기
    v.add(re.sub(r'\{(\w)\}', r'\1', tok))
    v.add(re.sub(r'([_^])(\w)(?![\w{])', r'\1{\2}', tok))
    v.add(tok.replace('\\,', ''))
    v.add(tok.replace('^\\prime', "'"))
    v.add(tok.replace('^\\prime', '^{\\prime}'))
    v.add(tok.replace('\\tfrac', '\\frac'))
    return [x for x in v if x]
out = []
for l in lines[start:end]:
    if not l.startswith('| $'):
        continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    if len(cells) < 5:
        continue
    toks = []
    for g in re.findall(r'\$([^$]+)\$', cells[0]):
        # 최상위 쉼표로 나눔(중괄호 안의 쉼표는 보존)
        depth = 0; cur = ''
        for ch in g:
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
            if ch == ',' and depth == 0:
                toks.append(cur); cur = ''
            else:
                cur += ch
        toks.append(cur)
    used = cells[4]
    if used == '전 장':
        continue
    declared = set(x.strip() for x in used.split(','))
    # 토큰마다 핵심 문자열: 인수 괄호 앞까지
    keys = []
    for t in toks:
        t = t.strip()
        core = re.split(r'\(', t)[0].strip()
        # 지표 꼴 S_1>S_2 같은 것은 첫 항만
        core = re.split(r'[<>=]', core)[0].strip()
        if len(core) <= 1:
            continue
        keys.extend(variants(core))
    if not keys:
        out.append(('짧은 글자(손으로)', cells[0], used)); continue
    found = set()
    for ch, t in texts.items():
        if any(k in t for k in keys):
            found.add(ch)
    missing = declared - found
    extra = found - declared
    if missing or extra:
        out.append(('차이', cells[0], '장부=' + ','.join(sorted(declared, key=int)), '없음=' + ','.join(sorted(missing, key=int)), '추가=' + ','.join(sorted(extra, key=int)), 'keys=' + ' | '.join(keys[:3])))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_chapters_out.txt'), 'w', encoding='utf-8') as f:
    for o in out:
        f.write('\t'.join(o) + '\n')
print('flagged', len(out))
