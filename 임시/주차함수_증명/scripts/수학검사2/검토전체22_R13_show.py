# 라벨의 진술문(머리부터 다음 빈 줄 뒤 '**증명' 또는 다음 머리 전까지)을 잘라 보여 준다.
import re, sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
H = {o['label']: o for o in heads if not o['proof']}
maxc = int(sys.argv[1])
for lab in sys.argv[2:]:
    o = H.get(lab)
    if not o: print('###', lab, 'DEAD'); continue
    L = open(W+"장v2/"+o['file']+".md", encoding='utf-8').read().split('\n')
    i = o['line']-1; out=[]
    while i < len(L):
        if i > o['line']-1 and (L[i].startswith('**증명') or re.match(r'^\*\*\S+ \{\{', L[i]) or L[i].startswith('#')): break
        out.append(L[i]); i+=1
    txt = '\n'.join(x for x in out if x.strip())
    print('###', lab, o['file'], o['line'], o['num'], 'sec', o['sec'])
    print(txt[:maxc]); print()
