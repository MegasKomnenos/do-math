# 1.2 표의 글자·정의 절·쓰이는 장을 한 줄씩 뽑아 본다(자리 찾기용; 판정은 원문 행으로)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L = open('장부_v2.md', encoding='utf-8').read().split('\n')
for i in range(47, 288):
    l = L[i]
    if not l.startswith('| $'): 
        if l.strip(): print(i+1, '##', l[:100])
        continue
    c = l.strip().strip('|').split(' | ')
    print(i+1, len(c), '§', c[0].strip()[:90], '§', c[3][:40] if len(c) > 3 else '', '§', c[4][:50] if len(c) > 4 else '')
