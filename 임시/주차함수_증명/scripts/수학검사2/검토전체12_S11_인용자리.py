# S11: 11.3절 세 표의 입력 라벨이 장9·장10·장7B(7.7절)에서 어느 진술의 진술/증명/뒤 문단에 나오는지 자리를 모은다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HDR = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의|관찰)\s+\{\{(\d+[AB]?:[^}]+)\}\}')
def segment(path):
    out = []  # (lineno, context, line)
    ctx = ('머리', None)
    for ln, line in enumerate(open(path, encoding='utf-8'), 1):
        m = HDR.match(line)
        if line.startswith('### '):
            ctx = ('절', line.strip()[4:40])
        elif m:
            ctx = (m.group(1) + ' 진술', m.group(2))
        elif re.match(r'^\*\*증명', line) or re.match(r'^\*\*\(.*\)의 증명', line) or re.match(r'^\*\*.*증명\.\*\*', line):
            if ctx[1] and '진술' in ctx[0]:
                ctx = ('증명', ctx[1])
        out.append((ln, ctx, line.rstrip('\n')))
        if '∎' in line and ctx[0] == '증명':
            ctx = ('뒤 문단', ctx[1])
    return out
segs = {ch: segment(f'장v2/{ch}.md') for ch in ['장9', '장10', '장7B']}
# 11.3 표의 라벨 모으기
tab = open('장v2/장11.md', encoding='utf-8').read()
s = tab.index('### 11.3'); e = tab.index('### 11.4')
sec = tab[s:e]
labels = sorted(set(re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', sec)))
labels = [l for l in labels if not l.startswith(('9:', '10:')) or True]
inputs = [l for l in labels if not l.split(':')[0] in ('9', '10')]
print('입력 라벨 수(9·10장 밖):', len(inputs))
for lab in inputs:
    print('\n#####', lab)
    for ch, lines in segs.items():
        for ln, ctx, line in lines:
            if '{{' + lab + '}}' in line:
                # 라벨 둘레 70자
                for mm in re.finditer(re.escape('{{' + lab + '}}'), line):
                    a = max(0, mm.start() - 90); b = min(len(line), mm.end() + 60)
                    print(f'  {ch}:{ln} [{ctx[0]} {ctx[1]}] …{line[a:b]}…')
