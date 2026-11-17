# 장 파일의 진술 머리를 라벨별로 모아 (파일, 행, 절, 머리 전문)을 TSV로 낸다. 자리 찾기용.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
files = [f'장{c}.md' for c in ['1','2','3','4','5A','5B','6','7A','7B','8','9','10']]
out = []
for f in files:
    sec = ''
    for i, ln in enumerate(open(base + f, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5} (\d+(?:\.\d+)*)', ln)
        if m: sec = m.group(1)
        m = re.match(r'\*\*((정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}.*?)\*\*', ln)
        if m:
            out.append((m.group(3), f, i, sec, m.group(1)))
open('C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체25_R10_색인.tsv', 'w', encoding='utf-8', newline='\n').write(
    '\n'.join('\t'.join(map(str, r)) for r in out) + '\n')
print(len(out))
