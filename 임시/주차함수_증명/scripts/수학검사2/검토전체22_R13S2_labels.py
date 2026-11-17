# 장부 166–287행이 인용하는 라벨을 뽑아 머리 목록(종류·절)과 맞대어 본다.
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
H = {o['label']: o for o in heads if not o['proof']}
L = open(W+"장부_v2.md", encoding='utf-8').read().split('\n')
# 장 파일 안의 모든 라벨 정의(식 라벨 포함)를 찾기 위해 원문 전체를 모은다
import glob, os
txt = {}
for p in glob.glob(W+"장v2/*.md"):
    txt[os.path.basename(p)[:-3]] = open(p, encoding='utf-8').read()
a, b = int(sys.argv[1]), int(sys.argv[2])
for ln in range(a, b+1):
    s = L[ln-1]
    for m in re.finditer(r'(\S+)\s+`?\{\{([^}]+)\}\}`?((?:\([가-힣ㄱ-ㅎa-z]+\))*)', s):
        kind, lab, part = m.group(1), m.group(2), m.group(3)
        o = H.get(lab)
        if o:
            flag = '' if o['kind'] in kind else ' <<KIND?'
            print(f"{ln}: {kind} {lab}{part} -> {o['kind']} {o['num']} [{o['file']}:{o['line']} sec {o['sec']}] {o['name']}{flag}")
        else:
            where = [f for f, t in txt.items() if '{{'+lab+'}}' in t]
            print(f"{ln}: {kind} {lab}{part} -> NOT A HEAD; appears in {where}")
