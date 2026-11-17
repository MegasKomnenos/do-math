# 장 파일에서 한글 낱말 바로 뒤 괄호에 영어만 든 자리(영어 병기)를 모아 부록 C의 넷째 표와 견준다(자리 찾기).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2/'
names = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
for n in names:
    sec = n; inmath = False
    for i, l in enumerate(open(base+n+'.md', encoding='utf-8').read().split('\n')):
        m = re.match(r'^#{2,4} (\d+(?:\.\d+)*)', l)
        if m: sec = m.group(1)
        if l.strip() == '$$': inmath = not inmath; continue
        if inmath: continue
        # 수식($…$)을 지운 뒤 찾는다
        t = re.sub(r'\$[^$]*\$', '§', l)
        for mm in re.finditer(r'([가-힣」][^()]{0,2})\(([A-Za-z][A-Za-z \-–]{3,60})\)', t):
            k = mm.start()
            print(f'{n}:{i+1} §{sec} …{t[max(0,k-28):mm.end()]}')
